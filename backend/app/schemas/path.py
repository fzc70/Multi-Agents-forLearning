from typing import Literal

from app.schemas.base import ApiModel


class LearningStep(ApiModel):
    id: str
    title: str
    objective: str
    resource: str
    exercise: str
    status: Literal["done", "current", "todo"]


class CompleteStepRequest(ApiModel):
    task_id: str
    step_id: str


class AdjustPathRequest(ApiModel):
    task_id: str
    reason: str | None = None
