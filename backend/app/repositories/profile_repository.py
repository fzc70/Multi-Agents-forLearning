from __future__ import annotations

from typing import Any

from app.core.time import now_iso
from app.storage.database import get_conn


class ProfileRepository:
    default_dimensions = [
        ("major", "专业/课程背景"),
        ("foundation", "知识基础"),
        ("goal", "学习目标"),
        ("style", "认知风格"),
        ("weakness", "薄弱点/易错点"),
        ("history", "学习历史"),
        ("preference", "资源偏好"),
        ("exercise", "练习表现"),
    ]

    def ensure_default(
        self,
        task_id: str,
        title: str,
        foundation: str | None = None,
        goal: str | None = None,
    ) -> None:
        """确保默认学生画像记录存在。"""
        if self.list_dimensions(task_id):
            return
        now = now_iso()
        values = {
            "foundation": foundation or "待了解",
            "goal": goal or title,
            "history": "新任务，暂无练习记录",
        }
        with get_conn() as conn:
            for key, label in self.default_dimensions:
                conn.execute(
                    """
                    INSERT INTO profile_dimensions(id,task_id,label,value,confidence,evidence,updated_at)
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        key,
                        task_id,
                        label,
                        values.get(key, "待通过对话和学习行为判断"),
                        58 if key in values else 30,
                        "来自任务创建" if key in values else "等待后续证据",
                        now,
                    ),
                )

    def list_dimensions(self, task_id: str) -> list[dict[str, Any]]:
        """查询学生画像的全部维度。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM profile_dimensions WHERE task_id=? ORDER BY rowid",
                (task_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def update_dimension(
        self,
        task_id: str,
        dimension_id: str,
        value: str,
        evidence: str,
        confidence_delta: int = 5,
    ) -> None:
        """更新画像维度及其证据。"""
        now = now_iso()
        with get_conn() as conn:
            row = conn.execute(
                "SELECT confidence FROM profile_dimensions WHERE task_id=? AND id=?",
                (task_id, dimension_id),
            ).fetchone()
            if row:
                confidence = min(95, int(row["confidence"]) + confidence_delta)
                conn.execute(
                    "UPDATE profile_dimensions SET value=?, evidence=?, confidence=?, updated_at=? WHERE task_id=? AND id=?",
                    (value, evidence, confidence, now, task_id, dimension_id),
                )
