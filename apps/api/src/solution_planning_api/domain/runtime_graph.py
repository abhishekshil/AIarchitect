"""Executable runtime assembly (Blueprint §5.7, §12)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject
from solution_planning_api.domain.runtime_component import RuntimeComponentType


class RuntimeGraphNode(BaseModel):
    model_config = {"extra": "forbid"}

    node_id: str
    component_type: str = Field(
        ...,
        description=f"One of: {', '.join(sorted(RuntimeComponentType))}",
    )
    label: str | None = None
    config: JsonObject = Field(default_factory=dict)


class RuntimeGraphEdge(BaseModel):
    model_config = {"extra": "forbid"}

    source_id: str
    target_id: str
    relation: str | None = None
    metadata: JsonObject | None = None


class RuntimeGraph(BaseModel):
    model_config = {"extra": "forbid"}

    runtime_graph_id: UUID
    project_id: UUID
    candidate_id: UUID | None = None
    requirement_id: UUID | None = Field(
        default=None,
        description="Requirement revision this graph was built from (when known).",
    )
    version: int = Field(default=1, ge=1)

    nodes: list[RuntimeGraphNode] = Field(default_factory=list)
    edges: list[RuntimeGraphEdge] = Field(default_factory=list)
    provider_bindings: JsonObject | None = None
    observability: JsonObject | None = None
    failure_handling: JsonObject | None = None
