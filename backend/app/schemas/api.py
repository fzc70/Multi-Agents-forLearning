"""Schema 兼容导出。

具体模型已按领域拆分到同目录下的 task/resource/chat 等文件。
保留本文件是为了兼容现有路由导入，避免一次重构影响接口行为。
"""

from app.schemas.agent_run import AgentRunLog
from app.schemas.assessment import Assessment, AssessmentRequest
from app.schemas.base import ApiModel, to_camel
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import Message, SourceRef
from app.schemas.health import HealthResponse
from app.schemas.knowledge_graph import GraphEdge, GraphNode, KnowledgeGraph, KnowledgeGraphRequest
from app.schemas.material import LearningMaterial
from app.schemas.path import AdjustPathRequest, CompleteStepRequest, LearningStep
from app.schemas.profile import ProfileDimension, StudentProfile
from app.schemas.resource import (
    AttachResourceRequest,
    GenerateResourceRequest,
    LearningResource,
    ResourceMasteryRequest,
    ResourceType,
    SubmitExerciseRequest,
)
from app.schemas.responses import GenerateResourceResponse, SubmitExerciseResponse
from app.schemas.task import CreateTaskRequest, LearningTask


__all__ = [
    "AdjustPathRequest",
    "AgentRunLog",
    "ApiModel",
    "Assessment",
    "AssessmentRequest",
    "AttachResourceRequest",
    "ChatRequest",
    "ChatResponse",
    "CompleteStepRequest",
    "CreateTaskRequest",
    "GenerateResourceRequest",
    "GenerateResourceResponse",
    "GraphEdge",
    "GraphNode",
    "HealthResponse",
    "KnowledgeGraph",
    "KnowledgeGraphRequest",
    "LearningMaterial",
    "LearningResource",
    "LearningStep",
    "LearningTask",
    "Message",
    "ProfileDimension",
    "ResourceMasteryRequest",
    "ResourceType",
    "SourceRef",
    "StudentProfile",
    "SubmitExerciseRequest",
    "SubmitExerciseResponse",
    "to_camel",
]
