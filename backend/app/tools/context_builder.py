from __future__ import annotations

from typing import Any

from app.repositories import ConversationRepository, MemoryRepository, ProfileRepository
from app.tools.retrieval_tool import RetrievalTool


class ContextBuilder:
    """统一控制上下文来源、长度和优先级，避免在工作流里散落拼接逻辑。"""

    def __init__(self) -> None:
        self.retrieval = RetrievalTool()
        self.profile = ProfileRepository()
        self.memory = MemoryRepository()
        self.conversation = ConversationRepository()

    def build_for_task(self, task: dict[str, Any], query: str, top_k: int = 6) -> dict[str, Any]:
        task_id = task["id"]
        profile_items = self.profile.list_dimensions(task_id)
        memories = self.memory.list(task_id, limit=8)
        messages = self.conversation.list_messages(task_id, limit=8)
        anchors = [
            task.get("title", ""),
            task.get("next_action", ""),
            " ".join(str(item.get("value", "")) for item in profile_items),
            " ".join(str(item.get("content", "")) for item in memories[:3]),
        ]
        retrieved = self.retrieval.search(task_id, query, top_k=top_k, anchors=anchors)
        return {
            "task": {
                "id": task_id,
                "title": task.get("title"),
                "next_action": task.get("next_action"),
                "reason": task.get("reason"),
            },
            "profile": profile_items,
            "memory": memories,
            "recent_messages": messages,
            "retrieved_contexts": self._trim_contexts(retrieved),
            "source_refs": [item["source_ref"] for item in retrieved if item.get("source_ref")],
        }

    @staticmethod
    def _trim_contexts(contexts: list[dict[str, Any]], max_chars: int = 4200) -> list[dict[str, Any]]:
        total = 0
        result: list[dict[str, Any]] = []
        for item in contexts:
            content = str(item.get("content", ""))
            if total + len(content) > max_chars:
                remain = max_chars - total
                if remain <= 160:
                    break
                item = {**item, "content": content[:remain]}
            result.append(item)
            total += len(str(item.get("content", "")))
            if total >= max_chars:
                break
        return result
