from __future__ import annotations

from typing import Any

from app.domain.constants import RESOURCE_TYPE_EXERCISE
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.learning_path_repository import LearningPathRepository
from app.repositories.material_repository import MaterialRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resource_repository import ResourceRepository
from app.repositories.task_repository import TaskRepository
from app.storage.database import loads
from app.tools.resource_quality import ResourceQualityGate


class TaskAssembler:
    """把多张持久化表装配成前端需要的任务视图。"""

    def __init__(self) -> None:
        """初始化 TaskAssembler 所需的依赖。"""
        self.tasks = TaskRepository()
        self.profile = ProfileRepository()
        self.materials = MaterialRepository()
        self.resources = ResourceRepository()
        self.path = LearningPathRepository()
        self.assessment = AssessmentRepository()
        self.conversation = ConversationRepository()

    def assemble(self, task_id: str) -> dict[str, Any] | None:
        """聚合任务及其关联数据。"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        return self._assemble_from_row(task)

    def list(self) -> list[dict[str, Any]]:
        """查询并返回业务数据。"""
        return [self._assemble_from_row(row) for row in self.tasks.list()]

    def _assemble_from_row(self, task: dict[str, Any]) -> dict[str, Any]:
        """将任务记录及关联数据组装为完整任务视图。"""
        task_id = task["id"]
        dimensions = [
            {
                "id": item["id"],
                "label": item["label"],
                "value": item["value"],
                "confidence": item["confidence"],
                "evidence": item["evidence"],
                "updated_at": item["updated_at"],
            }
            for item in self.profile.list_dimensions(task_id)
        ]
        evidences = [item["evidence"] for item in dimensions if item["evidence"]][:4]
        profile = {
            "summary": self._profile_summary(dimensions),
            "dimensions": dimensions,
            "recent_evidences": evidences,
        }
        materials = [
            {
                "id": item["id"],
                "name": item["name"],
                "type": item["type"],
                "size": item["size_label"],
                "status": item["status"],
                "text_length": item["text_length"],
                "used_for": loads(item["used_for"], []),
                "updated_at": item["updated_at"],
            }
            for item in self.materials.list(task_id)
        ]
        resources = [
            self._resource_from_row(item, task) for item in self.resources.list(task_id)
        ]
        steps = [
            {
                "id": item["id"],
                "title": item["title"],
                "objective": item["objective"],
                "resource": item["resource"],
                "exercise": item["exercise"],
                "status": item["status"],
            }
            for item in self.path.list(task_id)
        ]
        assessment_row = self.assessment.get(task_id) or {}
        assessment = {
            "score": assessment_row.get("score", 0),
            "mastery": assessment_row.get("mastery", "暂未评估"),
            "weak_points": loads(assessment_row.get("weak_points"), []),
            "mistake_types": loads(assessment_row.get("mistake_types"), []),
            "effort": assessment_row.get("effort", "暂无记录"),
            "next_suggestion": assessment_row.get(
                "next_suggestion", "先完成一次小测评。"
            ),
            "tested": bool(assessment_row.get("tested", 0)),
        }
        messages = [
            {"id": item["id"], "role": item["role"], "content": item["content"]}
            for item in self.conversation.list_messages(task_id)
        ]
        progress = self._path_progress(steps)
        return {
            "id": task_id,
            "title": task["title"],
            "category": task["category"],
            "progress": progress,
            "updated_at": task["updated_at"],
            "next_action": task["next_action"],
            "reason": task["reason"],
            "profile_tags": loads(task["profile_tags"], []),
            "profile": profile,
            "materials": materials,
            "materials_count": len(materials),
            "exercise_count": len(
                [r for r in resources if r["type"] == RESOURCE_TYPE_EXERCISE]
            ),
            "resources": resources,
            "path": steps,
            "assessment": assessment,
            "messages": messages,
        }

    @staticmethod
    def _path_progress(steps: list[dict[str, Any]]) -> int:
        """根据路径步骤状态计算学习进度。"""
        if not steps:
            return 0
        done = len([step for step in steps if step["status"] == "done"])
        return round(done / len(steps) * 100)

    @staticmethod
    def _profile_summary(dimensions: list[dict[str, Any]]) -> str:
        """根据画像维度构建摘要。"""
        values = {item["id"]: item["value"] for item in dimensions}
        return (
            f"目标：{values.get('goal', '待明确')}；基础：{values.get('foundation', '待了解')}；"
            f"当前薄弱点：{values.get('weakness', '待观察')}。"
        )

    @staticmethod
    def _resource_from_row(
        item: dict[str, Any], task: dict[str, Any]
    ) -> dict[str, Any]:
        """将资源记录转换为接口数据结构。"""
        normalized = ResourceQualityGate().normalize(
            {
                "type": item["type"],
                "title": item["title"],
                "description": item["description"],
                "content": item["content"],
                "detail": loads(item.get("detail_json"), {}),
                "recommendation_reason": item["recommendation_reason"],
            },
            task["title"],
            task["next_action"],
        )
        return {
            "id": item["id"],
            **normalized,
            "source_refs": loads(item["source_refs"], []),
            "created_at": item.get("created_at"),
        }
