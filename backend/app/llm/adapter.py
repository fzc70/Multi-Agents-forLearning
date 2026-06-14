from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Iterator

import httpx

from app.core.config import Settings, get_settings
from app.llm.json_parser import parse_json_object
from app.repositories.repositories import AgentRunRepository


class LLMError(RuntimeError):
    pass


class LLMNotConfigured(LLMError):
    pass


class LLMAdapter(ABC):
    model: str

    @abstractmethod
    def complete_json(
        self,
        agent_name: str,
        prompt_version: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        task_id: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def stream_text(
        self,
        agent_name: str,
        prompt_version: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        task_id: str | None = None,
    ) -> Iterator[str]:
        output = self.complete_json(agent_name, prompt_version, system_prompt, user_payload, task_id)
        text = str(output.get("reply") or output.get("summary") or "")
        if text:
            yield text


class DeepSeekAdapter(LLMAdapter):
    def __init__(self, settings: Settings | None = None, run_repo: AgentRunRepository | None = None) -> None:
        self.settings = settings or get_settings()
        self.run_repo = run_repo or AgentRunRepository()
        self.model = self.settings.deepseek_model

    def complete_json(
        self,
        agent_name: str,
        prompt_version: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        task_id: str | None = None,
    ) -> dict[str, Any]:
        if not self.settings.deepseek_api_key:
            raise LLMNotConfigured("DeepSeek API Key 未配置")

        started = time.perf_counter()
        request_json = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": f"{system_prompt}\n必须只返回一个合法 json 对象，不要输出 markdown。"},
                {"role": "user", "content": self._payload_to_text(user_payload)},
            ],
            "temperature": self.settings.llm_temperature,
            "max_tokens": self.settings.llm_max_tokens,
            "response_format": {"type": "json_object"},
        }
        error: str | None = None
        output: dict[str, Any] | None = None
        try:
            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                response = client.post(
                    f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_json,
                )
                response.raise_for_status()
                data = response.json()
            content = data["choices"][0]["message"]["content"]
            output = parse_json_object(content)
            return output
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            raise LLMError(error) from exc
        finally:
            latency_ms = int((time.perf_counter() - started) * 1000)
            self.run_repo.add(
                agent_name=agent_name,
                model=self.settings.deepseek_model,
                prompt_version=prompt_version,
                input_json=user_payload,
                output_json=output,
                error=error,
                latency_ms=latency_ms,
                task_id=task_id,
            )

    def stream_text(
        self,
        agent_name: str,
        prompt_version: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        task_id: str | None = None,
    ) -> Iterator[str]:
        if not self.settings.deepseek_api_key:
            raise LLMNotConfigured("DeepSeek API Key 未配置")

        started = time.perf_counter()
        request_json = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": f"{system_prompt}\n请直接输出自然语言回答，不要输出 JSON 或 markdown 代码块。"},
                {"role": "user", "content": self._payload_to_text(user_payload)},
            ],
            "temperature": self.settings.llm_temperature,
            "max_tokens": self.settings.llm_max_tokens,
            "stream": True,
        }
        error: str | None = None
        chunks: list[str] = []
        try:
            import json

            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                with client.stream(
                    "POST",
                    f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.deepseek_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_json,
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data_text = line.removeprefix("data:").strip()
                        if data_text == "[DONE]":
                            break
                        data = json.loads(data_text)
                        delta = data["choices"][0].get("delta", {}).get("content") or ""
                        if delta:
                            chunks.append(delta)
                            yield delta
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            raise LLMError(error) from exc
        finally:
            latency_ms = int((time.perf_counter() - started) * 1000)
            self.run_repo.add(
                agent_name=agent_name,
                model=self.settings.deepseek_model,
                prompt_version=prompt_version,
                input_json=user_payload,
                output_json={"text": "".join(chunks)} if chunks else None,
                error=error,
                latency_ms=latency_ms,
                task_id=task_id,
            )

    @staticmethod
    def _payload_to_text(payload: dict[str, Any]) -> str:
        import json

        return json.dumps(payload, ensure_ascii=False)


class FakeLLMAdapter(LLMAdapter):
    model = "fake-llm"

    def __init__(self, run_repo: AgentRunRepository | None = None) -> None:
        self.run_repo = run_repo or AgentRunRepository()

    def complete_json(
        self,
        agent_name: str,
        prompt_version: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        task_id: str | None = None,
    ) -> dict[str, Any]:
        query = str(user_payload.get("message") or user_payload.get("task_title") or "学习任务")
        output = {
            "summary": f"围绕“{query[:30]}”生成的结构化结果。",
            "reply": f"我会结合当前任务、资料和学习记录，先帮你拆出下一步：{query[:40]}。",
            "dimensions": [],
            "resources": [],
            "steps": [],
            "weak_points": [],
            "nodes": [],
            "edges": [],
        }
        self.run_repo.add(
            agent_name=agent_name,
            model=self.model,
            prompt_version=prompt_version,
            input_json=user_payload,
            output_json=output,
            latency_ms=1,
            task_id=task_id,
        )
        return output

    def stream_text(
        self,
        agent_name: str,
        prompt_version: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        task_id: str | None = None,
    ) -> Iterator[str]:
        output = self.complete_json(agent_name, prompt_version, system_prompt, user_payload, task_id)
        text = str(output.get("reply", ""))
        for index in range(0, len(text), 8):
            yield text[index : index + 8]


def get_llm_adapter(fake: bool = False) -> LLMAdapter:
    if fake:
        return FakeLLMAdapter()
    return DeepSeekAdapter()
