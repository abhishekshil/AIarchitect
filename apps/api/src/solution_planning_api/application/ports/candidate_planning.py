"""
Candidate synthesis + scoring — swap implementations for ML / LLM planners.

MVP: `HeuristicCandidatePlanningEngine` composes registry templates + capability metadata.
"""

from __future__ import annotations

from typing import Protocol

from solution_planning_api.domain import (
    ArchitectureTemplate,
    CapabilityBlock,
    ConstraintProfile,
    RequirementProfile,
    SolutionCandidate,
)
from solution_planning_api.domain.scoring import ScoringMode


class CandidatePlanningEngine(Protocol):
    async def synthesize_and_score(
        self,
        *,
        requirement: RequirementProfile,
        constraint: ConstraintProfile | None,
        templates: list[ArchitectureTemplate],
        capabilities: list[CapabilityBlock],
        generation_mode: ScoringMode,
    ) -> list[SolutionCandidate]: ...
