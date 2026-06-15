from __future__ import annotations

from typing import Any

from app.core.errors import bad_request
from app.repositories.repositories import KnowledgeGraphRepository, loads
from app.services.task_service import TaskService
from app.workflows.workflows import KnowledgeGraphWorkflow


class KnowledgeGraphService:
    """知识图谱服务。

    负责图谱工作流入口和最新图谱查询，不在路由层拼装图谱结构。
    """

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

