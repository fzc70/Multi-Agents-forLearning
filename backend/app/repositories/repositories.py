from __future__ import annotations

import json
from typing import Any

from app.core.ids import new_id
from app.core.time import now_iso
from app.storage.database import dumps, get_conn, loads, row_to_dict


def _label_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


class TaskRepository:
    def list(self) -> list[dict[str, Any]]:
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM learning_tasks ORDER BY updated_at DESC").fetchall()
            return [dict(row) for row in rows]

    def get(self, task_id: str) -> dict[str, Any] | None:
        with get_conn() as conn:
            return row_to_dict(conn.execute("SELECT * FROM learning_tasks WHERE id=?", (task_id,)).fetchone())

    def create(self, title: str, foundation: str | None, expected_outcome: str | None) -> str:
        task_id = new_id("task")
        now = now_iso()
        profile_tags = ["新任务", "画像待完善", foundation or "基础待了解", expected_outcome or "目标待细化"]
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
                    f"当前基础：{foundation}" if foundation else "建议先用对话补充目标、基础和学习偏好。",
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
        fields["updated_at"] = now_iso()
        keys = list(fields.keys())
        values = [dumps(v) if isinstance(v, (list, dict)) else v for v in fields.values()]
        values.append(task_id)
        sql = f"UPDATE learning_tasks SET {','.join(f'{key}=?' for key in keys)} WHERE id=?"
        with get_conn() as conn:
            conn.execute(sql, values)


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

    def ensure_default(self, task_id: str, title: str, foundation: str | None = None, goal: str | None = None) -> None:
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
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM profile_dimensions WHERE task_id=? ORDER BY rowid", (task_id,)).fetchall()
            return [dict(row) for row in rows]

    def update_dimension(self, task_id: str, dimension_id: str, value: str, evidence: str, confidence_delta: int = 5) -> None:
        now = now_iso()
        with get_conn() as conn:
            row = conn.execute(
                "SELECT confidence FROM profile_dimensions WHERE task_id=? AND id=?", (task_id, dimension_id)
            ).fetchone()
            if row:
                confidence = min(95, int(row["confidence"]) + confidence_delta)
                conn.execute(
                    "UPDATE profile_dimensions SET value=?, evidence=?, confidence=?, updated_at=? WHERE task_id=? AND id=?",
                    (value, evidence, confidence, now, task_id, dimension_id),
                )


class MaterialRepository:
    def list(self, task_id: str) -> list[dict[str, Any]]:
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM materials WHERE task_id=? ORDER BY updated_at DESC", (task_id,)).fetchall()
            return [dict(row) for row in rows]

    def get(self, material_id: str, task_id: str | None = None) -> dict[str, Any] | None:
        with get_conn() as conn:
            if task_id:
                return row_to_dict(
                    conn.execute("SELECT * FROM materials WHERE id=? AND task_id=?", (material_id, task_id)).fetchone()
                )
            return row_to_dict(conn.execute("SELECT * FROM materials WHERE id=?", (material_id,)).fetchone())

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
                    _label_size(size),
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
                    _label_size(size),
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
        with get_conn() as conn:
            conn.execute("DELETE FROM materials WHERE id=? AND task_id=?", (material_id, task_id))

    def add_chunks(self, task_id: str, material_id: str, chunks: list[dict[str, Any]]) -> None:
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


class ConversationRepository:
    def ensure(self, task_id: str) -> str:
        with get_conn() as conn:
            row = conn.execute("SELECT id FROM conversations WHERE task_id=?", (task_id,)).fetchone()
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
        conv_id = self.ensure(task_id)
        message_id = new_id("msg")
        now = now_iso()
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO messages(id,conversation_id,task_id,role,content,created_at) VALUES(?,?,?,?,?,?)",
                (message_id, conv_id, task_id, role, content, now),
            )
            conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conv_id))
        return message_id

    def list_messages(self, task_id: str, limit: int = 50) -> list[dict[str, Any]]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE task_id=? ORDER BY created_at DESC LIMIT ?", (task_id, limit)
            ).fetchall()
            return [dict(row) for row in reversed(rows)]

    def summary(self, task_id: str) -> str:
        with get_conn() as conn:
            row = conn.execute("SELECT summary FROM conversations WHERE task_id=?", (task_id,)).fetchone()
            return str(row["summary"]) if row else ""

    def update_summary(self, task_id: str, summary: str) -> None:
        self.ensure(task_id)
        with get_conn() as conn:
            conn.execute("UPDATE conversations SET summary=?, updated_at=? WHERE task_id=?", (summary, now_iso(), task_id))


