from pydantic import Field

from app.schemas.assessment import Assessment
from app.schemas.base import ApiModel
from app.schemas.common import Message
from app.schemas.material import LearningMaterial
from app.schemas.path import LearningStep
from app.schemas.profile import StudentProfile
from app.schemas.resource import LearningResource


class LearningTask(ApiModel):
    id: str
    title: str
    category: str
    progress: int
    updated_at: str
    next_action: str
    reason: str
    profile_tags: list[str]
    profile: StudentProfile | None = None
    materials: list[LearningMaterial] = Field(default_factory=list)
    materials_count: int
    exercise_count: int
    resources: list[LearningResource]
    path: list[LearningStep]
    assessment: Assessment
    messages: list[Message]
    path_adjustment_note: str | None = None


class CreateTaskRequest(ApiModel):
    title: str
    foundation: str | None = None
    expected_outcome: str | None = None
