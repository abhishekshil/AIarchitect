"""Stable HTTP contract for architecture recommendation options (Phase 7 — UI-facing)."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from solution_planning_api.domain import SolutionCandidate
from solution_planning_api.domain.common import JsonObject
from solution_planning_api.domain.scoring import ScoringMode

# Bump when adding/removing/renaming response fields (clients may branch on this).
API_SCHEMA_VERSION: Literal["1.0"] = "1.0"


class ArchitectureRecommendationOption(BaseModel):
    """One persisted architecture option for selection (stable field names for the frontend)."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: UUID
    project_id: UUID
    requirement_id: UUID
    title: str
    summary: str | None = None
    score: float | None = Field(
        default=None,
        description="Primary suitability score used when this batch was generated (see score_breakdown).",
    )
    rationale: str | None = Field(
        default=None,
        description="Human-readable reasoning summary for the option.",
    )
    tradeoffs: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    complexity_estimate: JsonObject | None = None
    latency_estimate: JsonObject | None = None
    cost_estimate: JsonObject | None = None
    governance_score: float | None = None
    score_breakdown: JsonObject | None = Field(
        default=None,
        description="Explainable dimensions and composite_by_mode scores.",
    )
    capability_set: list[str] = Field(default_factory=list)
    architecture_template_ref: str | None = None
    candidate_type: str | None = None
    synthesized_graph: JsonObject = Field(default_factory=dict)

    @classmethod
    def from_candidate(cls, c: SolutionCandidate) -> ArchitectureRecommendationOption:
        return cls(
            candidate_id=c.candidate_id,
            project_id=c.project_id,
            requirement_id=c.requirement_id,
            title=c.title,
            summary=c.summary,
            score=c.suitability_score,
            rationale=c.reasoning_summary,
            tradeoffs=list(c.tradeoffs),
            assumptions=list(c.assumptions),
            complexity_estimate=_as_json_object(c.complexity_estimate),
            latency_estimate=_as_json_object(c.latency_estimate),
            cost_estimate=_as_json_object(c.cost_estimate),
            governance_score=c.governance_score,
            score_breakdown=_as_json_object(c.score_breakdown),
            capability_set=list(c.capability_set),
            architecture_template_ref=c.architecture_template_ref,
            candidate_type=c.candidate_type,
            synthesized_graph=dict(c.synthesized_graph) if c.synthesized_graph else {},
        )


def _as_json_object(value: dict[str, Any] | None) -> JsonObject | None:
    if value is None:
        return None
    return dict(value)


class ArchitectureRecommendationsEnvelope(BaseModel):
    """Wrapper for list/generate responses so the UI can rely on a versioned shape."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = API_SCHEMA_VERSION
    project_id: UUID
    requirement_id: UUID | None = Field(
        default=None,
        description="When set, all options belong to this requirement; omitted for project-wide aggregates.",
    )
    sort_mode: ScoringMode
    options: list[ArchitectureRecommendationOption] = Field(default_factory=list)


class ArchitectureRecommendationDetail(BaseModel):
    """Single-option fetch (same option shape as in the list envelope)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = API_SCHEMA_VERSION
    option: ArchitectureRecommendationOption


def envelope_for_candidates(
    *,
    project_id: UUID,
    sort_mode: ScoringMode,
    candidates: list[SolutionCandidate],
) -> ArchitectureRecommendationsEnvelope:
    """Build list/generate response; `requirement_id` is set only when all options share one revision."""
    req: UUID | None = None
    if candidates:
        first = candidates[0].requirement_id
        if all(c.requirement_id == first for c in candidates):
            req = first
    return ArchitectureRecommendationsEnvelope(
        project_id=project_id,
        requirement_id=req,
        sort_mode=sort_mode,
        options=[ArchitectureRecommendationOption.from_candidate(c) for c in candidates],
    )
