from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from solution_planning_api.application.ports.llm import (
    LLMInvocation,
    LLMProvider,
    LLMTask,
    LLMTelemetry,
    PromptRegistry,
)

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class LLMTaskPolicy:
    model: str
    timeout_s: float
    max_retries: int
    min_confidence: float = 0.0


class LLMOrchestrator:
    def __init__(
        self,
        *,
        provider: LLMProvider,
        prompts: PromptRegistry,
        telemetry: LLMTelemetry,
        task_policies: dict[LLMTask, LLMTaskPolicy],
    ) -> None:
        self._provider = provider
        self._prompts = prompts
        self._telemetry = telemetry
        self._task_policies = task_policies

    async def run_structured(
        self,
        *,
        task: LLMTask,
        values: dict[str, Any],
        schema: type[T],
    ) -> T:
        policy = self._task_policies[task]
        template, user_prompt = self._prompts.render(task, values)
        invocation = LLMInvocation(
            task=task,
            model=policy.model,
            system_prompt=template.system_prompt,
            user_prompt=user_prompt,
            timeout_s=policy.timeout_s,
            max_retries=policy.max_retries,
        )

        self._telemetry.record_start(task=task, model=policy.model, provider=type(self._provider).__name__)
        try:
            result = await self._provider.invoke(invocation)
            obj = json.loads(result.raw_text)
            parsed = schema.model_validate(obj)
            self._telemetry.record_success(
                task=task,
                model=result.model,
                provider=result.provider,
                latency_ms=result.latency_ms,
                attempts=result.attempts,
            )
            return parsed
        except (ValidationError, ValueError, KeyError, RuntimeError) as e:
            self._telemetry.record_failure(
                task=task,
                model=policy.model,
                provider=type(self._provider).__name__,
                error=str(e),
            )
            raise
