"""工作流层入口。

Workflow 负责编排 Agent、Tool 和 Repository，不处理 HTTP 请求。
"""

from app.workflows.assessment_workflow import AssessmentWorkflow
from app.workflows.chat_profile_workflow import ChatProfileWorkflow
from app.workflows.knowledge_graph_workflow import KnowledgeGraphWorkflow
from app.workflows.learning_path_workflow import LearningPathWorkflow
from app.workflows.resource_generation_workflow import ResourceGenerationWorkflow

__all__ = [
    "AssessmentWorkflow",
    "ChatProfileWorkflow",
    "KnowledgeGraphWorkflow",
    "LearningPathWorkflow",
    "ResourceGenerationWorkflow",
]
