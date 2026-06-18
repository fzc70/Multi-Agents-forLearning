from typing import Any

from app.agents.base import BaseAgent
from app.domain.constants import RESOURCE_TYPE_LECTURE, RESOURCE_TYPES


class ResourceAgent(BaseAgent):
    name = "ResourceAgent"
    supported_types_text = "、".join(RESOURCE_TYPES)
    system_prompt = (
        "生成高质量、可直接使用的个性化学习资源，面向真实学生，不要只给摘要或预览。"
        "必须结合任务、画像、资料片段和下一步目标，内容要具体、可学习、可操作、可评估。"
        "如果上下文里有 recent_exercise_memory 或 memory，练习题必须避开已练过的题干和同构题。"
        f"只支持：{supported_types_text}。"
        "每个资源必须包含非空 detail 结构，严禁空数组、空对象、占位符。"
        "讲解文档 detail.sections 至少 6 节，每节必须包含 heading、body、steps、key_points、common_mistakes、example、self_check；"
        "其中 steps 必须是 4-6 条完整可执行步骤，不能只写摘要，不能空泛写“复述/举例/自检”，必须结合本节知识内容；"
        "练习题 detail.questions 至少 5 题，题干清楚，至少 2 道选择题和 2 道简答/应用题，每题含 answer、analysis、difficulty；"
        "思维导图必须是层级学习提纲：1 个中心主题、3-6 个一级分支、每个分支 2-4 个子点，nodes 要包含 level，edges 表示包含/展开/复盘顺序；"
        "知识图谱必须是实体关系网络：节点是概念、方法、条件、例题、误区、资源或证据，edges 的 label 必须是明确语义关系，如前置、包含、依赖、应用于、易混淆、证明；"
        "思维导图和知识图谱不能输出同一套节点关系。两者 detail.nodes 至少 8 个、edges 至少 7 条，节点 label 不得为空；"
        "拓展阅读 detail.readings 至少 5 条，每条说明阅读目标、推荐理由、预计时间；"
        "代码案例必须含 scenario、starter_code、tasks、reference_solution、tests、explanation。"
        "content 字段要是该资源正文摘要，不要与 detail 矛盾。"
        "输出 JSON："
        '{"resources":[{"type":"讲解文档","title":"...","description":"...","content":"...","detail":{},"recommendation_reason":"..."}]}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        """生成指定类型的结构化学习资源。"""
        output = self.run_llm(payload, task_id)
        if output and isinstance(output.get("resources"), list) and output["resources"]:
            return output
        task_title = str(payload.get("task_title", "学习任务"))
        next_action = str(payload.get("next_action", "当前重点"))
        contexts = payload.get("retrieved_contexts") or []
        source_hint = (
            str(contexts[0].get("content", ""))[:180]
            if contexts
            else "暂无资料片段，按当前任务画像生成。"
        )
        types = payload.get("types") or [RESOURCE_TYPE_LECTURE]
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
                    "detail": self._detail_for(
                        type_, task_title, next_action, source_hint
                    ),
                    "recommendation_reason": f"当前下一步是“{next_action}”，该资源能直接支持本阶段学习。",
                }
            )
        return {"resources": resources}

    def _detail_for(
        self, type_: str, task_title: str, next_action: str, source_hint: str
    ) -> dict[str, Any]:
        """生成指定资源类型的降级详情结构。"""
        from app.tools.resource_quality import ResourceQualityGate

        return ResourceQualityGate().default_detail(type_, task_title, next_action) | {
            "source_hint": source_hint
        }
