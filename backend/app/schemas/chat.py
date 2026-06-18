from app.schemas.base import ApiModel
from app.schemas.common import Message, SourceRef
from app.schemas.task import LearningTask


class ChatRequest(ApiModel):
    task_id: str
    message: str
    use_rag: bool = True


class ChatResponse(ApiModel):
    task: LearningTask
    reply: Message
    grounded: bool
    source_refs: list[SourceRef]
