from __future__ import annotations

import os
from typing import Any

from fastapi import UploadFile

from app.core.errors import bad_request, not_found
from app.core.ids import new_id
from app.agents.grading_agent import GradingAgent
from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.text_cleaner import clean_text
from app.repositories.repositories import (
    AgentRunRepository,
    AssessmentRepository,
    ExerciseAttemptRepository,
    KnowledgeGraphRepository,
    LearningPathRepository,
    MaterialRepository,
    MemoryRepository,
    ProfileRepository,
    ResourceRepository,
    ResourceMasteryRepository,
    TaskRepository,
    loads,
)
from app.services.task_assembler import TaskAssembler
from app.storage.file_store import FileStore
from app.workflows.workflows import (
    AssessmentWorkflow,
    ChatProfileWorkflow,
    KnowledgeGraphWorkflow,
    LearningPathWorkflow,
    ResourceGenerationWorkflow,
)
from app.tools.resource_quality import ResourceQualityGate


class TaskService:
    def __init__(self) -> None:
        self.repo = TaskRepository()
        self.assembler = TaskAssembler()

    def list_tasks(self) -> list[dict[str, Any]]:
        return self.assembler.list()

    def get_task(self, task_id: str) -> dict[str, Any]:
        task = self.assembler.assemble(task_id)
        if not task:
            raise not_found("学习任务不存在")
        return task

    def create_task(self, title: str, foundation: str | None, expected_outcome: str | None) -> dict[str, Any]:
        if not title.strip():
            raise bad_request("任务标题不能为空")
        task_id = self.repo.create(title.strip(), foundation, expected_outcome)
        return self.get_task(task_id)

    def delete_task(self, task_id: str) -> dict[str, Any]:
        self.get_task(task_id)
        self.repo.delete(task_id)
        return {"ok": True}

class MaterialService:
    max_pdf_size = 30 * 1024 * 1024

    def __init__(self) -> None:
        self.tasks = TaskService()
        self.repo = MaterialRepository()
        self.files = FileStore()

    def list_materials(self, task_id: str) -> list[dict[str, Any]]:
        self.tasks.get_task(task_id)
        return self.tasks.get_task(task_id)["materials"]

    def upload_pdf(self, task_id: str, file: UploadFile) -> dict[str, Any]:
        self.tasks.get_task(task_id)
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise bad_request("只支持上传 PDF 文件")
        material_id = new_id("mat")
        path = self.files.save_upload(task_id, material_id, file.filename, file.file)
        size = os.path.getsize(path)
        if size > self.max_pdf_size:
            path.unlink(missing_ok=True)
            raise bad_request("单个 PDF 不能超过 30MB")
        pages = parse_pdf(path)
        text = clean_text("\n\n".join(str(page["text"]) for page in pages))
        if not text:
            path.unlink(missing_ok=True)
            raise bad_request("PDF 未解析到有效文本")
        text_path = self.files.save_text(task_id, material_id, text)
        self.repo.insert_with_id(material_id, task_id, file.filename, size, len(text), str(path), str(text_path))
        chunks = chunk_pages(pages)
        self.repo.add_chunks(task_id, material_id, chunks)
        return self.tasks.get_task(task_id)

    def delete_material(self, task_id: str, material_id: str) -> dict[str, Any]:
        material = self.repo.get(material_id, task_id)
        if not material:
            raise not_found("资料不存在")
        for key in ("file_path", "text_path"):
            if material.get(key):
                try:
                    os.remove(material[key])
                except OSError:
                    pass
        self.repo.delete(material_id, task_id)
        return self.tasks.get_task(task_id)


class ChatService:
    def __init__(self) -> None:
        self.tasks = TaskService()
        self.workflow = ChatProfileWorkflow()

    def chat(self, task_id: str, message: str, use_rag: bool = True) -> dict[str, Any]:
        if not message.strip():
            raise bad_request("消息不能为空")
        task = self.tasks.get_task(task_id)
        result = self.workflow.run(task, message.strip(), use_rag)
        return {"task": self.tasks.get_task(task_id), **result}

    def chat_stream_events(self, task_id: str, message: str, use_rag: bool = True):
        if not message.strip():
            yield {"type": "error", "message": "消息不能为空"}
            return
        yield {"type": "status", "message": "thinking"}
        task = self.tasks.get_task(task_id)
        for event in self.workflow.stream_events(task, message.strip(), use_rag):
            if event.get("type") == "done":
                event["task"] = self.tasks.get_task(task_id)
            yield event


