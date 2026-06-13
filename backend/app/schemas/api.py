from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Message(ApiModel):
    id: str
    role: Literal["user", "assistant"]
    content: str


class LearningStep(ApiModel):
    id: str
    title: str
    objective: str
    resource: str
    exercise: str
    status: Literal["done", "current", "todo"]


ResourceType = Literal["讲解文档", "练习题", "思维导图", "拓展阅读", "视频脚本", "代码案例", "知识图谱"]


class SourceRef(ApiModel):
    type: str
    id: str
    title: str | None = None
    page: int | None = None
    chunk_id: str | None = None


class LearningResource(ApiModel):
    id: str
    type: ResourceType
    title: str
    description: str
    content: str | None = None
    recommendation_reason: str | None = None
    source_refs: list[SourceRef] = Field(default_factory=list)


class Assessment(ApiModel):
    score: int
    mastery: str
    weak_points: list[str]
    mistake_types: list[str]
    effort: str
    next_suggestion: str
    tested: bool


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


class LearningMaterial(ApiModel):
    id: str
    name: str
    type: Literal["PDF", "文档", "网页", "笔记"]
    size: str
    status: Literal["已解析", "解析中", "待处理"]
    text_length: int
    used_for: list[str]
    updated_at: str


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


class ChatRequest(ApiModel):
    task_id: str
    message: str
    use_rag: bool = True


class ChatResponse(ApiModel):
    task: LearningTask
    reply: Message
    grounded: bool
    source_refs: list[SourceRef]


class GenerateResourceRequest(ApiModel):
    task_id: str
    types: list[str] | None = None
    mode: Literal["smart", "selected"] = "smart"


class GenerateResourceResponse(ApiModel):
    task: LearningTask
    resources: list[LearningResource]


class AttachResourceRequest(ApiModel):
    task_id: str


class AdjustPathRequest(ApiModel):
    task_id: str
    reason: str | None = None


class AssessmentRequest(ApiModel):
    task_id: str
    answers: list[dict[str, Any]] = Field(default_factory=list)


class KnowledgeGraphRequest(ApiModel):
    task_id: str


class GraphNode(ApiModel):
    id: str
    label: str
    type: str = "concept"


class GraphEdge(ApiModel):
    source: str
    target: str
    label: str


class KnowledgeGraph(ApiModel):
    id: str
    task_id: str
    title: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    source_stats: dict[str, Any]
    created_at: str


class AgentRunLog(ApiModel):
    id: str
    task_id: str | None = None
    workflow_run_id: str | None = None
    agent_name: str
    model: str
    prompt_version: str
    input_json: dict[str, Any]
    output_json: dict[str, Any] | None = None
    error: str | None = None
    latency_ms: int
    created_at: str


class HealthResponse(ApiModel):
    status: str
    app_name: str
    llm_provider: str
    model: str
    api_key_configured: bool
