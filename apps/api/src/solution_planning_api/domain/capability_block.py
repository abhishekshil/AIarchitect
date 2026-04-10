"""Reusable capability unit for composition (Blueprint §5.3)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject


class CapabilityBlock(BaseModel):
    """Registry-facing capability definition; extensible via structured JSON fields."""

    model_config = {"extra": "forbid"}

    capability_id: str = Field(..., min_length=1, pattern=r"^[a-z0-9_]+$")
    name: str
    category: str | None = None
    description: str | None = None

    required_inputs: list[str] = Field(default_factory=list)
    produced_outputs: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    compatible_architectures: list[str] = Field(default_factory=list)
    provider_compatibility: list[str] = Field(default_factory=list)

    cost_profile: JsonObject | None = None
    latency_profile: JsonObject | None = None
    risk_profile: JsonObject | None = None
    governance_flags: JsonObject | None = None
