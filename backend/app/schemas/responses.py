from typing import Any

from app.schemas.base import ApiModel
from app.schemas.resource import LearningResource
from app.schemas.task import LearningTask


class GenerateResourceResponse(ApiModel):
    task: LearningTask
    resources: list[LearningResource]


class SubmitExerciseResponse(ApiModel):
    task: LearningTask
    result: dict[str, Any]
