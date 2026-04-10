"""Translate planning artifacts into an executable RuntimeGraph (Phase 10+)."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from solution_planning_api.domain import (
    ArchitectureTemplate,
    RuntimeGraph,
    SolutionCandidate,
    TaskGraph,
)


class RuntimeGraphBuilder(Protocol):
    def build(
        self,
        *,
        requirement_id: UUID | None,
        template: ArchitectureTemplate,
        candidate: SolutionCandidate,
        task_graph: TaskGraph | None,
    ) -> RuntimeGraph:
        ...