class ResourceService:
    allowed_types = {"讲解文档", "练习题", "思维导图", "拓展阅读", "代码案例", "知识图谱"}

    def __init__(self) -> None:
        self.tasks = TaskService()
        self.workflow = ResourceGenerationWorkflow()
        self.resources = ResourceRepository()
        self.path = LearningPathRepository()
        self.attempts = ExerciseAttemptRepository()
        self.mastery = ResourceMasteryRepository()

    def generate(self, task_id: str, types: list[str] | None, mode: str) -> dict[str, Any]:
        task = self.tasks.get_task(task_id)
        if types:
            types = [item for item in types if item in self.allowed_types]
        if mode == "selected" and not types:
            raise bad_request("请选择有效的资源类型")
        resources = self.workflow.run(task, types, mode)
        return {"task": self.tasks.get_task(task_id), "resources": resources}

    def attach_to_path(self, task_id: str, resource_id: str) -> dict[str, Any]:
        self.tasks.get_task(task_id)
        resource = self.resources.get(resource_id, task_id)
        if not resource:
            raise not_found("学习资源不存在")
        self.path.attach_resource_to_current_step(task_id, resource["title"])
        TaskRepository().touch(task_id, reason=f"已将「{resource['title']}」加入当前学习阶段。")
        return self.tasks.get_task(task_id)

    def get_resource(self, task_id: str, resource_id: str) -> dict[str, Any]:
        self.tasks.get_task(task_id)
        resource = self.resources.get(resource_id, task_id)
        if not resource:
            raise not_found("学习资源不存在")
        task = self.tasks.get_task(task_id)
        normalized = ResourceQualityGate().normalize(
            {
                "type": resource["type"],
                "title": resource["title"],
                "description": resource["description"],
                "content": resource["content"],
                "detail": loads(resource.get("detail_json"), {}),
                "recommendation_reason": resource["recommendation_reason"],
            },
            task["title"],
            task["next_action"],
        )
        self.resources.update_normalized(
            resource["id"],
            task_id,
            normalized["content"],
            normalized["detail"],
            normalized["description"],
            normalized.get("recommendation_reason", ""),
        )
        return {"id": resource["id"], **normalized, "source_refs": loads(resource["source_refs"], []), "created_at": resource.get("created_at")}

    def submit_exercise(self, task_id: str, resource_id: str, answers: dict[str, Any]) -> dict[str, Any]:
        resource = self.get_resource(task_id, resource_id)
        if resource["type"] != "练习题":
            raise bad_request("该资源不是练习题")
        questions = resource.get("detail", {}).get("questions", [])
        total = max(len(questions), 1)
        results: list[dict[str, Any]] = []
        short_items: list[dict[str, Any]] = []
        choice_score = 0
        per_question_score = round(100 / total)
        for question in questions:
            qid = str(question.get("id"))
            expected = str(question.get("answer", "")).strip()
            given = str(answers.get(qid, "")).strip()
            q_type = str(question.get("type", "short_answer"))
            if q_type == "single_choice":
                correct = given.upper() == expected.upper()
                earned = per_question_score if correct else 0
                choice_score += earned
                results.append(
                    {
                        "id": qid,
                        "correct": correct,
                        "score": earned,
                        "max_score": per_question_score,
                        "answer": expected,
                        "given": given,
                        "analysis": question.get("analysis", "请对照答案复盘关键步骤。"),
                        "weak_point": "" if correct else "概念判断",
                        "mistake_type": "" if correct else "选择判断错误",
                    }
                )
                continue
            short_items.append(
                {
                    "id": qid,
                    "stem": question.get("stem", ""),
                    "answer": expected,
                    "student_answer": given,
                    "max_score": per_question_score,
                    "analysis_reference": question.get("analysis", ""),
                }
            )
        if short_items:
            graded = GradingAgent().run(
                {
                    "task_title": resource["title"],
                    "resource_title": resource["title"],
                    "items": short_items,
                    "grading_rules": [
                        "必须按满分给出 0 到 max_score 的整数分",
                        "看是否覆盖关键概念、推理步骤、依据表达",
                        "空答案必须 0 分",
                        "允许等价表达，不要求逐字一致",
                    ],
                },
                task_id,
            )
            by_id = {str(item.get("id")): item for item in graded.get("items", [])}
            for item in short_items:
                graded_item = by_id.get(str(item["id"]), {})
                earned = max(0, min(int(item["max_score"]), int(graded_item.get("score", 0))))
                results.append(
                    {
                        "id": item["id"],
                        "correct": bool(graded_item.get("correct", earned >= int(item["max_score"]) * 0.75)),
                        "score": earned,
                        "max_score": item["max_score"],
                        "answer": item["answer"],
                        "given": item["student_answer"],
                        "analysis": str(graded_item.get("analysis") or item.get("analysis_reference") or "请对照参考答案补充关键步骤。"),
                        "weak_point": str(graded_item.get("weak_point") or ("步骤表达" if earned < int(item["max_score"]) * 0.75 else "")),
                        "mistake_type": str(graded_item.get("mistake_type") or ("答案不完整" if earned < int(item["max_score"]) * 0.75 else "")),
                    }
                )
        results.sort(key=lambda item: str(item["id"]))
        correct_count = len([item for item in results if item["correct"]])
        score = max(0, min(100, round(sum(int(item.get("score", 0)) for item in results))))
        def meaningful(value: str | None) -> str:
            text = str(value or "").strip()
            empty_words = {"无", "暂无", "没有", "无明显", "暂无明显", "none", "null", "n/a"}
            if not text or text.lower() in empty_words:
                return ""
            if text.startswith("无明显") or text.startswith("暂无明显"):
                return ""
            return text

        weak_points = [text for item in results if (text := meaningful(item.get("weak_point")))]
        mistake_types = [text for item in results if (text := meaningful(item.get("mistake_type")))]
        if not weak_points:
            weak_points = ["暂未发现明显薄弱点"]
        if not mistake_types:
            mistake_types = ["暂无明显易错类型"]
        detail = {"items": results, "answers": answers, "resource_type": resource["type"]}
        self.attempts.add(task_id, resource_id, resource["title"], score, detail)
        MemoryRepository().add(
            task_id,
            "exercise",
            f"完成练习「{resource['title']}」，得分 {score}，薄弱点：{'、'.join(weak_points[:3])}",
            f"来自资源练习：{resource['title']}",
            82,
        )
        ProfileRepository().update_dimension(task_id, "weakness", "；".join(weak_points[:4]), f"来自练习「{resource['title']}」")
        ProfileRepository().update_dimension(task_id, "exercise", f"最近练习 {score} 分", f"来自练习「{resource['title']}」")
        assessment_score = self._dynamic_score(task_id)
        next_suggestion = "先复盘错题解析，再生成一组同类型练习。" if score < 80 else "可以确认本资源掌握度，或进入下一阶段。"
        AssessmentRepository().update(
            task_id,
            assessment_score,
            f"综合最近练习、资源掌握和路径进度，当前掌握度为 {assessment_score}。",
            list(dict.fromkeys(weak_points))[:5],
            list(dict.fromkeys(mistake_types))[:5],
            f"最近完成资源「{resource['title']}」练习，得分 {score}",
            next_suggestion,
        )
        TaskRepository().touch(task_id, next_action=next_suggestion, reason="根据最近练习结果和历史表现更新。")
        return {
            "task": self.tasks.get_task(task_id),
            "result": {
                "score": score,
                "assessment_score": assessment_score,
                "correct_count": correct_count,
                "total": total,
                "items": results,
                "summary": next_suggestion,
            },
        }

    def mark_mastery(self, task_id: str, resource_id: str, mastery: int, note: str | None = None) -> dict[str, Any]:
        resource = self.get_resource(task_id, resource_id)
        self.mastery.upsert(task_id, resource_id, resource["title"], mastery, note or "")
        MemoryRepository().add(
            task_id,
            "resource_mastery",
            f"学生确认资源「{resource['title']}」掌握度 {mastery}%",
            f"来自资源掌握反馈：{resource['title']}",
            72,
        )
        assessment_score = self._dynamic_score(task_id)
        AssessmentRepository().update(
            task_id,
            assessment_score,
            f"综合最近练习和资源掌握反馈，当前掌握度为 {assessment_score}。",
            ["资源理解不稳定"] if mastery < 80 else ["保持稳定输出"],
            ["掌握度自评偏低"] if mastery < 80 else ["暂无明显易错类型"],
            f"资源「{resource['title']}」自评掌握度 {mastery}%",
            "低掌握资源建议回看讲解并做针对练习。" if mastery < 80 else "可以推进学习路径的下一阶段。",
        )
        ProfileRepository().update_dimension(task_id, "preference", f"最近资源掌握反馈 {mastery}%", f"来自资源「{resource['title']}」")
        TaskRepository().touch(task_id, reason="根据资源掌握反馈更新评估。")
        return self.tasks.get_task(task_id)

    def _dynamic_score(self, task_id: str) -> int:
        attempts = self.attempts.list_recent(task_id, limit=10)
        mastery_items = self.mastery.list_recent(task_id, limit=10)
        exercise_score = 0
        if attempts:
            weights = [1 / (index + 1) for index, _ in enumerate(attempts)]
            exercise_score = round(sum(int(item["score"]) * weights[index] for index, item in enumerate(attempts)) / sum(weights))
        mastery_score = round(sum(int(item["mastery"]) for item in mastery_items) / len(mastery_items)) if mastery_items else exercise_score
        task = self.tasks.get_task(task_id)
        path = task.get("path", [])
        path_score = round(len([step for step in path if step["status"] == "done"]) / max(len(path), 1) * 100)
        if attempts:
            return round(exercise_score * 0.7 + mastery_score * 0.2 + path_score * 0.1)
        if mastery_items:
            return round(mastery_score * 0.75 + path_score * 0.25)
        return path_score


