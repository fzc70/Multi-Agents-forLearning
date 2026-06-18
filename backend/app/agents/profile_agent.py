from typing import Any

from app.agents.base import BaseAgent
from app.domain.learning_rules import PROFILE_RULES, evidence_text, match_rules


class ProfileAgent(BaseAgent):
    name = "ProfileAgent"
    system_prompt = (
        "从对话、练习和行为证据中更新学生画像。只输出 JSON："
        '{"updates":[{"dimension_id":"foundation|goal|style|weakness|preference|history|exercise","value":"...","evidence":"..."}]}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        """从有效证据中更新学生画像。"""
        output = self.run_llm(payload, task_id)
        if output and isinstance(output.get("updates"), list):
            return output
        message = str(payload.get("message", ""))
        updates = [
            {
                "dimension_id": rule.dimension_id,
                "value": message[:120],
                "evidence": evidence_text(rule.evidence_label, message),
            }
            for rule in match_rules(message, PROFILE_RULES)
        ]
        # 没有明确证据时不写画像，避免把普通聊天误判成学习偏好。
        return {"updates": updates[:3]}
