from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import get_conn


class MemoryRepository:
    def add(
        self,
        task_id: str,
        type_: str,
        content: str,
        evidence: str,
        importance: int = 50,
    ) -> str:
        """新增一条长期记忆记录。"""
        item_id = new_id("mem")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO memory_records(id,task_id,type,content,evidence,importance,created_at) VALUES(?,?,?,?,?,?,?)",
                (item_id, task_id, type_, content, evidence, importance, now_iso()),
            )
        return item_id

    def list(self, task_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """查询当前范围内的长期记忆记录。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM memory_records WHERE task_id=? ORDER BY importance DESC, created_at DESC LIMIT ?",
                (task_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]