class LearningPathService:
    def __init__(self) -> None:
        self.tasks = TaskService()
        self.workflow = LearningPathWorkflow()

    def adjust(self, task_id: str, reason: str | None = None) -> dict[str, Any]:
        task = self.tasks.get_task(task_id)
        self.workflow.run(task, reason)
        return self.tasks.get_task(task_id)

    def complete_step(self, task_id: str, step_id: str) -> dict[str, Any]:
        self.tasks.get_task(task_id)
        self.workflow.complete_step(task_id, step_id)
        return self.tasks.get_task(task_id)


class AssessmentService:
    def __init__(self) -> None:
        self.tasks = TaskService()
        self.workflow = AssessmentWorkflow()

    def assess(self, task_id: str, answers: list[dict[str, Any]]) -> dict[str, Any]:
        task = self.tasks.get_task(task_id)
        self.workflow.run(task, answers)
        return self.tasks.get_task(task_id)


class KnowledgeGraphService:
    def __init__(self) -> None:
        self.tasks = TaskService()
        self.workflow = KnowledgeGraphWorkflow()
        self.repo = KnowledgeGraphRepository()

    def build(self, task_id: str) -> dict[str, Any]:
        task = self.tasks.get_task(task_id)
        try:
            return self.workflow.run(task)
        except ValueError as exc:
            raise bad_request(str(exc)) from exc

    def latest(self, task_id: str) -> dict[str, Any] | None:
        self.tasks.get_task(task_id)
        row = self.repo.latest(task_id)
        if not row:
            return None
        return {
            "id": row["id"],
            "task_id": row["task_id"],
            "title": row["title"],
            "nodes": loads(row["nodes"], []),
            "edges": loads(row["edges"], []),
            "source_stats": loads(row["source_stats"], {}),
            "created_at": row["created_at"],
        }


class AgentRunService:
    def __init__(self) -> None:
        self.repo = AgentRunRepository()

    def list(self, task_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.repo.list(task_id, limit)
        return [
            {
                **row,
                "input_json": loads(row["input_json"], {}),
                "output_json": loads(row["output_json"], None),
            }
            for row in rows
        ]
