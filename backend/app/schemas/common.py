from typing import Literal

from app.schemas.base import ApiModel


class Message(ApiModel):
    id: str
    role: Literal["user", "assistant"]
    content: str


class SourceRef(ApiModel):
    type: str
    id: str
    title: str | None = None
    page: int | None = None
    chunk_id: str | None = None
