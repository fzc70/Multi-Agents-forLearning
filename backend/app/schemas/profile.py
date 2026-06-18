from app.schemas.base import ApiModel


class ProfileDimension(ApiModel):
    id: str
    label: str
    value: str
    confidence: int
    evidence: str
    updated_at: str


class StudentProfile(ApiModel):
    summary: str
    dimensions: list[ProfileDimension]
    recent_evidences: list[str]