class MemoryRepository:
    def add(self, task_id: str, type_: str, content: str, evidence: str, importance: int = 50) -> str:
        item_id = new_id("mem")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO memory_records(id,task_id,type,content,evidence,importance,created_at) VALUES(?,?,?,?,?,?,?)",
                (item_id, task_id, type_, content, evidence, importance, now_iso()),
            )
        return item_id

    def list(self, task_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM memory_records WHERE task_id=? ORDER BY importance DESC, created_at DESC LIMIT ?",
                (task_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]


class ResourceRepository:
    def list(self, task_id: str) -> list[dict[str, Any]]:
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM learning_resources WHERE task_id=? ORDER BY created_at DESC", (task_id,)).fetchall()
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
        with get_conn() as conn:
            return row_to_dict(
                conn.execute("SELECT * FROM learning_resources WHERE id=? AND task_id=?", (resource_id, task_id)).fetchone()
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
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE learning_resources
                SET content=?, detail_json=?, description=?, recommendation_reason=?, updated_at=?
                WHERE id=? AND task_id=?
                """,
                (content, dumps(detail), description, recommendation_reason, now_iso(), resource_id, task_id),
            )


class LearningPathRepository:
    def ensure_default(self, task_id: str, title: str) -> None:
        if self.list(task_id):
            return
        defaults = [
            ("明确学习目标", "把目标拆成可执行的小步骤。", "对话澄清", "回答 3 个目标问题", "current"),
            ("评估当前基础", "了解已经掌握什么、卡在哪里。", "小测评", "完成一次基础测评", "todo"),
            ("生成学习资源", "围绕当前薄弱点生成资料和练习。", "个性化资源", "完成第一组练习", "todo"),
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
        with get_conn() as conn:
            rows = conn.execute("SELECT * FROM learning_steps WHERE task_id=? ORDER BY sort_order", (task_id,)).fetchall()
            return [dict(row) for row in rows]

    def replace(self, task_id: str, steps: list[dict[str, Any]]) -> None:
        now = now_iso()
        status_map = {"done": "done", "current": "current", "todo": "todo", "pending": "todo", "next": "todo"}
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

    def attach_resource_to_current_step(self, task_id: str, resource_title: str) -> None:
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

class AssessmentRepository:
    def ensure_default(self, task_id: str) -> None:
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
        with get_conn() as conn:
            return row_to_dict(conn.execute("SELECT * FROM assessment_results WHERE task_id=?", (task_id,)).fetchone())

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
        self.ensure_default(task_id)
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE assessment_results
                SET score=?,mastery=?,weak_points=?,mistake_types=?,effort=?,next_suggestion=?,tested=1,updated_at=?
                WHERE task_id=?
                """,
                (score, mastery, dumps(weak_points), dumps(mistake_types), effort, next_suggestion, now_iso(), task_id),
            )


class KnowledgeGraphRepository:
    def create(self, task_id: str, title: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], stats: dict[str, Any]) -> str:
        graph_id = new_id("kg")
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO knowledge_graphs(id,task_id,title,nodes,edges,source_stats,created_at) VALUES(?,?,?,?,?,?,?)",
                (graph_id, task_id, title, dumps(nodes), dumps(edges), dumps(stats), now_iso()),
            )
        return graph_id

    def latest(self, task_id: str) -> dict[str, Any] | None:
        with get_conn() as conn:
            return row_to_dict(
                conn.execute("SELECT * FROM knowledge_graphs WHERE task_id=? ORDER BY created_at DESC LIMIT 1", (task_id,)).fetchone()
            )


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
        with get_conn() as conn:
            if task_id:
                rows = conn.execute(
                    "SELECT * FROM agent_run_logs WHERE task_id=? ORDER BY created_at DESC LIMIT ?", (task_id, limit)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM agent_run_logs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]


def decode_json_columns(row: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    copy = dict(row)
    for column in columns:
        copy[column] = loads(copy.get(column), [])
    return copy
