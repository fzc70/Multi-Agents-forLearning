from __future__ import annotations

from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import dumps, get_conn


class AgentRunRepository:
    def add(
        self,
        agent_name: str,
        model: str,
        prompt_version: str,
        input_json: dict[str, Any],
        output_json: dict[str, Any] | None = None,
        error: str | None = None,
        latency_ms: int = 0,
        task_id: str | None = None,
        workflow_run_id: str | None = None,
    ) -> str:
        """新增一条智能体运行日志记录。"""
        run_id = new_id("run")
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO agent_run_logs(id,task_id,workflow_run_id,agent_name,model,prompt_version,input_json,output_json,error,latency_ms,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    run_id,
                    task_id,
                    workflow_run_id,
                    agent_name,
                    model,
                    prompt_version,
                    dumps(input_json),
                    dumps(output_json) if output_json is not None else None,
                    error,
                    latency_ms,
                    now_iso(),
                ),
            )
        return run_id

    def list(self, task_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """查询当前范围内的智能体运行日志记录。"""
        with get_conn() as conn:
            if task_id:
                rows = conn.execute(
                    "SELECT * FROM agent_run_logs WHERE task_id=? ORDER BY created_at DESC LIMIT ?",
                    (task_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM agent_run_logs ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]
