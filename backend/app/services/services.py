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


class ResourceService:
    allowed_types = {"讲解文档", "练习题", "思维导图", "拓展阅读", "视频脚本", "代码案例", "知识图谱"}

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
