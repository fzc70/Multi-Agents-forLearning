from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.repositories.common import label_size
from app.storage.database import dumps, get_conn, row_to_dict


class MaterialRepository:
    def list(self, task_id: str) -> list[dict[str, Any]]:
        """查询当前范围内的学习资料记录。"""
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM materials WHERE task_id=? ORDER BY updated_at DESC",
                (task_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def get(
        self, material_id: str, task_id: str | None = None
    ) -> dict[str, Any] | None:
        """查询指定的学习资料记录。"""
        with get_conn() as conn:
            if task_id:
                return row_to_dict(
                    conn.execute(
                        "SELECT * FROM materials WHERE id=? AND task_id=?",
                        (material_id, task_id),
                    ).fetchone()
                )
            return row_to_dict(
                conn.execute(
                    "SELECT * FROM materials WHERE id=?", (material_id,)
                ).fetchone()
            )

    def create(
        self,
        task_id: str,
        name: str,
        size: int,
        text_length: int,
        file_path: str,
        text_path: str,
        used_for: list[str] | None = None,
    ) -> str:
        """创建并持久化学习资料记录。"""
        material_id = new_id("mat")
        now = now_iso()
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO materials(id,task_id,name,type,size_label,status,text_length,used_for,file_path,text_path,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    material_id,
                    task_id,
                    name,
                    "PDF",
                    label_size(size),
                    "已解析",
                    text_length,
                    dumps(used_for or ["知识图谱", "答疑", "资源生成"]),
                    file_path,
                    text_path,
                    now,
                    now,
                ),
            )
        return material_id

    def insert_with_id(
        self,
        material_id: str,
        task_id: str,
        name: str,
        size: int,
        text_length: int,
        file_path: str,
        text_path: str,
    ) -> None:
        """使用指定标识新增学习资料。"""
        now = now_iso()
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO materials(id,task_id,name,type,size_label,status,text_length,used_for,file_path,text_path,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    material_id,
                    task_id,
                    name,
                    "PDF",
                    label_size(size),
                    "已解析",
                    text_length,
                    dumps(["知识图谱", "答疑", "资源生成"]),
                    file_path,
                    text_path,
                    now,
                    now,
                ),
            )

    def delete(self, material_id: str, task_id: str) -> None:
        """删除指定的学习资料记录。"""
        with get_conn() as conn:
            conn.execute(
                "DELETE FROM materials WHERE id=? AND task_id=?", (material_id, task_id)
            )

    def add_chunks(
        self, task_id: str, material_id: str, chunks: list[dict[str, Any]]
    ) -> None:
        """批量保存资料文本块。"""
        now = now_iso()
        with get_conn() as conn:
            for item in chunks:
                conn.execute(
                    """
                    INSERT INTO material_chunks(id,material_id,task_id,page,chunk_index,content,token_count,created_at)
                    VALUES(?,?,?,?,?,?,?,?)
                    """,
                    (
                        new_id("chunk"),
                        material_id,
                        task_id,
                        item.get("page"),
                        item["chunk_index"],
                        item["content"],
                        len(item["content"]),
                        now,
                    ),
                )

    def list_chunks(self, task_id: str) -> list[dict[str, Any]]:
        """查询任务下的资料文本块。"""
        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT c.*, m.name AS material_name
                FROM material_chunks c
                JOIN materials m ON m.id = c.material_id
                WHERE c.task_id=?
                ORDER BY c.material_id, c.chunk_index
                """,
                (task_id,),
            ).fetchall()
            return [dict(row) for row in rows]
