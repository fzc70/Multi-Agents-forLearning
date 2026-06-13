from typing import Any

from app.agents.base import BaseAgent


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
        if any(word in message for word in ["生成", "资料", "资源", "练习"]):
            intent = "generate_resource"
        elif any(word in message for word in ["路径", "计划", "下一步"]):
            intent = "plan"
        elif any(word in message for word in ["测评", "测试", "掌握"]):
            intent = "assessment"
        else:
            intent = "tutoring"
        return {"intent": intent, "need_retrieval": True, "confidence": 72}
