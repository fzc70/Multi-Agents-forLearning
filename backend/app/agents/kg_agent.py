import re
from typing import Any

from app.agents.base import BaseAgent
from app.domain.learning_rules import KG_MINIMAL_NODES, KG_STOP_WORDS


class KGAgent(BaseAgent):
    name = "KGAgent"
    system_prompt = (
        "从学习资料和会话摘要中抽取知识图谱。节点必须是概念、方法、条件、例子或能力点。输出 JSON："
        '{"nodes":[{"id":"n1","label":"概念","type":"concept"}],"edges":[{"source":"n1","target":"n2","label":"关联"}]}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        """从学习上下文中抽取实体与关系。"""
        output = self.run_llm(payload, task_id)
        if output and isinstance(output.get("nodes"), list):
            return output
        text = str(payload.get("text", ""))
        words = re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9_]{2,}", text)
        seen: list[str] = []
        for word in words:
            if word not in KG_STOP_WORDS and word not in seen and len(seen) < 16:
                seen.append(word)
        if len(seen) < 2:
            seen = list(KG_MINIMAL_NODES)
        nodes = [
            {"id": f"n{i + 1}", "label": word, "type": "concept"}
            for i, word in enumerate(seen)
        ]
        edges = [
            {"source": nodes[i]["id"], "target": nodes[i + 1]["id"], "label": "关联"}
            for i in range(min(len(nodes) - 1, 14))
        ]
        return {"nodes": nodes, "edges": edges}
