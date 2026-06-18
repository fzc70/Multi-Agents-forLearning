from __future__ import annotations

from typing import Any

from app.agents.planner_agent import PlannerAgent
from app.repositories.learning_path_repository import LearningPathRepository
from app.repositories.task_repository import TaskRepository


class LearningPathWorkflow:
    """学习路径工作流：根据画像、薄弱点和资源状态生成/推进路径。"""

    def __init__(self) -> None:
        """初始化 LearningPathWorkflow 所需的依赖。"""
        self.agent = PlannerAgent()
        self.path = LearningPathRepository()
        self.tasks = TaskRepository()

    def run(self, task: dict[str, Any], reason: str | None = None) -> dict[str, Any]:
        """编排学习路径生成、调整和推进流程。"""
        task_id = task["id"]
        output = self.agent.run(
            {
                "task_title": task["title"],
                "weak_points": task.get("assessment", {}).get("weak_points", []),
                "reason": reason,
            },
            task_id,
        )
        self.path.replace(task_id, output["steps"])
        next_action = (
            output["steps"][0]["title"] if output.get("steps") else task["next_action"]
        )
        self.tasks.touch(
            task_id,
            next_action=next_action,
            reason=output.get("note", "学习路径已调整。"),
        )
        return output

    def complete_step(self, task_id: str, step_id: str) -> None:
        """校验前置状态并完成指定学习路径步骤。"""
        self.path.mark_step_done(task_id, step_id)
        self.tasks.touch(task_id, reason="学生确认已完成当前学习阶段。")
