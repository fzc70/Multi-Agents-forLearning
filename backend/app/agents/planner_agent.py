from typing import Any

from app.agents.base import BaseAgent
from app.domain.constants import RESOURCE_TYPE_EXERCISE, RESOURCE_TYPE_LECTURE, RESOURCE_TYPE_MINDMAP
from app.domain.learning_rules import clean_meaningful_values


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"
    system_prompt = (
        "生成或调整学习路径。路径必须可执行、顺序清晰、每步含资源和练习。输出 JSON："
        '{"steps":[{"title":"...","objective":"...","resource":"...","exercise":"...","status":"current"}],"note":"..."}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        output = self.run_llm(payload, task_id)
        if output and isinstance(output.get("steps"), list) and output["steps"]:
            return output
        task_title = str(payload.get("task_title", "学习任务"))
        weak_points = clean_meaningful_values(payload.get("weak_points") or [])
        weak = "、".join(weak_points) if weak_points else "当前未稳定掌握的内容"
        return {
            "steps": [
                {
                    "title": f"澄清“{task_title}”关键概念",
                    "objective": f"先把“{task_title}”的核心概念和适用条件讲清楚。",
                    "resource": RESOURCE_TYPE_LECTURE,
                    "exercise": "完成 3 个概念判断题",
                    "status": "current",
                },
                {
                    "title": "专项训练薄弱点",
                    "objective": f"集中处理：{weak}",
                    "resource": RESOURCE_TYPE_EXERCISE,
                    "exercise": "完成一组针对性练习",
                    "status": "todo",
                },
                {
                    "title": "复盘与迁移",
                    "objective": "把方法迁移到新题或新场景。",
                    "resource": RESOURCE_TYPE_MINDMAP,
                    "exercise": "完成一次综合复盘",
                    "status": "todo",
                },
            ],
            "note": "已根据当前任务进度、薄弱点、资料和测评结果调整路径。",
        }
