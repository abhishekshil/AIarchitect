"""Stable responses for architecture selection + task graph (Phase 8)."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from solution_planning_api.domain import ArchitectureSelection, TaskGraph


class SelectArchitectureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: UUID


class ArchitectureSelectionEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    selection: ArchitectureSelection
    task_graph: TaskGraph
