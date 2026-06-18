from __future__ import annotations

from typing import Any

from app.agents.resource_agent import ResourceAgent
from app.domain.constants import DEFAULT_SMART_RESOURCE_TYPES
from app.repositories.resource_repository import ResourceRepository
from app.repositories.task_repository import TaskRepository
from app.tools.context_builder import ContextBuilder
from app.tools.resource_quality import ResourceQualityGate


class ResourceGenerationWorkflow:
    """资源生成工作流：统一决定资源类型、构建上下文、调用资源 Agent 和质量门禁。"""

    def __init__(self) -> None:
        """初始化 ResourceGenerationWorkflow 所需的依赖。"""
        self.agent = ResourceAgent()
        self.resources = ResourceRepository()
        self.context_builder = ContextBuilder()
        self.quality = ResourceQualityGate()
        self.tasks = TaskRepository()

    def run(
        self, task: dict[str, Any], types: list[str] | None, mode: str
    ) -> list[dict[str, Any]]:
        """编排资源选择、内容生成、质检和持久化流程。"""
        task_id = task["id"]
        if mode == "smart" or not types:
            # 智能生成走完整资源包，保证学生拿到讲解、练习、图谱和迁移材料。
            types = list(DEFAULT_SMART_RESOURCE_TYPES)
        context = self.context_builder.build_for_task(
            task, f"{task['title']} {task['next_action']}", top_k=4
        )
        contexts = context.get("retrieved_contexts", [])
        output = self.agent.run(
            {
                "task_title": task["title"],
                "next_action": task["next_action"],
                "types": types,
                "provided_context": context,
                "retrieved_contexts": contexts,
                "recent_exercise_memory": [
                    item
                    for item in context.get("memory", [])
                    if item.get("type") in {"exercise", "resource_mastery"}
                ],
            },
            task_id,
        )
        created: list[dict[str, Any]] = []
        source_refs = [
            item["source_ref"] for item in contexts if item.get("source_ref")
        ]
        for resource in output.get("resources", []):
            resource = self.quality.normalize(
                resource, task["title"], task["next_action"]
            )
            resource_id = self.resources.create(
                task_id=task_id,
                type_=resource["type"],
                title=resource["title"],
                description=resource["description"],
                content=resource["content"],
                detail=resource["detail"],
                recommendation_reason=resource.get("recommendation_reason", ""),
                source_refs=source_refs,
            )
            created.append({"id": resource_id, **resource, "source_refs": source_refs})
        self.tasks.touch(task_id)
        return created
