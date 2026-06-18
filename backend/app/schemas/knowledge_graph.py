from typing import Any

from app.schemas.base import ApiModel


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
