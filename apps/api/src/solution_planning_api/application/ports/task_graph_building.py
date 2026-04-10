"""Pluggable task-graph synthesis from a selected candidate (Phase 8+)."""

from __future__ import annotations

from typing import Protocol

from solution_planning_api.domain import (
    ArchitectureTemplate,
    CapabilityBlock,
    ConstraintProfile,
    RequirementProfile,
    SolutionCandidate,
    TaskGraph,
)


class TaskGraphBuilder(Protocol):
    def build(
        self,
        *,
        candidate: SolutionCandidate,
        requirement: RequirementProfile,
        constraint: ConstraintProfile | None,
        template: ArchitectureTemplate,
        capabilities_by_id: dict[str, CapabilityBlock],
    ) -> TaskGraph: ...
