from __future__ import annotations

from typing import Any

from app.llm.adapter import LLMAdapter, LLMError, LLMNotConfigured, get_llm_adapter
from app.repositories.agent_run_repository import AgentRunRepository


class BaseAgent:
    """所有 Agent 的统一 LLM 调用入口。

    Agent 只负责“输入 payload -> 结构化 JSON 输出”，不直接修改业务表。
    业务持久化、状态推进和跨模块编排放在 Service/Workflow。
    """

    name = "BaseAgent"
    prompt_version = "v1"
    system_prompt = "你是一个学习系统智能体。只输出 JSON 对象。"

    def __init__(self, llm: LLMAdapter | None = None) -> None:
        """初始化 BaseAgent 所需的依赖。"""
        self.llm = llm or get_llm_adapter()
        self.run_repo = AgentRunRepository()

    def run_llm(
        self, payload: dict[str, Any], task_id: str | None = None
    ) -> dict[str, Any] | None:
        """执行 run_llm 对应的业务处理。"""
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
