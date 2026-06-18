from __future__ import annotations

from typing import Any

from app.agents.intent_agent import IntentAgent
from app.agents.profile_agent import ProfileAgent
from app.agents.tutor_agent import TutorAgent
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.task_repository import TaskRepository
from app.tools.context_builder import ContextBuilder


class ChatProfileWorkflow:
    """对话工作流：识别意图、检索上下文、生成回答并更新画像/记忆。"""

    def __init__(self) -> None:
        """初始化 ChatProfileWorkflow 所需的依赖。"""
        self.intent = IntentAgent()
        self.profile_agent = ProfileAgent()
        self.tutor = TutorAgent()
        self.context_builder = ContextBuilder()
        self.tasks = TaskRepository()
        self.profile = ProfileRepository()
        self.conversation = ConversationRepository()
        self.memory = MemoryRepository()

    def run(
        self, task: dict[str, Any], message: str, use_rag: bool = True
    ) -> dict[str, Any]:
        """编排意图识别、画像更新、检索和学习对话流程。"""
        task_id = task["id"]
        self.conversation.add_message(task_id, "user", message)
        intent = self.intent.run(
            {"message": message, "task_title": task["title"]}, task_id
        )
        context = (
            self.context_builder.build_for_task(task, message, top_k=6)
            if use_rag and intent.get("need_retrieval")
            else {}
        )
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
        profile_updates = self.profile_agent.run(
            {"message": message, "task_title": task["title"]}, task_id
        )
        for update in profile_updates.get("updates", []):
            self.profile.update_dimension(
                task_id,
                str(update.get("dimension_id", "style")),
                str(update.get("value", "")),
                str(update.get("evidence", f"来自对话：{message[:60]}")),
            )
        self.memory.add(
            task_id, "conversation", message[:300], f"来自对话：{message[:60]}", 55
        )
        message_id = self.conversation.add_message(
            task_id, "assistant", str(reply["reply"])
        )
        self.tasks.touch(task_id)
        return {
            "reply": {
                "id": message_id,
                "role": "assistant",
                "content": str(reply["reply"]),
            },
            "grounded": bool(reply.get("grounded")),
            "source_refs": reply.get("source_refs", []),
        }

    def stream_events(self, task: dict[str, Any], message: str, use_rag: bool = True):
        """以事件流方式执行当前工作流。"""
        task_id = task["id"]
        self.conversation.add_message(task_id, "user", message)
        intent = self.intent.run(
            {"message": message, "task_title": task["title"]}, task_id
        )
        context = (
            self.context_builder.build_for_task(task, message, top_k=6)
            if use_rag and intent.get("need_retrieval")
            else {}
        )
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

        profile_updates = self.profile_agent.run(
            {"message": message, "task_title": task["title"]}, task_id
        )
        for update in profile_updates.get("updates", []):
            self.profile.update_dimension(
                task_id,
                str(update.get("dimension_id", "style")),
                str(update.get("value", "")),
                str(update.get("evidence", f"来自对话：{message[:60]}")),
            )
        self.memory.add(
            task_id, "conversation", message[:300], f"来自对话：{message[:60]}", 55
        )
        message_id = self.conversation.add_message(task_id, "assistant", reply_text)
        self.tasks.touch(task_id)
        source_refs = [
            item.get("source_ref") for item in contexts if item.get("source_ref")
        ]
        yield {
            "type": "done",
            "reply": {"id": message_id, "role": "assistant", "content": reply_text},
            "grounded": bool(source_refs),
            "sourceRefs": source_refs,
        }
