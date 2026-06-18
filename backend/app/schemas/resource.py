from typing import Any, Literal

from pydantic import Field

from app.schemas.base import ApiModel
from app.schemas.common import SourceRef


ResourceType = Literal[
    "讲解文档", "练习题", "思维导图", "拓展阅读", "代码案例", "知识图谱"
]


class LearningResource(ApiModel):
    id: str
    type: ResourceType
    title: str
    description: str
    content: str | None = None
    detail: dict[str, Any] = Field(default_factory=dict)
    recommendation_reason: str | None = None
    source_refs: list[SourceRef] = Field(default_factory=list)
    created_at: str | None = None


class GenerateResourceRequest(ApiModel):
    task_id: str
    types: list[str] | None = None
    mode: Literal["smart", "selected"] = "smart"


class AttachResourceRequest(ApiModel):
    task_id: str


class SubmitExerciseRequest(ApiModel):
    task_id: str
    answers: dict[str, Any]


class ResourceMasteryRequest(ApiModel):
    task_id: str
    mastery: int = Field(ge=0, le=100)
    note: str | None = None
