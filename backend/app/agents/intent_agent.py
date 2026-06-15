from typing import Any

from app.agents.base import BaseAgent
from app.domain.learning_rules import infer_intent


class IntentAgent(BaseAgent):
    name = "IntentAgent"
    system_prompt = (
        "识别学生消息意图。输出 JSON："
        '{"intent":"tutoring|generate_resource|plan|assessment|profile_update","need_retrieval":true,"confidence":0-100}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        output = self.run_llm(payload, task_id)
        if output and "intent" in output:
            return output
        message = str(payload.get("message", ""))
        return infer_intent(message)
