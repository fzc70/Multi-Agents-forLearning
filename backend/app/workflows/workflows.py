from __future__ import annotations

from typing import Any

from app.agents import EvaluatorAgent, IntentAgent, KGAgent, PlannerAgent, ProfileAgent, ResourceAgent, TutorAgent
from app.core.time import now_iso
from app.repositories.repositories import (
    AssessmentRepository,
    ConversationRepository,
    KnowledgeGraphRepository,
    LearningPathRepository,
    MemoryRepository,
    ProfileRepository,
    ResourceRepository,
    TaskRepository,
)
from app.tools.context_builder import ContextBuilder
from app.tools.resource_quality import ResourceQualityGate


class ChatProfileWorkflow:
    def __init__(self) -> None:
        self.intent = IntentAgent()
        self.profile_agent = ProfileAgent()
        self.tutor = TutorAgent()
        self.context_builder = ContextBuilder()
        self.tasks = TaskRepository()
        self.profile = ProfileRepository()
        self.conversation = ConversationRepository()
        self.memory = MemoryRepository()

    def run(self, task: dict[str, Any], message: str, use_rag: bool = True) -> dict[str, Any]:
        task_id = task["id"]
        self.conversation.add_message(task_id, "user", message)
        intent = self.intent.run({"message": message, "task_title": task["title"]}, task_id)
        context = self.context_builder.build_for_task(task, message, top_k=6) if use_rag and intent.get("need_retrieval") else {}
        contexts = context.get("retrieved_contexts", [])
        reply = self.tutor.run(
            {
                "message": message,
                "task_title": task["title"],
                "next_action": task["next_action"],
                "provided_context": context,
                "retrieved_contexts": contexts,
            },
            task_id,
        )
        profile_updates = self.profile_agent.run({"message": message, "task_title": task["title"]}, task_id)
        for update in profile_updates.get("updates", []):
            self.profile.update_dimension(
                task_id,
                str(update.get("dimension_id", "style")),
                str(update.get("value", "")),
                str(update.get("evidence", f"来自对话：{message[:60]}")),
            )
        self.memory.add(task_id, "conversation", message[:300], f"来自对话：{message[:60]}", 55)
        message_id = self.conversation.add_message(task_id, "assistant", str(reply["reply"]))
        self.tasks.touch(task_id)
        return {
            "reply": {"id": message_id, "role": "assistant", "content": str(reply["reply"])},
            "grounded": bool(reply.get("grounded")),
            "source_refs": reply.get("source_refs", []),
        }

    def stream_events(self, task: dict[str, Any], message: str, use_rag: bool = True):
        task_id = task["id"]
        self.conversation.add_message(task_id, "user", message)
        intent = self.intent.run({"message": message, "task_title": task["title"]}, task_id)
        context = self.context_builder.build_for_task(task, message, top_k=6) if use_rag and intent.get("need_retrieval") else {}
        contexts = context.get("retrieved_contexts", [])
        payload = {
            "message": message,
            "task_title": task["title"],
            "next_action": task["next_action"],
            "provided_context": context,
            "retrieved_contexts": contexts,
        }
        chunks: list[str] = []
        for chunk in self.tutor.stream_reply(payload, task_id):
            chunks.append(chunk)
            yield {"type": "delta", "content": chunk}

        reply_text = "".join(chunks).strip()
        if not reply_text:
            fallback = self.tutor.run(payload, task_id)
            reply_text = str(fallback["reply"])
            yield {"type": "delta", "content": reply_text}

        profile_updates = self.profile_agent.run({"message": message, "task_title": task["title"]}, task_id)
        for update in profile_updates.get("updates", []):
            self.profile.update_dimension(
                task_id,
                str(update.get("dimension_id", "style")),
                str(update.get("value", "")),
                str(update.get("evidence", f"来自对话：{message[:60]}")),
            )
        self.memory.add(task_id, "conversation", message[:300], f"来自对话：{message[:60]}", 55)
        message_id = self.conversation.add_message(task_id, "assistant", reply_text)
        self.tasks.touch(task_id)
        source_refs = [item.get("source_ref") for item in contexts if item.get("source_ref")]
        yield {
            "type": "done",
            "reply": {"id": message_id, "role": "assistant", "content": reply_text},
            "grounded": bool(source_refs),
            "sourceRefs": source_refs,
        }


