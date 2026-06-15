from typing import Any

from app.agents.base import BaseAgent
from app.domain.learning_rules import clean_meaningful_values


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
        task_title = str(payload.get("task_title", "当前任务"))
        score = self._score_from_answers(answers)
        weak_points = self._extract_values(answers, ("weak_point", "weakness", "knowledge_point", "topic"))
        mistake_types = self._extract_values(answers, ("mistake_type", "error_type", "reason"))
        if not weak_points and score < 75:
            weak_points = ["需要补充作答依据"]
        if not mistake_types and score < 75:
            mistake_types = ["答案证据不足或步骤不完整"]
        mastery = self._mastery_text(score, len(answers))
        suggestion = (
            f"围绕“{task_title}”复盘低分题并补充依据。"
            if score < 80
            else f"围绕“{task_title}”完成迁移练习，检查能否稳定输出。"
        )
        return {
            "score": score,
            "mastery": mastery,
            "weak_points": weak_points,
            "mistake_types": mistake_types,
            "effort": f"本次提交 {len(answers)} 条作答记录。",
            "next_suggestion": suggestion,
        }

    @staticmethod
    def _score_from_answers(answers: list[dict[str, Any]]) -> int:
        if not answers:
            return 0
        explicit_scores = []
        correctness = []
        completeness = []
        for item in answers:
            if "score" in item:
                try:
                    explicit_scores.append(float(item["score"]))
                except (TypeError, ValueError):
                    pass
            if "correct" in item:
                correctness.append(1 if item.get("correct") else 0)
            text = str(item.get("answer") or item.get("content") or item.get("student_answer") or "")
            completeness.append(min(1.0, len(text.strip()) / 80))
        if explicit_scores:
            average = sum(explicit_scores) / len(explicit_scores)
            return round(average if average <= 100 else min(100, average))
        if correctness:
            return round(sum(correctness) / len(correctness) * 100)
        return round(sum(completeness) / len(completeness) * 72)

    @staticmethod
    def _extract_values(answers: list[dict[str, Any]], keys: tuple[str, ...]) -> list[str]:
        values = []
        for item in answers:
            for key in keys:
                value = item.get(key)
                if isinstance(value, list):
                    values.extend(value)
                elif value:
                    values.append(value)
        return clean_meaningful_values(values)[:5]

    @staticmethod
    def _mastery_text(score: int, answer_count: int) -> str:
        if answer_count == 0:
            return "暂无有效作答记录，无法形成可靠评估。"
        if score >= 85:
            return "最近作答表现较稳定，可以进入迁移练习或下一阶段。"
        if score >= 70:
            return "基础理解已有支撑，但仍需要通过错题复盘稳定步骤。"
        return "当前掌握不稳定，应先回到讲解和例题，再做针对练习。"
