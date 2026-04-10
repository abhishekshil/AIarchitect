"""Implementation and business constraints (Blueprint §5.2)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class ConstraintProfile(BaseModel):
    """Constraints applied during planning and architecture selection."""

    model_config = {"extra": "forbid"}

    constraint_id: UUID
    project_id: UUID
    requirement_id: UUID | None = None

    privacy_level: str | None = None
    data_residency: str | None = None
    max_latency_ms: int | None = Field(default=None, ge=0)
    max_cost_per_request: float | None = Field(default=None, ge=0.0)
    expected_usage_volume: str | None = None
    maintainability_preference: str | None = None
    deployment_preference: str | None = None
    required_auditability: str | None = None
    acceptable_failure_mode: str | None = None
