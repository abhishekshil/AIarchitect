"""Shared domain primitives and type aliases."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypeAlias

JsonObject: TypeAlias = dict[str, Any]


def utc_now() -> datetime:
    return datetime.now(UTC)


__all__ = ["JsonObject", "utc_now"]
