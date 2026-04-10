"""
Requirement normalization — pluggable analysis from raw text → structured profiles.

MVP: `HeuristicRequirementNormalizer` uses keyword/rule signals.
TODO(LLM): Add an async LLM-backed implementation that maps model output into
`RequirementProfile` / `ConstraintProfile` (structured output + Pydantic validation).
Keep `RequirementNormalizer` stable so the service layer does not change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from typing import Protocol
from uuid import UUID

from solution_planning_api.domain import ConstraintProfile, RequirementProfile


@dataclass(frozen=True)
class NormalizationContext:
    """Inputs available to any normalizer (extend fields as product grows)."""

    project_id: UUID
    owner_user_id: UUID
    raw_text: str


@dataclass(frozen=True)
class NormalizationResult:
    """Output of a normalization pass, ready for persistence (includes new UUIDs)."""

    requirement_profile: RequirementProfile
    constraint_profile: ConstraintProfile | None
    method: str
    rationale: list[str]
    clarification_questions: list[str] = field(default_factory=list)
    audit: dict[str, Any] = field(default_factory=dict)


class RequirementNormalizer(Protocol):
    async def normalize(self, context: NormalizationContext) -> NormalizationResult: ...
