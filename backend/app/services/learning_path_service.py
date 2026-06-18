from __future__ import annotations

from typing import Any

from app.services.task_service import TaskService
from app.workflows.learning_path_workflow import LearningPathWorkflow


class LearningPathService:
    """学习路径服务：只负责路径工作流入口和阶段推进。"""

    def __init__(self) -> None:
        """初始化 LearningPathService 所需的依赖。"""
        self.tasks = TaskService()
        self.workflow = LearningPathWorkflow()

    def adjust(self, task_id: str, reason: str | None = None) -> dict[str, Any]:
        """根据学习证据调整当前学习路径。"""
        task = self.tasks.get_task(task_id)
        self.workflow.run(task, reason)
        return self.tasks.get_task(task_id)

    def complete_step(self, task_id: str, step_id: str) -> dict[str, Any]:
        """完成路径步骤并更新任务学习状态。"""
        self.tasks.get_task(task_id)
        self.workflow.complete_step(task_id, step_id)
        return self.tasks.get_task(task_id)
