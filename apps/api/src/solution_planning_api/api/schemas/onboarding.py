"""Stable onboarding API shapes (Phase 9)."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_V: Literal["1.0"] = "1.0"


class OnboardingTaskItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    title: str
    description: str | None = None
    task_type: str | None = None
    metadata: dict[str, Any] | None = None
    guidance_refs: list[str] = Field(default_factory=list)
    condition: str | None = None
    state: str
    suggestions: list[str] = Field(default_factory=list)
    example_placeholder: str = ""
    response: dict[str, Any] | None = None
    validation_feedback: dict[str, Any] | None = None
    updated_at: str | None = None


class OnboardingTaskGraphEdgeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    target_id: str
    relation: str | None = "depends_on"


class OnboardingTasksEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = SCHEMA_V
    task_graph_id: UUID
    tasks: list[OnboardingTaskItemResponse]
    edges: list[OnboardingTaskGraphEdgeResponse] = Field(
        default_factory=list,
        description="Task graph edges for dependency-aware ordering in UIs.",
    )


class OnboardingProgressResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = SCHEMA_V
    task_graph_id: UUID
    total_tasks: int
    by_state: dict[str, int]
    percent_completed: float


class SubmitOnboardingTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    response: dict[str, Any] = Field(
        ...,
        description='JSON object with required string field "notes" (see OpenAPI examples).',
    )
