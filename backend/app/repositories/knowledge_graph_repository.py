from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import dumps, get_conn, row_to_dict


class KnowledgeGraphRepository:
    def create(
        self,
        task_id: str,
        title: str,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        stats: dict[str, Any],
    ) -> str:
        """创建并持久化知识图谱记录。"""
        graph_id = new_id("kg")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO knowledge_graphs(id,task_id,title,nodes,edges,source_stats,created_at) VALUES(?,?,?,?,?,?,?)",
                (
                    graph_id,
                    task_id,
                    title,
                    dumps(nodes),
                    dumps(edges),
                    dumps(stats),
                    now_iso(),
                ),
            )
        return graph_id

    def latest(self, task_id: str) -> dict[str, Any] | None:
        """查询最新的知识图谱记录。"""
        with get_conn() as conn:
            return row_to_dict(
                conn.execute(
                    "SELECT * FROM knowledge_graphs WHERE task_id=? ORDER BY created_at DESC LIMIT 1",
                    (task_id,),
                ).fetchone()
            )
