from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import dumps, get_conn, row_to_dict


class ResourceRepository:
    def list(self, task_id: str) -> list[dict[str, Any]]:
        """查询当前范围内的学习资源记录。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM learning_resources WHERE task_id=? ORDER BY created_at DESC",
                (task_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def create(
        self,
        task_id: str,
        type_: str,
        title: str,
        description: str,
        content: str,
        detail: dict[str, Any],
        recommendation_reason: str,
        source_refs: list[dict[str, Any]],
    ) -> str:
        """创建并持久化学习资源记录。"""
        resource_id = new_id("res")
        now = now_iso()
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO learning_resources(id,task_id,type,title,description,content,detail_json,recommendation_reason,source_refs,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    resource_id,
                    task_id,
                    type_,
                    title,
                    description,
                    content,
                    dumps(detail),
                    recommendation_reason,
                    dumps(source_refs),
                    now,
                    now,
                ),
            )
        return resource_id

    def get(self, resource_id: str, task_id: str) -> dict[str, Any] | None:
        """查询指定的学习资源记录。"""
        with get_conn() as conn:
            return row_to_dict(
                conn.execute(
                    "SELECT * FROM learning_resources WHERE id=? AND task_id=?",
                    (resource_id, task_id),
                ).fetchone()
            )

    def update_normalized(
        self,
        resource_id: str,
        task_id: str,
        content: str,
        detail: dict[str, Any],
        description: str,
        recommendation_reason: str,
    ) -> None:
        """更新规范化后的学习资源。"""
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE learning_resources
                SET content=?, detail_json=?, description=?, recommendation_reason=?, updated_at=?
                WHERE id=? AND task_id=?
                """,
                (
                    content,
                    dumps(detail),
                    description,
                    recommendation_reason,
                    now_iso(),
                    resource_id,
                    task_id,
                ),
            )
