from typing import Any

from app.agents.base import BaseAgent
from app.llm.adapter import LLMError, LLMNotConfigured


class TutorAgent(BaseAgent):
    name = "TutorAgent"
    system_prompt = (
        "你是个性化学习答疑智能体。必须优先使用 provided_context 中的资料和画像。"
        "当 source_refs 为空时，不得声称已经参考资料。只输出 JSON："
        '{"reply":"...","grounded":true,"source_refs":[{"type":"material_chunk","id":"...","page":1,"chunk_id":"..."}]}'
    )

    def run(self, payload: dict[str, Any], task_id: str) -> dict[str, Any]:
        """结合任务上下文生成个性化辅导回答。"""
        output = self.run_llm(payload, task_id)
        if output and "reply" in output:
            return output
        message = str(payload.get("message", ""))
        task_title = str(payload.get("task_title", "当前任务"))
        contexts = payload.get("retrieved_contexts") or []
        source_refs = [
            item.get("source_ref") for item in contexts if item.get("source_ref")
        ]
        if contexts:
            first = str(contexts[0].get("content", ""))[:160]
            reply = (
                f"我结合了你上传的资料。围绕“{task_title}”，可以先抓住这段依据：{first}...\n\n"
                f"针对你的问题“{message}”，建议按“概念-条件-例子-练习”四步推进。"
            )
        else:
            reply = (
                f"当前没有可引用的资料来源。围绕“{task_title}”，我先按你的学习记录给出建议："
                "先明确卡点，再做一个最小练习，完成后根据错因调整路径。"
            )
        return {"reply": reply, "grounded": bool(contexts), "source_refs": source_refs}

    def stream_reply(self, payload: dict[str, Any], task_id: str):
        """以流式方式生成个性化辅导回答。"""
        try:
            yielded = False
            for chunk in self.llm.stream_text(
                agent_name=self.name,
                prompt_version=f"{self.prompt_version}-stream",
                system_prompt=(
                    "你是个性化学习答疑智能体。结合当前任务、学习画像、资料片段和历史表现回答。"
                    "回答要直接、清晰、适合学生继续行动；没有资料依据时不要声称参考了资料。"
                ),
                user_payload=payload,
                task_id=task_id,
            ):
                yielded = True
                yield chunk
            if yielded:
                return
        except (LLMNotConfigured, LLMError) as exc:
            self.run_repo.add(
                agent_name=self.name,
                model=getattr(self.llm, "model", "unknown"),
                prompt_version=f"{self.prompt_version}-stream",
                input_json=payload,
                output_json={"fallback": True},
                error=str(exc),
                latency_ms=0,
                task_id=task_id,
            )
        fallback = self.run(payload, task_id)
        text = str(fallback.get("reply", ""))
        for index in range(0, len(text), 12):
            yield text[index : index + 12]
