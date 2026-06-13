from typing import Any

from app.agents.base import BaseAgent


class EvaluatorAgent(BaseAgent):
    name = "EvaluatorAgent"
    system_prompt = (
        "评估学习效果。输出掌握度、薄弱点、易错类型和下一步建议。只输出 JSON："
        '{"score":80,"mastery":"...","weak_points":["..."],"mistake_types":["..."],"effort":"...","next_suggestion":"..."}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        output = self.run_llm(payload, task_id)
        if output and "score" in output:
            return output
        answers = payload.get("answers") or []
        base = 68 + min(17, len(answers) * 4)
        task_title = str(payload.get("task_title", "当前任务"))
        return {
            "score": base,
            "mastery": "已完成一次学习反馈分析，基础可以继续推进，但关键步骤仍需练习巩固。",
            "weak_points": ["概念边界", "方法选择"],
            "mistake_types": ["条件判断不完整", "步骤遗漏"],
            "effort": f"本次提交 {len(answers)} 条作答记录。",
            "next_suggestion": f"围绕“{task_title}”完成一组专项练习，再复盘错因。",
        }
