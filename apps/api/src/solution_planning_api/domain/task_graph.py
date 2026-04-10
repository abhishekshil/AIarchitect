"""Onboarding / configuration task graph (Blueprint §5.6)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject


class TaskGraphNode(BaseModel):
    model_config = {"extra": "forbid"}

    node_id: str
    title: str
    description: str | None = None
    task_type: str | None = None
    metadata: JsonObject | None = None
    # Stable hints for onboarding UIs / Phase 9 (evaluated against requirement + constraint).
    guidance_refs: list[str] = Field(default_factory=list)
    condition: str | None = Field(
        default=None,
        description="If set, task is included for conditional flows (e.g. privacy_elevated).",
    )


class TaskGraphEdge(BaseModel):
    model_config = {"extra": "forbid"}

    source_id: str
    target_id: str
    relation: str | None = "depends_on"


class TaskGraph(BaseModel):
    model_config = {"extra": "forbid"}

    task_graph_id: UUID
    project_id: UUID
    candidate_id: UUID

    nodes: list[TaskGraphNode] = Field(default_factory=list)
    edges: list[TaskGraphEdge] = Field(default_factory=list)
    dependencies: JsonObject | None = None
    validation_rules: JsonObject | None = None
    user_guidance_refs: list[str] = Field(default_factory=list)
