from typing import Any

from app.schemas.base import ApiModel


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
