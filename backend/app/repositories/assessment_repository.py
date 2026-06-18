from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import dumps, get_conn, row_to_dict


class AssessmentRepository:
    def ensure_default(self, task_id: str) -> None:
        """确保默认学习评估记录存在。"""
        if self.get(task_id):
            return
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO assessment_results(id,task_id,score,mastery,weak_points,mistake_types,effort,next_suggestion,tested,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    new_id("assess"),
                    task_id,
                    0,
                    "暂未评估",
                    "[]",
                    "[]",
                    "暂无记录",
                    "先完成一次小测评，建立初始学习画像。",
                    0,
                    now_iso(),
                ),
            )

    def get(self, task_id: str) -> dict[str, Any] | None:
        """查询指定的学习评估记录。"""
        with get_conn() as conn:
            return row_to_dict(
                conn.execute(
                    "SELECT * FROM assessment_results WHERE task_id=?", (task_id,)
                ).fetchone()
            )

    def update(
        self,
        task_id: str,
        score: int,
        mastery: str,
        weak_points: list[str],
        mistake_types: list[str],
        effort: str,
        next_suggestion: str,
    ) -> None:
        """更新指定的学习评估记录。"""
        self.ensure_default(task_id)
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE assessment_results
                SET score=?,mastery=?,weak_points=?,mistake_types=?,effort=?,next_suggestion=?,tested=1,updated_at=?
                WHERE task_id=?
                """,
                (
                    score,
                    mastery,
                    dumps(weak_points),
                    dumps(mistake_types),
                    effort,
                    next_suggestion,
                    now_iso(),
                    task_id,
                ),
            )