class ResourceGenerationWorkflow:
    def __init__(self) -> None:
        self.agent = ResourceAgent()
        self.resources = ResourceRepository()
        self.context_builder = ContextBuilder()
        self.quality = ResourceQualityGate()
        self.tasks = TaskRepository()

    def run(self, task: dict[str, Any], types: list[str] | None, mode: str) -> list[dict[str, Any]]:
        task_id = task["id"]
        if mode == "smart" or not types:
            weak = task.get("assessment", {}).get("weak_points", [])
            types = ["练习题"] if weak else ["讲解文档"]
        context = self.context_builder.build_for_task(task, f"{task['title']} {task['next_action']}", top_k=4)
        contexts = context.get("retrieved_contexts", [])
        output = self.agent.run(
            {
                "task_title": task["title"],
                "next_action": task["next_action"],
                "types": types,
                "provided_context": context,
                "retrieved_contexts": contexts,
                "recent_exercise_memory": [
                    item for item in context.get("memory", []) if item.get("type") in {"exercise", "resource_mastery"}
                ],
            },
            task_id,
        )
        created: list[dict[str, Any]] = []
        source_refs = [item["source_ref"] for item in contexts if item.get("source_ref")]
        for resource in output.get("resources", []):
            resource = self.quality.normalize(resource, task["title"], task["next_action"])
            resource_id = self.resources.create(
                task_id=task_id,
                type_=resource["type"],
                title=resource["title"],
                description=resource["description"],
                content=resource["content"],
                detail=resource["detail"],
                recommendation_reason=resource.get("recommendation_reason", ""),
                source_refs=source_refs,
            )
            created.append({"id": resource_id, **resource, "source_refs": source_refs})
        self.tasks.touch(task_id)
        return created


class LearningPathWorkflow:
    def __init__(self) -> None:
        self.agent = PlannerAgent()
        self.path = LearningPathRepository()
        self.tasks = TaskRepository()

    def run(self, task: dict[str, Any], reason: str | None = None) -> dict[str, Any]:
        task_id = task["id"]
        output = self.agent.run(
            {
                "task_title": task["title"],
                "weak_points": task.get("assessment", {}).get("weak_points", []),
                "reason": reason,
            },
            task_id,
        )
        self.path.replace(task_id, output["steps"])
        next_action = output["steps"][0]["title"] if output.get("steps") else task["next_action"]
        self.tasks.touch(task_id, next_action=next_action, reason=output.get("note", "学习路径已调整。"))
        return output

    def complete_step(self, task_id: str, step_id: str) -> None:
        self.path.mark_step_done(task_id, step_id)
        self.tasks.touch(task_id, reason="学生确认已完成当前学习阶段。")


class AssessmentWorkflow:
    def __init__(self) -> None:
        self.agent = EvaluatorAgent()
        self.assessment = AssessmentRepository()
        self.profile = ProfileRepository()
        self.tasks = TaskRepository()

    def run(self, task: dict[str, Any], answers: list[dict[str, Any]]) -> dict[str, Any]:
        task_id = task["id"]
        output = self.agent.run({"task_title": task["title"], "answers": answers}, task_id)
        self.assessment.update(
            task_id,
            int(output["score"]),
            str(output["mastery"]),
            list(output["weak_points"]),
            list(output["mistake_types"]),
            str(output["effort"]),
            str(output["next_suggestion"]),
        )
        if output.get("weak_points"):
            self.profile.update_dimension(task_id, "weakness", "；".join(output["weak_points"]), "来自学习测评")
        self.profile.update_dimension(task_id, "exercise", f"测评分数 {output['score']}", "来自学习测评")
        self.tasks.touch(task_id, next_action=str(output["next_suggestion"]), reason="根据最近测评结果更新。")
        return output


class KnowledgeGraphWorkflow:
    def __init__(self) -> None:
        self.agent = KGAgent()
        self.kg = KnowledgeGraphRepository()
        self.context_builder = ContextBuilder()
        self.conversation = ConversationRepository()

    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        task_id = task["id"]
        context = self.context_builder.build_for_task(task, task["title"], top_k=10)
        contexts = context.get("retrieved_contexts", [])
        messages = self.conversation.list_messages(task_id, limit=20)
        text = "\n".join([item["content"] for item in contexts] + [item["content"] for item in messages])
        if not text.strip():
            raise ValueError("请先上传学习资料或开始对话")
        output = self.agent.run({"task_title": task["title"], "text": text[:12000]}, task_id)
        stats = {
            "material_chunks": len(contexts),
            "conversation_messages": len(messages),
            "node_count": len(output.get("nodes", [])),
            "edge_count": len(output.get("edges", [])),
        }
        created_at = now_iso()
        graph_id = self.kg.create(task_id, f"{task['title']} 知识图谱", output.get("nodes", []), output.get("edges", []), stats)
        return {
            "id": graph_id,
            "task_id": task_id,
            "title": f"{task['title']} 知识图谱",
            **output,
            "source_stats": stats,
            "created_at": created_at,
        }
