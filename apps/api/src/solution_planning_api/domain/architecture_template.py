"""Reusable architecture pattern template (Blueprint §5.4)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject


class ArchitectureTemplate(BaseModel):
    """Template describing how capabilities compose into a known pattern."""

    model_config = {"extra": "forbid"}

    template_id: str = Field(..., min_length=1, pattern=r"^[a-z0-9_]+$")
    name: str
    visible_label: str | None = None
    description: str | None = None

    required_capabilities: list[str] = Field(default_factory=list)
    optional_capabilities: list[str] = Field(default_factory=list)
    constraints_supported: list[str] = Field(default_factory=list)

    onboarding_template_ref: str | None = None
    runtime_graph_template_ref: str | None = None
    evaluation_template_ref: str | None = None

    metadata: JsonObject | None = None
