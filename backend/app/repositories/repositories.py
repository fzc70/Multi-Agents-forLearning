"""Repository 兼容导出。

具体 SQL 按领域拆分到 task_repository/resource_repository 等文件。
保留本文件是为了兼容历史导入，业务代码应逐步改为从具体 repository 模块导入。
"""

from app.repositories.agent_run_repository import AgentRunRepository
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.common import decode_json_columns
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.exercise_attempt_repository import ExerciseAttemptRepository
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.repositories.learning_path_repository import LearningPathRepository
from app.repositories.material_repository import MaterialRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resource_mastery_repository import ResourceMasteryRepository
from app.repositories.resource_repository import ResourceRepository
from app.repositories.task_repository import TaskRepository
from app.storage.database import dumps, loads

__all__ = [
    "AgentRunRepository",
    "AssessmentRepository",
    "ConversationRepository",
    "ExerciseAttemptRepository",
    "KnowledgeGraphRepository",
    "LearningPathRepository",
    "MaterialRepository",
    "MemoryRepository",
    "ProfileRepository",
    "ResourceMasteryRepository",
    "ResourceRepository",
    "TaskRepository",
    "decode_json_columns",
    "dumps",
    "loads",
]
