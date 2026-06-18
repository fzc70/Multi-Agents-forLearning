from __future__ import annotations

from typing import Any

from app.core.errors import bad_request
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.services.task_service import TaskService
from app.storage.database import loads
from app.workflows.knowledge_graph_workflow import KnowledgeGraphWorkflow


class KnowledgeGraphService:
    """知识图谱服务。

    负责图谱工作流入口和最新图谱查询，不在路由层拼装图谱结构。
    """

    def __init__(self) -> None:
        """初始化 KnowledgeGraphService 所需的依赖。"""
        self.tasks = TaskService()
        self.workflow = KnowledgeGraphWorkflow()
        self.repo = KnowledgeGraphRepository()

    def build(self, task_id: str) -> dict[str, Any]:
        """生成并保存任务知识图谱。"""
        task = self.tasks.get_task(task_id)
        try:
            return self.workflow.run(task)
        except ValueError as exc:
            raise bad_request(str(exc)) from exc

    def latest(self, task_id: str) -> dict[str, Any] | None:
        """返回任务最新的知识图谱。"""
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
