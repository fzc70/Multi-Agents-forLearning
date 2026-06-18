from __future__ import annotations

from typing import Any

from app.core.errors import bad_request, not_found
from app.repositories.task_repository import TaskRepository
from app.services.task_assembler import TaskAssembler


class TaskService:
    """学习任务应用服务。

    Service 层只编排领域操作和仓储调用，不直接处理 HTTP，也不调用 LLM。
    """

    def __init__(self) -> None:
        """初始化 TaskService 所需的依赖。"""
        self.repo = TaskRepository()
        self.assembler = TaskAssembler()

    def list_tasks(self) -> list[dict[str, Any]]:
        """查询并返回完整学习任务列表。"""
        return self.assembler.list()

    def get_task(self, task_id: str) -> dict[str, Any]:
        """查询并返回指定学习任务。"""
        task = self.assembler.assemble(task_id)
        if not task:
            raise not_found("学习任务不存在")
        return task

    def create_task(
        self, title: str, foundation: str | None, expected_outcome: str | None
    ) -> dict[str, Any]:
        """校验输入并创建学习任务。"""
        title = title.strip()
        if not title:
            raise bad_request("任务标题不能为空")
        task_id = self.repo.create(title, foundation, expected_outcome)
        return self.get_task(task_id)

    def delete_task(self, task_id: str) -> dict[str, Any]:
        """校验任务存在后删除学习任务。"""
        self.get_task(task_id)
        self.repo.delete(task_id)
        return {"ok": True}
