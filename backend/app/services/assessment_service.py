from __future__ import annotations

from typing import Any

from app.services.task_service import TaskService
from app.workflows.assessment_workflow import AssessmentWorkflow


class AssessmentService:
    """学习评估服务。

    当前主要保留手动触发入口；动态评估由 ResourceService 在练习/掌握反馈后更新。
    """

    def __init__(self) -> None:
        """初始化 AssessmentService 所需的依赖。"""
        self.tasks = TaskService()
        self.workflow = AssessmentWorkflow()

    def assess(self, task_id: str, answers: list[dict[str, Any]]) -> dict[str, Any]:
        """汇总学习证据并更新动态评估结果。"""
        task = self.tasks.get_task(task_id)
        self.workflow.run(task, answers)
        return self.tasks.get_task(task_id)
