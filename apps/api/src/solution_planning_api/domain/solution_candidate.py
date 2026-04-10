"""One generated architecture option (Blueprint §5.5)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject


class SolutionCandidate(BaseModel):
    """Ranked / explainable solution option produced by the planning engine."""

    model_config = {"extra": "forbid"}

    candidate_id: UUID
    project_id: UUID
    requirement_id: UUID

    candidate_type: str | None = None
    title: str
    summary: str | None = None

    capability_set: list[str] = Field(default_factory=list)
    architecture_template_ref: str | None = None
    synthesized_graph: JsonObject = Field(default_factory=dict)

    assumptions: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)

    suitability_score: float | None = None
    cost_estimate: JsonObject | None = None
    complexity_estimate: JsonObject | None = None
    latency_estimate: JsonObject | None = None
    governance_score: float | None = None
    reasoning_summary: str | None = None

    # Explainable decomposition (Blueprint §14.1); optional until scoring engine lands.
    score_breakdown: JsonObject | None = None
