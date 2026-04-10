"""Canonical normalized requirement intent (Blueprint §5.1)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class RequirementProfile(BaseModel):
    """Structured capture of user intent after analysis / normalization."""

    model_config = {"extra": "forbid"}

    requirement_id: UUID
    project_id: UUID
    raw_text: str = Field(..., min_length=1)

    business_goal: str | None = None
    primary_task_type: str | None = None
    secondary_task_types: list[str] = Field(default_factory=list)
    input_modalities: list[str] = Field(default_factory=list)
    output_modalities: list[str] = Field(default_factory=list)
    domain: str | None = None

    freshness_requirement: str | None = None
    grounding_requirement: str | None = None
    personalization_requirement: str | None = None
    behavior_specialization_requirement: str | None = None

    decision_criticality: str | None = None
    traceability_requirement: str | None = None
    latency_sensitivity: str | None = None
    cost_sensitivity: str | None = None
    security_sensitivity: str | None = None

    human_in_loop_requirement: str | None = None
    tool_use_requirement: str | None = None
    automation_depth: str | None = None

    success_criteria: list[str] = Field(default_factory=list)
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
