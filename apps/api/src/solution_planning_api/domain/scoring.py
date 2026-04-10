"""Scoring modes for candidate ranking (extensible — add modes + weights in the planning engine)."""

from __future__ import annotations

from enum import StrEnum


class ScoringMode(StrEnum):
    BEST_OVERALL = "best_overall"
    LOWEST_COST = "lowest_cost"
    FASTEST_LAUNCH = "fastest_launch"
    HIGHEST_QUALITY = "highest_quality"
