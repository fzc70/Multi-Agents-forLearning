from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import get_conn


class LearningPathRepository:
    def ensure_default(self, task_id: str, title: str) -> None:
        """确保默认学习路径记录存在。"""
        if self.list(task_id):
            return
        defaults = [
            (
                "明确学习目标",
                "把目标拆成可执行的小步骤。",
                "对话澄清",
                "回答 3 个目标问题",
                "current",
            ),
            (
                "评估当前基础",
                "了解已经掌握什么、卡在哪里。",
                "小测评",
                "完成一次基础测评",
                "todo",
            ),
            (
                "生成学习资源",
                "围绕当前薄弱点生成资料和练习。",
                "个性化资源",
                "完成第一组练习",
                "todo",
            ),
        ]
        now = now_iso()
        with get_conn() as conn:
            for index, item in enumerate(defaults):
                conn.execute(
                    """
                    INSERT INTO learning_steps(id,task_id,title,objective,resource,exercise,status,sort_order,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                    """,
                    (new_id("step"), task_id, *item, index, now, now),
                )

    def list(self, task_id: str) -> list[dict[str, Any]]:
        """查询当前范围内的学习路径记录。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM learning_steps WHERE task_id=? ORDER BY sort_order",
                (task_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def replace(self, task_id: str, steps: list[dict[str, Any]]) -> None:
        """替换当前范围内的学习路径记录。"""
        now = now_iso()
        status_map = {
            "done": "done",
            "current": "current",
            "todo": "todo",
            "pending": "todo",
            "next": "todo",
        }
        with get_conn() as conn:
            conn.execute("DELETE FROM learning_steps WHERE task_id=?", (task_id,))
            for index, step in enumerate(steps):
                status = status_map.get(str(step.get("status", "todo")), "todo")
                conn.execute(
                    """
                    INSERT INTO learning_steps(id,task_id,title,objective,resource,exercise,status,sort_order,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        step.get("id") or new_id("step"),
                        task_id,
                        step["title"],
                        step["objective"],
                        step["resource"],
                        step["exercise"],
                        status,
                        index,
                        now,
                        now,
                    ),
                )

    def attach_resource_to_current_step(
        self, task_id: str, resource_title: str
    ) -> None:
        """将资源关联到当前可执行的学习步骤。"""
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM learning_steps WHERE task_id=? AND status='current' ORDER BY sort_order LIMIT 1",
                (task_id,),
            ).fetchone()
            if not row:
                row = conn.execute(
                    "SELECT id FROM learning_steps WHERE task_id=? ORDER BY sort_order LIMIT 1",
                    (task_id,),
                ).fetchone()
            if row:
                conn.execute(
                    "UPDATE learning_steps SET resource=?, updated_at=? WHERE id=? AND task_id=?",
                    (resource_title, now_iso(), row["id"], task_id),
                )

    def mark_step_done(self, task_id: str, step_id: str) -> None:
        """将指定学习步骤更新为已完成。"""
        now = now_iso()
        with get_conn() as conn:
            row = conn.execute(
                "SELECT sort_order FROM learning_steps WHERE id=? AND task_id=?",
                (step_id, task_id),
            ).fetchone()
            if not row:
                return
            sort_order = int(row["sort_order"])
            conn.execute(
                "UPDATE learning_steps SET status='done', updated_at=? WHERE id=? AND task_id=?",
                (now, step_id, task_id),
            )
            next_row = conn.execute(
                """
                SELECT id FROM learning_steps
                WHERE task_id=? AND sort_order>? AND status!='done'
                ORDER BY sort_order LIMIT 1
                """,
                (task_id, sort_order),
            ).fetchone()
            if next_row:
                conn.execute(
                    "UPDATE learning_steps SET status='current', updated_at=? WHERE id=? AND task_id=?",
                    (now, next_row["id"], task_id),
                )
