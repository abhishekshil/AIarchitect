from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RequirementUnderstandingOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    business_goal: str | None = None
    primary_task_type: str | None = None
    secondary_task_types: list[str] = Field(default_factory=list)
    grounding_requirement: str | None = None
    behavior_specialization_requirement: str | None = None
    privacy_level: str | None = None
    security_sensitivity: str | None = None
    latency_sensitivity: str | None = None
    cost_sensitivity: str | None = None
    human_in_loop_requirement: str | None = None
    agentic_decomposition_helpful: bool = False
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ambiguity_signals: list[str] = Field(default_factory=list)


class ClarificationQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=3, max_length=240)
    target_field: str = Field(min_length=2, max_length=64)


class ClarificationQuestionsOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    questions: list[ClarificationQuestion] = Field(default_factory=list, max_length=4)


class CandidateExplanationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_friendly_summary: str | None = None
    why_fit: list[str] = Field(default_factory=list)
    plain_tradeoffs: list[str] = Field(default_factory=list)
    when_not_to_use: list[str] = Field(default_factory=list)


class OnboardingGuidanceOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestions: list[str] = Field(default_factory=list, max_length=5)
    tips: list[str] = Field(default_factory=list, max_length=3)
    warnings: list[str] = Field(default_factory=list, max_length=3)
    example_placeholder: str | None = None
