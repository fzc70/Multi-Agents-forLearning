from __future__ import annotations

from typing import Any

from app.core.errors import bad_request, not_found
from app.repositories.repositories import TaskRepository
from app.services.task_assembler import TaskAssembler


class TaskService:
    """学习任务应用服务。

    Service 层只编排领域操作和仓储调用，不直接处理 HTTP，也不调用 LLM。
    """

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
        title = title.strip()
        if not title:
            raise bad_request("任务标题不能为空")
        task_id = self.repo.create(title, foundation, expected_outcome)
        return self.get_task(task_id)

    def delete_task(self, task_id: str) -> dict[str, Any]:
        self.get_task(task_id)
        self.repo.delete(task_id)
        return {"ok": True}

