from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from urllib import request

from solution_planning_api.application.ports.llm import LLMInvocation, LLMProvider, LLMResult, LLMTelemetry


class LoggingLLMTelemetry(LLMTelemetry):
    def record_start(self, *, task, model: str, provider: str) -> None:  # type: ignore[no-untyped-def]
        _ = task
        print(f"[llm] start provider={provider} model={model}")

    def record_success(self, *, task, model: str, provider: str, latency_ms: int, attempts: int) -> None:  # type: ignore[no-untyped-def]
        _ = task
        print(
            f"[llm] success provider={provider} model={model} latency_ms={latency_ms} attempts={attempts}"
        )

    def record_failure(self, *, task, model: str, provider: str, error: str) -> None:  # type: ignore[no-untyped-def]
        _ = task
        print(f"[llm] failure provider={provider} model={model} error={error}")


class DisabledLLMProvider(LLMProvider):
    async def invoke(self, invocation: LLMInvocation) -> LLMResult:
        raise RuntimeError("LLM provider is disabled")


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    base_url: str
    api_key: str
    provider_name: str


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, cfg: OpenAICompatibleConfig) -> None:
        self._cfg = cfg

    async def invoke(self, invocation: LLMInvocation) -> LLMResult:
        attempts = 0
        last_error: Exception | None = None
        start_ms = time.time()
        while attempts <= invocation.max_retries:
            attempts += 1
            try:
                raw = await asyncio.wait_for(
                    asyncio.to_thread(self._do_request, invocation),
                    timeout=invocation.timeout_s,
                )
                latency_ms = int((time.time() - start_ms) * 1000)
                return LLMResult(
                    raw_text=raw,
                    provider=self._cfg.provider_name,
                    model=invocation.model,
                    latency_ms=latency_ms,
                    attempts=attempts,
                )
            except Exception as e:  # noqa: BLE001
                last_error = e
        raise RuntimeError(f"LLM request failed after retries: {last_error}")

    def _do_request(self, invocation: LLMInvocation) -> str:
        url = self._cfg.base_url.rstrip("/") + "/chat/completions"
        body = {
            "model": invocation.model,
            "response_format": {"type": invocation.response_format},
            "messages": [
                {"role": "system", "content": invocation.system_prompt},
                {"role": "user", "content": invocation.user_prompt},
            ],
        }
        req = request.Request(
            url=url,
            method="POST",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._cfg.api_key}",
            },
        )
        with request.urlopen(req, timeout=invocation.timeout_s) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode("utf-8"))
        return str(payload["choices"][0]["message"]["content"])
