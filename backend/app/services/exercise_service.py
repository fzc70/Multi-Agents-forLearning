from __future__ import annotations

from typing import Any

from app.agents.grading_agent import GradingAgent
from app.core.errors import bad_request, not_found
from app.domain.constants import RESOURCE_TYPE_EXERCISE
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.exercise_attempt_repository import ExerciseAttemptRepository
from app.repositories.memory_repository import MemoryRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.resource_mastery_repository import ResourceMasteryRepository
from app.repositories.resource_repository import ResourceRepository
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService
from app.storage.database import loads
from app.tools.resource_quality import ResourceQualityGate


class ExerciseService:
    """练习作答服务。

    选择题本地判分，简答/应用题交给 GradingAgent 按满分和评分规则判分。
    判分结果会写入练习记忆、画像薄弱点和动态评估。
    """

    def __init__(self) -> None:
        """初始化 ExerciseService 所需的依赖。"""
        self.tasks = TaskService()
        self.resources = ResourceRepository()
        self.attempts = ExerciseAttemptRepository()
        self.mastery = ResourceMasteryRepository()

    def submit(
        self, task_id: str, resource_id: str, answers: dict[str, Any]
    ) -> dict[str, Any]:
        """批改练习、记录证据并更新学习状态。"""
        resource = self._get_exercise(task_id, resource_id)
        questions = resource.get("detail", {}).get("questions", [])
        total = max(len(questions), 1)
        per_question_score = round(100 / total)

        results, short_items = self._grade_choice_questions(
            questions, answers, per_question_score
        )
        results.extend(self._grade_short_questions(resource, short_items, task_id))
        results.sort(key=lambda item: str(item["id"]))

        score = max(
            0, min(100, round(sum(int(item.get("score", 0)) for item in results)))
        )
        weak_points = self._meaningful_values(
            item.get("weak_point") for item in results
        )
        mistake_types = self._meaningful_values(
            item.get("mistake_type") for item in results
        )

        detail = {
            "items": results,
            "answers": answers,
            "resource_type": resource["type"],
        }
        self.attempts.add(task_id, resource_id, resource["title"], score, detail)
        self._record_exercise_feedback(
            task_id, resource["title"], score, weak_points, mistake_types
        )

        assessment_score = self.dynamic_score(task_id)
        next_suggestion = (
            "先复盘错题解析，再生成一组同类型练习。"
            if score < 80
            else "可以确认本资源掌握度，或进入下一阶段。"
        )
        AssessmentRepository().update(
            task_id,
            assessment_score,
            f"综合最近练习、资源掌握和路径进度，当前掌握度为 {assessment_score}。",
            list(dict.fromkeys(weak_points))[:5],
            list(dict.fromkeys(mistake_types))[:5],
            f"最近完成资源「{resource['title']}」练习，得分 {score}",
            next_suggestion,
        )
        TaskRepository().touch(
            task_id,
            next_action=next_suggestion,
            reason="根据最近练习结果和历史表现更新。",
        )
        return {
            "task": self.tasks.get_task(task_id),
            "result": {
                "score": score,
                "assessment_score": assessment_score,
                "correct_count": len([item for item in results if item["correct"]]),
                "total": total,
                "items": results,
                "summary": next_suggestion,
            },
        }

    def dynamic_score(self, task_id: str) -> int:
        """越近的练习权重越高，练习分数优先于资源自评和路径进度。"""

        attempts = self.attempts.list_recent(task_id, limit=10)
        mastery_items = self.mastery.list_recent(task_id, limit=10)
        exercise_score = 0
        if attempts:
            weights = [1 / (index + 1) for index, _ in enumerate(attempts)]
            exercise_score = round(
                sum(
                    int(item["score"]) * weights[index]
                    for index, item in enumerate(attempts)
                )
                / sum(weights)
            )
        mastery_score = (
            round(
                sum(int(item["mastery"]) for item in mastery_items) / len(mastery_items)
            )
            if mastery_items
            else exercise_score
        )
        path = self.tasks.get_task(task_id).get("path", [])
        path_score = round(
            len([step for step in path if step["status"] == "done"])
            / max(len(path), 1)
            * 100
        )
        if attempts:
            return round(exercise_score * 0.7 + mastery_score * 0.2 + path_score * 0.1)
        if mastery_items:
            return round(mastery_score * 0.75 + path_score * 0.25)
        return path_score

    def _get_exercise(self, task_id: str, resource_id: str) -> dict[str, Any]:
        """读取并校验资源中的练习内容。"""
        task = self.tasks.get_task(task_id)
        resource = self.resources.get(resource_id, task_id)
        if not resource:
            raise not_found("学习资源不存在")
        normalized = ResourceQualityGate().normalize(
            {
                "type": resource["type"],
                "title": resource["title"],
                "description": resource["description"],
                "content": resource["content"],
                "detail": loads(resource.get("detail_json"), {}),
                "recommendation_reason": resource["recommendation_reason"],
            },
            task["title"],
            task["next_action"],
        )
        if normalized["type"] != RESOURCE_TYPE_EXERCISE:
            raise bad_request("该资源不是练习题")
        return {
            "id": resource["id"],
            **normalized,
            "source_refs": loads(resource["source_refs"], []),
            "created_at": resource.get("created_at"),
        }

    def _grade_choice_questions(
        self,
        questions: list[dict[str, Any]],
        answers: dict[str, Any],
        per_question_score: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """使用确定性规则批改选择题。"""
        results: list[dict[str, Any]] = []
        short_items: list[dict[str, Any]] = []
        for question in questions:
            qid = str(question.get("id"))
            expected = str(question.get("answer", "")).strip()
            given = str(answers.get(qid, "")).strip()
            if str(question.get("type", "short_answer")) == "single_choice":
                correct = given.upper() == expected.upper()
                results.append(
                    {
                        "id": qid,
                        "correct": correct,
                        "score": per_question_score if correct else 0,
                        "max_score": per_question_score,
                        "answer": expected,
                        "given": given,
                        "analysis": question.get(
                            "analysis", "请对照答案复盘关键步骤。"
                        ),
                        "weak_point": "" if correct else "概念判断",
                        "mistake_type": "" if correct else "选择判断错误",
                    }
                )
                continue
            short_items.append(
                {
                    "id": qid,
                    "stem": question.get("stem", ""),
                    "answer": expected,
                    "student_answer": given,
                    "max_score": per_question_score,
                    "analysis_reference": question.get("analysis", ""),
                }
            )
        return results, short_items

    def _grade_short_questions(
        self, resource: dict[str, Any], short_items: list[dict[str, Any]], task_id: str
    ) -> list[dict[str, Any]]:
        """调用评分智能体批改主观题。"""
        if not short_items:
            return []
        graded = GradingAgent().run(
            {
                "task_title": resource["title"],
                "resource_title": resource["title"],
                "items": short_items,
                "grading_rules": [
                    "必须按满分给出 0 到 max_score 的整数分",
                    "看是否覆盖关键概念、推理步骤、依据表达",
                    "空答案必须 0 分",
                    "允许等价表达，不要求逐字一致",
                ],
            },
            task_id,
        )
        by_id = {str(item.get("id")): item for item in graded.get("items", [])}
        results = []
        for item in short_items:
            graded_item = by_id.get(str(item["id"]), {})
            earned = max(
                0, min(int(item["max_score"]), int(graded_item.get("score", 0)))
            )
            results.append(
                {
                    "id": item["id"],
                    "correct": bool(
                        graded_item.get(
                            "correct", earned >= int(item["max_score"]) * 0.75
                        )
                    ),
                    "score": earned,
                    "max_score": item["max_score"],
                    "answer": item["answer"],
                    "given": item["student_answer"],
                    "analysis": str(
                        graded_item.get("analysis")
                        or item.get("analysis_reference")
                        or "请对照参考答案补充关键步骤。"
                    ),
                    "weak_point": str(
                        graded_item.get("weak_point")
                        or (
                            "步骤表达" if earned < int(item["max_score"]) * 0.75 else ""
                        )
                    ),
                    "mistake_type": str(
                        graded_item.get("mistake_type")
                        or (
                            "答案不完整"
                            if earned < int(item["max_score"]) * 0.75
                            else ""
                        )
                    ),
                }
            )
        return results

    @staticmethod
    def _meaningful_values(values: Any) -> list[str]:
        """提取非空且去重的反馈值。"""
        empty_words = {
            "无",
            "暂无",
            "没有",
            "无明显",
            "暂无明显",
            "none",
            "null",
            "n/a",
        }
        cleaned = []
        for value in values:
            text = str(value or "").strip()
            if (
                not text
                or text.lower() in empty_words
                or text.startswith(("无明显", "暂无明显"))
            ):
                continue
            cleaned.append(text)
        return list(dict.fromkeys(cleaned))

    @staticmethod
    def _record_exercise_feedback(
        task_id: str,
        resource_title: str,
        score: int,
        weak_points: list[str],
        mistake_types: list[str],
    ) -> None:
        """记录作答反馈并更新画像证据。"""
        MemoryRepository().add(
            task_id,
            "exercise",
            f"完成练习「{resource_title}」，得分 {score}，薄弱点：{'、'.join(weak_points[:3]) or '本次未记录明确薄弱点'}",
            f"来自资源练习：{resource_title}",
            82,
        )
        if weak_points:
            ProfileRepository().update_dimension(
                task_id,
                "weakness",
                "；".join(weak_points[:4]),
                f"来自练习「{resource_title}」",
            )
        ProfileRepository().update_dimension(
            task_id, "exercise", f"最近练习 {score} 分", f"来自练习「{resource_title}」"
        )
