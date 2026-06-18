from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import dumps, get_conn


class ExerciseAttemptRepository:
    def add(
        self,
        task_id: str,
        resource_id: str,
        resource_title: str,
        score: int,
        detail: dict[str, Any],
    ) -> str:
        """新增一条练习记录记录。"""
        attempt_id = new_id("attempt")
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO exercise_attempts(id,task_id,resource_id,resource_title,score,total_score,detail_json,created_at)
                VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    attempt_id,
                    task_id,
                    resource_id,
                    resource_title,
                    score,
                    100,
                    dumps(detail),
                    now_iso(),
                ),
            )
        return attempt_id

    def list_recent(self, task_id: str, limit: int = 12) -> list[dict[str, Any]]:
        """查询最近的练习记录记录。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM exercise_attempts WHERE task_id=? ORDER BY created_at DESC LIMIT ?",
                (task_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]
