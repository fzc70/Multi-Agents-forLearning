from typing import Any

from app.agents.base import BaseAgent


class ResourceAgent(BaseAgent):
    name = "ResourceAgent"
    system_prompt = (
        "生成个性化学习资源。必须结合任务、画像、资料片段和下一步目标。输出 JSON："
        '{"resources":[{"type":"讲解文档","title":"...","description":"...","content":"...","recommendation_reason":"..."}]}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        output = self.run_llm(payload, task_id)
        if output and isinstance(output.get("resources"), list) and output["resources"]:
            return output
        task_title = str(payload.get("task_title", "学习任务"))
        next_action = str(payload.get("next_action", "当前重点"))
        contexts = payload.get("retrieved_contexts") or []
        source_hint = str(contexts[0].get("content", ""))[:180] if contexts else "暂无资料片段，按当前任务画像生成。"
        types = payload.get("types") or ["讲解文档"]
        resources = []
        for type_ in types:
            resources.append(
                {
                    "type": type_,
                    "title": f"{task_title} · {type_}",
                    "description": f"围绕“{next_action}”生成，包含讲解、示例和练习安排。",
                    "content": (
                        f"## {task_title}\n\n"
                        f"当前目标：{next_action}\n\n"
                        f"参考依据：{source_hint}\n\n"
                        "学习安排：\n1. 先理解核心概念。\n2. 结合例子完成一次迁移。\n3. 用小练习验证掌握情况。\n4. 复盘错因并更新下一步。"
                    ),
                    "recommendation_reason": f"当前下一步是“{next_action}”，该资源能直接支持本阶段学习。",
                }
            )
        return {"resources": resources}
