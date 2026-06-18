from typing import Literal

from app.schemas.base import ApiModel


class LearningMaterial(ApiModel):
    id: str
    name: str
    type: Literal["PDF", "文档", "网页", "笔记"]
    size: str
    status: Literal["已解析", "解析中", "待处理"]
    text_length: int
    used_for: list[str]
    updated_at: str
