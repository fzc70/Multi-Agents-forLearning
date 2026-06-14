from __future__ import annotations

import os
from typing import Any

from fastapi import UploadFile

from app.core.errors import bad_request, not_found
from app.core.ids import new_id
from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.text_cleaner import clean_text
from app.repositories.repositories import (
    AgentRunRepository,
    AssessmentRepository,
    KnowledgeGraphRepository,
    LearningPathRepository,
    MaterialRepository,
    ResourceRepository,
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
        return {"id": resource["id"], **normalized, "source_refs": loads(resource["source_refs"], [])}

    def submit_exercise(self, task_id: str, resource_id: str, answers: dict[str, Any]) -> dict[str, Any]:
        resource = self.get_resource(task_id, resource_id)
        if resource["type"] != "练习题":
            raise bad_request("该资源不是练习题")
        questions = resource.get("detail", {}).get("questions", [])
        total = max(len(questions), 1)
        results: list[dict[str, Any]] = []
        correct_count = 0
        for question in questions:
            qid = str(question.get("id"))
            expected = str(question.get("answer", "")).strip()
            given = str(answers.get(qid, "")).strip()
            q_type = str(question.get("type", "short_answer"))
            if q_type == "single_choice":
                correct = given.upper() == expected.upper()
            else:
                correct = bool(given) and (expected in given or given in expected or len(given) >= 8)
            if correct:
                correct_count += 1
            results.append(
                {
                    "id": qid,
                    "correct": correct,
                    "answer": expected,
                    "given": given,
                    "analysis": question.get("analysis", "请对照答案复盘关键步骤。"),
                }
            )
        score = round(correct_count / total * 100)
        weak_points = ["题目理解", "知识迁移"] if score < 80 else ["保持稳定输出"]
        next_suggestion = "先复盘错题解析，再生成一组同类型练习。" if score < 80 else "可以进入下一阶段或做一次综合练习。"
        AssessmentRepository().update(
            task_id,
            score,
            f"本次练习得分 {score}，答对 {correct_count}/{total} 题。",
            weak_points,
            ["答案不完整" if score < 80 else "暂无明显易错类型"],
            f"完成资源「{resource['title']}」练习",
            next_suggestion,
        )
        TaskRepository().touch(task_id, next_action=next_suggestion, reason="根据资源练习结果更新。")
        return {
            "task": self.tasks.get_task(task_id),
            "result": {
                "score": score,
                "correct_count": correct_count,
                "total": total,
                "items": results,
                "summary": next_suggestion,
            },
        }


class LearningPathService:
    def __init__(self) -> None:
        self.tasks = TaskService()
        self.workflow = LearningPathWorkflow()

    def adjust(self, task_id: str, reason: str | None = None) -> dict[str, Any]:
        task = self.tasks.get_task(task_id)
        self.workflow.run(task, reason)
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
