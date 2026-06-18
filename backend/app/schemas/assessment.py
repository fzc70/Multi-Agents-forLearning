from typing import Any

from pydantic import Field

from app.schemas.base import ApiModel


class Assessment(ApiModel):
    score: int
    mastery: str
    weak_points: list[str]
    mistake_types: list[str]
    effort: str
    next_suggestion: str
    tested: bool


class AssessmentRequest(ApiModel):
    task_id: str
    answers: list[dict[str, Any]] = Field(default_factory=list)
