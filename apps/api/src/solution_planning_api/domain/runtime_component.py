"""Runtime graph component kinds (Phase 10 — executable assembly)."""

from __future__ import annotations

from enum import StrEnum


class RuntimeComponentType(StrEnum):
    MODEL = "model"
    RETRIEVER = "retriever"
    VALIDATOR = "validator"
    ROUTER = "router"
    AGENT = "agent"
    FORMATTER = "formatter"
