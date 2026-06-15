from __future__ import annotations

from typing import Any

from app.core.errors import bad_request, not_found
from app.domain.constants import RESOURCE_TYPE_SET
from app.repositories.repositories import (
    AssessmentRepository,
    LearningPathRepository,
    MemoryRepository,
    ProfileRepository,
    ResourceMasteryRepository,
    ResourceRepository,
    TaskRepository,
    loads,
)
from app.services.exercise_service import ExerciseService
from app.services.task_service import TaskService
from app.tools.resource_quality import ResourceQualityGate
from app.workflows.workflows import ResourceGenerationWorkflow


class ResourceService:
    """学习资源服务。

    负责资源生成、详情规范化、路径挂载和资源掌握反馈。
    Agent 只产出结构化结果；数据库写入和评估联动由 Service 编排。
    """

    allowed_types = RESOURCE_TYPE_SET

    def __init__(self) -> None:
        self.tasks = TaskService()
        self.workflow = ResourceGenerationWorkflow()
        self.resources = ResourceRepository()
        self.path = LearningPathRepository()
        self.mastery = ResourceMasteryRepository()

    def generate(self, task_id: str, types: list[str] | None, mode: str) -> dict[str, Any]:
        task = self.tasks.get_task(task_id)
        selected_types = [item for item in (types or []) if item in self.allowed_types]
        if mode == "selected" and not selected_types:
            raise bad_request("请选择有效的资源类型")
        resources = self.workflow.run(task, selected_types or None, mode)
        return {"task": self.tasks.get_task(task_id), "resources": resources}

    def attach_to_path(self, task_id: str, resource_id: str) -> dict[str, Any]:
        self.tasks.get_task(task_id)
        resource = self.resources.get(resource_id, task_id)
        if not resource:
            raise not_found("学习资源不存在")
        self.path.attach_resource_to_current_step(task_id, resource["title"])
        TaskRepository().touch(task_id, reason=f"已将「{resource['title']}」加入当前学习阶段。")
        return self.tasks.get_task(task_id)

    def get_resource(self, task_id: str, resource_id: str) -> dict[str, Any]:
        """读取资源详情，并用质量门禁补齐旧数据或异常 LLM 输出。"""

        self.tasks.get_task(task_id)
        resource = self.resources.get(resource_id, task_id)
        if not resource:
            raise not_found("学习资源不存在")
        task = self.tasks.get_task(task_id)
        normalized = ResourceQualityGate().normalize(
            {
                "type": resource["type"],
                "title": resource["title"],
                "description": resource["description"],
                "content": resource["content"],
                "detail": loads(resource.get("detail_json"), {}),
                "recommendation_reason": resource["recommendation_reason"],
            },
            task["title"],
            task["next_action"],
        )
        self.resources.update_normalized(
            resource["id"],
            task_id,
            normalized["content"],
            normalized["detail"],
            normalized["description"],
            normalized.get("recommendation_reason", ""),
        )
        return {
            "id": resource["id"],
            **normalized,
            "source_refs": loads(resource["source_refs"], []),
            "created_at": resource.get("created_at"),
        }

    def submit_exercise(self, task_id: str, resource_id: str, answers: dict[str, Any]) -> dict[str, Any]:
        return ExerciseService().submit(task_id, resource_id, answers)

    def mark_mastery(self, task_id: str, resource_id: str, mastery: int, note: str | None = None) -> dict[str, Any]:
        resource = self.get_resource(task_id, resource_id)
        self.mastery.upsert(task_id, resource_id, resource["title"], mastery, note or "")
        MemoryRepository().add(
            task_id,
            "resource_mastery",
            f"学生确认资源「{resource['title']}」掌握度 {mastery}%",
            f"来自资源掌握反馈：{resource['title']}",
            72,
        )
        assessment_score = ExerciseService().dynamic_score(task_id)
        AssessmentRepository().update(
            task_id,
            assessment_score,
            f"综合最近练习和资源掌握反馈，当前掌握度为 {assessment_score}。",
            ["资源理解不稳定"] if mastery < 80 else ["保持稳定输出"],
            ["掌握度自评偏低"] if mastery < 80 else ["暂无明显易错类型"],
            f"资源「{resource['title']}」自评掌握度 {mastery}%",
            "低掌握资源建议回看讲解并做针对练习。" if mastery < 80 else "可以推进学习路径的下一阶段。",
        )
        ProfileRepository().update_dimension(task_id, "preference", f"最近资源掌握反馈 {mastery}%", f"来自资源「{resource['title']}」")
        TaskRepository().touch(task_id, reason="根据资源掌握反馈更新评估。")
        return self.tasks.get_task(task_id)

