from typing import Any

from app.agents.base import BaseAgent


class GradingAgent(BaseAgent):
    name = "GradingAgent"
    system_prompt = (
        "你是学习练习批改智能体。根据题目、参考答案、学生答案和满分进行评分。"
        "评分要严格但允许等价表达。必须输出 JSON："
        '{"items":[{"id":"q1","score":8,"max_score":10,"correct":true,"analysis":"...","weak_point":"...","mistake_type":"..."}]}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        output = self.run_llm(payload, task_id)
        items = output.get("items") if output else None
        if isinstance(items, list) and items:
            return {"items": items}
        return {"items": [self._fallback_item(item) for item in payload.get("items", [])]}

    @staticmethod
    def _fallback_item(item: dict[str, Any]) -> dict[str, Any]:
        answer = str(item.get("answer", "")).strip()
        given = str(item.get("student_answer", "")).strip()
        max_score = int(item.get("max_score", 20))
        stem = str(item.get("stem") or "本题")
        overlap = len(set(answer) & set(given))
        base = 0
        if given:
            base = max_score * 0.55
        if answer and given and (answer in given or given in answer):
            base = max_score * 0.9
        elif overlap >= max(4, len(set(answer)) // 4):
            base = max(base, max_score * 0.7)
        score = round(min(max_score, base))
        return {
            "id": str(item.get("id")),
            "score": score,
            "max_score": max_score,
            "correct": score >= max_score * 0.75,
            "analysis": (
                f"回答与参考答案有一定相关性，但“{stem[:30]}”仍需要补充关键依据。"
                if score < max_score * 0.75
                else f"回答基本覆盖“{stem[:30]}”的主要要求。"
            ),
            "weak_point": f"{stem[:24]}：依据不足" if score < max_score * 0.75 else "",
            "mistake_type": "答案不完整或缺少推理依据" if score < max_score * 0.75 else "",
        }
