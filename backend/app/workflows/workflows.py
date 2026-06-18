"""Workflow 兼容导出。

工作流实现已按业务拆分到 chat_profile_workflow/resource_generation_workflow 等文件。
保留本文件兼容旧导入。
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
