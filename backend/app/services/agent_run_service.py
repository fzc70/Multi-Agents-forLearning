from __future__ import annotations

from typing import Any

from app.repositories.agent_run_repository import AgentRunRepository
from app.storage.database import loads


class AgentRunService:
    """Agent 运行日志查询服务，用于调试与可追溯。"""

    def __init__(self) -> None:
        """初始化 AgentRunService 所需的依赖。"""
        self.repo = AgentRunRepository()

    def list(self, task_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """查询并返回智能体运行日志。"""
        return [
            {
                **row,
                "input_json": loads(row["input_json"], {}),
                "output_json": loads(row["output_json"], None),
            }
            for row in self.repo.list(task_id, limit)
        ]
