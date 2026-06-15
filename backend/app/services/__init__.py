"""应用服务层入口。

Service 负责业务编排：校验输入、调用 Workflow/Repository、返回聚合结果。
路由层不直接调用 Agent，Agent 也不直接写数据库。
"""

from app.services.agent_run_service import AgentRunService
from app.services.assessment_service import AssessmentService
from app.services.chat_service import ChatService
from app.services.exercise_service import ExerciseService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.learning_path_service import LearningPathService
from app.services.material_service import MaterialService
from app.services.resource_service import ResourceService
from app.services.task_service import TaskService

__all__ = [
    "AgentRunService",
    "AssessmentService",
    "ChatService",
    "ExerciseService",
    "KnowledgeGraphService",
    "LearningPathService",
    "MaterialService",
    "ResourceService",
    "TaskService",
]
