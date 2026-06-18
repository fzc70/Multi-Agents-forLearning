from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import get_conn


class ResourceMasteryRepository:
    def upsert(
        self,
        task_id: str,
        resource_id: str,
        resource_title: str,
        mastery: int,
        note: str = "",
    ) -> None:
        """新增或更新资源掌握度记录。"""
        now = now_iso()
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO resource_mastery(id,task_id,resource_id,resource_title,mastery,note,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(task_id, resource_id)
                DO UPDATE SET mastery=excluded.mastery,note=excluded.note,updated_at=excluded.updated_at
                """,
                (
                    new_id("mastery"),
                    task_id,
                    resource_id,
                    resource_title,
                    mastery,
                    note,
                    now,
                    now,
                ),
            )

    def list_recent(self, task_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """查询最近的资源掌握度记录。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM resource_mastery WHERE task_id=? ORDER BY updated_at DESC LIMIT ?",
                (task_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]
