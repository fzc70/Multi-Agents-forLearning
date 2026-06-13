from __future__ import annotations

from typing import Any

from app.llm.adapter import LLMAdapter, LLMError, LLMNotConfigured, get_llm_adapter
from app.repositories.repositories import AgentRunRepository


class BaseAgent:
    name = "BaseAgent"
    prompt_version = "v1"
    system_prompt = "你是一个学习系统智能体。只输出 JSON 对象。"

    def __init__(self, llm: LLMAdapter | None = None) -> None:
        self.llm = llm or get_llm_adapter()
        self.run_repo = AgentRunRepository()

    def run_llm(self, payload: dict[str, Any], task_id: str | None = None) -> dict[str, Any] | None:
        try:
            return self.llm.complete_json(
                agent_name=self.name,
                prompt_version=self.prompt_version,
                system_prompt=self.system_prompt,
                user_payload=payload,
                task_id=task_id,
            )
        except (LLMNotConfigured, LLMError) as exc:
            self.run_repo.add(
                agent_name=self.name,
                model=getattr(self.llm, "model", "unknown"),
                prompt_version=self.prompt_version,
                input_json=payload,
                output_json={"fallback": True},
                error=str(exc),
                latency_ms=0,
                task_id=task_id,
            )
            return None
