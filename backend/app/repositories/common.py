from __future__ import annotations

from typing import Any

from app.storage.database import loads


def label_size(size: int) -> str:
    """根据文本长度计算图谱节点显示尺寸。"""
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


def decode_json_columns(row: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    """反序列化记录中的 JSON 字段。"""
    copy = dict(row)
    for column in columns:
        copy[column] = loads(copy.get(column), [])
    return copy
