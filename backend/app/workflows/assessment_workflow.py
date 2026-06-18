from __future__ import annotations

from typing import Any

from app.agents.evaluator_agent import EvaluatorAgent
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.task_repository import TaskRepository


class AssessmentWorkflow:
    """评估工作流：汇总作答表现，更新评估结果、画像和下一步建议。"""

    def __init__(self) -> None:
        """初始化 AssessmentWorkflow 所需的依赖。"""
        self.agent = EvaluatorAgent()
        self.assessment = AssessmentRepository()
        self.profile = ProfileRepository()
        self.tasks = TaskRepository()

    def run(
        self, task: dict[str, Any], answers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """编排学习证据收集、评估和结果持久化流程。"""
        task_id = task["id"]
        output = self.agent.run(
            {"task_title": task["title"], "answers": answers}, task_id
        )
        self.assessment.update(
            task_id,
            int(output["score"]),
            str(output["mastery"]),
            list(output["weak_points"]),
            list(output["mistake_types"]),
            str(output["effort"]),
            str(output["next_suggestion"]),
        )
        if output.get("weak_points"):
            self.profile.update_dimension(
                task_id, "weakness", "；".join(output["weak_points"]), "来自学习测评"
            )
        self.profile.update_dimension(
            task_id, "exercise", f"测评分数 {output['score']}", "来自学习测评"
        )
        self.tasks.touch(
            task_id,
            next_action=str(output["next_suggestion"]),
            reason="根据最近测评结果更新。",
        )
        return output
