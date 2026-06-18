import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from app.core.config import get_settings


def _db_path() -> Path:
    """获取当前数据库文件路径。"""
    settings = get_settings()
    settings.data_path.mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return settings.sqlite_path


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """提供带事务管理的 SQLite 连接。"""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """将 SQLite 行对象转换为普通字典。"""
    return dict(row) if row else None


def dumps(value: Any) -> str:
    """将 Python 数据序列化为 JSON 文本。"""
    return json.dumps(value, ensure_ascii=False)


def loads(value: str | None, default: Any = None) -> Any:
    """安全地反序列化 JSON 文本。"""
    if value is None or value == "":
        return default
    return json.loads(value)


def init_db() -> None:
    """初始化 SQLite 数据库结构。"""
    from app.storage.schema import apply_schema

    with get_conn() as conn:
        apply_schema(conn)
