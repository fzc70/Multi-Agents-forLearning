"""API Schema 层入口。

模型按业务领域拆分；路由统一从本包导入，避免依赖单一大文件。
"""

from app.schemas.agent_run import AgentRunLog
from app.schemas.assessment import Assessment, AssessmentRequest
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
]
