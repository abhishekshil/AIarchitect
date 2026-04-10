from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol


class LLMTask(StrEnum):
    REQUIREMENT_UNDERSTANDING = "requirement_understanding"
    CLARIFICATION_QUESTIONS = "clarification_questions"
    CANDIDATE_EXPLANATION = "candidate_explanation"
    ONBOARDING_GUIDANCE = "onboarding_guidance"
    IMPROVEMENT_SUGGESTIONS = "improvement_suggestions"
    EVALUATION_EXPLANATION = "evaluation_explanation"


@dataclass(frozen=True)
class PromptTemplate:
    prompt_id: str
    purpose: str
    version: str
    expected_schema: str
    fallback_notes: str
    system_prompt: str
    user_prompt_template: str


@dataclass(frozen=True)
class LLMInvocation:
    task: LLMTask
    model: str
    system_prompt: str
    user_prompt: str
    timeout_s: float
    max_retries: int
    response_format: str = "json_object"


@dataclass(frozen=True)
class LLMResult:
    raw_text: str
    provider: str
    model: str
    latency_ms: int
    attempts: int


class LLMProvider(Protocol):
    async def invoke(self, invocation: LLMInvocation) -> LLMResult: ...


class LLMTelemetry(Protocol):
    def record_start(self, *, task: LLMTask, model: str, provider: str) -> None: ...

    def record_success(
        self,
        *,
        task: LLMTask,
        model: str,
        provider: str,
        latency_ms: int,
        attempts: int,
    ) -> None: ...

    def record_failure(
        self,
        *,
        task: LLMTask,
        model: str,
        provider: str,
        error: str,
    ) -> None: ...


class PromptRegistry(Protocol):
    def get(self, task: LLMTask) -> PromptTemplate: ...

    def render(self, task: LLMTask, values: dict[str, Any]) -> tuple[PromptTemplate, str]: ...
