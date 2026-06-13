from typing import Any

from app.agents.base import BaseAgent


class ProfileAgent(BaseAgent):
    name = "ProfileAgent"
    system_prompt = (
        "从对话、练习和行为证据中更新学生画像。只输出 JSON："
        '{"updates":[{"dimension_id":"foundation|goal|style|weakness|preference|history|exercise","value":"...","evidence":"..."}]}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        output = self.run_llm(payload, task_id)
        if output and isinstance(output.get("updates"), list):
            return output
        message = str(payload.get("message", ""))
        updates: list[dict[str, str]] = []
        if any(word in message for word in ["不会", "不懂", "困难", "卡", "错"]):
            updates.append({"dimension_id": "weakness", "value": message[:80], "evidence": f"来自对话：{message[:60]}"})
        if any(word in message for word in ["喜欢", "希望", "想要", "目标"]):
            updates.append({"dimension_id": "goal", "value": message[:80], "evidence": f"来自对话：{message[:60]}"})
        if any(word in message for word in ["例子", "代码", "视频", "图", "练习"]):
            updates.append({"dimension_id": "preference", "value": message[:80], "evidence": f"来自对话：{message[:60]}"})
        if not updates:
            updates.append({"dimension_id": "style", "value": "偏好分步骤引导", "evidence": f"来自对话：{message[:60]}"})
        return {"updates": updates[:3]}
