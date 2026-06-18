from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import get_conn


class ConversationRepository:
    def ensure(self, task_id: str) -> str:
        """确保基础会话记录存在。"""
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM conversations WHERE task_id=?", (task_id,)
            ).fetchone()
            if row:
                return str(row["id"])
            conv_id = new_id("conv")
            now = now_iso()
            conn.execute(
                "INSERT INTO conversations(id,task_id,summary,created_at,updated_at) VALUES(?,?,?,?,?)",
                (conv_id, task_id, "", now, now),
            )
            return conv_id

    def add_message(self, task_id: str, role: str, content: str) -> str:
        """新增一条会话消息。"""
        conv_id = self.ensure(task_id)
        message_id = new_id("msg")
        now = now_iso()
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO messages(id,conversation_id,task_id,role,content,created_at) VALUES(?,?,?,?,?,?)",
                (message_id, conv_id, task_id, role, content, now),
            )
            conn.execute(
                "UPDATE conversations SET updated_at=? WHERE id=?", (now, conv_id)
            )
        return message_id

    def list_messages(self, task_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """查询会话中的全部消息。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE task_id=? ORDER BY created_at DESC LIMIT ?",
                (task_id, limit),
            ).fetchall()
            return [dict(row) for row in reversed(rows)]

    def summary(self, task_id: str) -> str:
        """读取会话摘要。"""
        with get_conn() as conn:
            row = conn.execute(
                "SELECT summary FROM conversations WHERE task_id=?", (task_id,)
            ).fetchone()
            return str(row["summary"]) if row else ""

    def update_summary(self, task_id: str, summary: str) -> None:
        """更新会话摘要。"""
        self.ensure(task_id)
        with get_conn() as conn:
            conn.execute(
                "UPDATE conversations SET summary=?, updated_at=? WHERE task_id=?",
                (summary, now_iso(), task_id),
            )
