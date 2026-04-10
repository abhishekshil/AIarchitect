"""Workspace primitives (users/projects) — supporting domain, not planning canonicals."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class User(BaseModel):
    model_config = {"extra": "forbid"}

    user_id: UUID
    email: str = Field(..., min_length=3, max_length=320)
    password_hash: str | None = None
    created_at: datetime | None = None


class Project(BaseModel):
    model_config = {"extra": "forbid"}

    project_id: UUID
    owner_user_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    created_at: datetime | None = None
    updated_at: datetime | None = None
