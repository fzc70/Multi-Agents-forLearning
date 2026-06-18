from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.learning_path_repository import LearningPathRepository
from app.repositories.profile_repository import ProfileRepository
from app.storage.database import dumps, get_conn, row_to_dict


class TaskRepository:
    def list(self) -> list[dict[str, Any]]:
        """查询当前范围内的学习任务记录。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM learning_tasks ORDER BY updated_at DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def get(self, task_id: str) -> dict[str, Any] | None:
        """查询指定的学习任务记录。"""
        with get_conn() as conn:
            return row_to_dict(
                conn.execute(
                    "SELECT * FROM learning_tasks WHERE id=?", (task_id,)
                ).fetchone()
            )

    def create(
        self, title: str, foundation: str | None, expected_outcome: str | None
    ) -> str:
        """创建并持久化学习任务记录。"""
        task_id = new_id("task")
        now = now_iso()
        profile_tags = [
            "新任务",
            "画像待完善",
            foundation or "基础待了解",
            expected_outcome or "目标待细化",
        ]
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO learning_tasks(id,title,category,next_action,reason,profile_tags,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    task_id,
                    title,
                    "自定义",
                    expected_outcome or "先通过对话明确目标和当前基础",
                    (
                        f"当前基础：{foundation}"
                        if foundation
                        else "建议先用对话补充目标、基础和学习偏好。"
                    ),
                    dumps(profile_tags),
                    now,
                    now,
                ),
            )
        ProfileRepository().ensure_default(task_id, title, foundation, expected_outcome)
        ConversationRepository().ensure(task_id)
        LearningPathRepository().ensure_default(task_id, title)
        AssessmentRepository().ensure_default(task_id)
        ConversationRepository().add_message(
            task_id,
            "assistant",
            f"新任务已创建。你可以先告诉我：学习“{title}”的目标、当前基础和希望多久看到效果。",
        )
        return task_id

    def touch(self, task_id: str, **fields: Any) -> None:
        """更新学习任务的最后活动时间。"""
        fields["updated_at"] = now_iso()
        keys = list(fields.keys())
        values = [
            dumps(v) if isinstance(v, (list, dict)) else v for v in fields.values()
        ]
        values.append(task_id)
        sql = f"UPDATE learning_tasks SET {','.join(f'{key}=?' for key in keys)} WHERE id=?"
        with get_conn() as conn:
            conn.execute(sql, values)

    def delete(self, task_id: str) -> None:
        """删除指定的学习任务记录。"""
        with get_conn() as conn:
            conn.execute("DELETE FROM learning_tasks WHERE id=?", (task_id,))
