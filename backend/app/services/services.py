"""服务层兼容导出。

历史代码从 `app.services.services` 导入所有 Service。实际实现已拆到独立文件，
这里仅做导出，避免路由和测试一次性大面积改动。
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
