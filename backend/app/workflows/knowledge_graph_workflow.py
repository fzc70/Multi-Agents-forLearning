from __future__ import annotations

from typing import Any

from app.agents.kg_agent import KGAgent
from app.core.time import now_iso
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.tools.context_builder import ContextBuilder


class KnowledgeGraphWorkflow:
    """知识图谱工作流：合并资料片段和会话文本，抽取实体关系。"""

    def __init__(self) -> None:
        """初始化 KnowledgeGraphWorkflow 所需的依赖。"""
        self.agent = KGAgent()
        self.kg = KnowledgeGraphRepository()
        self.context_builder = ContextBuilder()
        self.conversation = ConversationRepository()

    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        """编排上下文构建、图谱抽取和持久化流程。"""
        task_id = task["id"]
        context = self.context_builder.build_for_task(task, task["title"], top_k=10)
        contexts = context.get("retrieved_contexts", [])
        messages = self.conversation.list_messages(task_id, limit=20)
        text = "\n".join(
            [item["content"] for item in contexts]
            + [item["content"] for item in messages]
        )
        if not text.strip():
            raise ValueError("请先上传学习资料或开始对话")
        output = self.agent.run(
            {"task_title": task["title"], "text": text[:12000]}, task_id
        )
        stats = {
            "material_chunks": len(contexts),
            "conversation_messages": len(messages),
            "node_count": len(output.get("nodes", [])),
            "edge_count": len(output.get("edges", [])),
        }
        created_at = now_iso()
        graph_id = self.kg.create(
            task_id,
            f"{task['title']} 知识图谱",
            output.get("nodes", []),
            output.get("edges", []),
            stats,
        )
        return {
            "id": graph_id,
            "task_id": task_id,
            "title": f"{task['title']} 知识图谱",
            **output,
            "source_stats": stats,
            "created_at": created_at,
        }
