"""User's committed architecture choice for a requirement revision (Blueprint §5.5)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ArchitectureSelection(BaseModel):
    model_config = {"extra": "forbid"}

    selection_id: UUID
    project_id: UUID
    requirement_id: UUID
    solution_candidate_id: UUID
    selected_at: datetime
