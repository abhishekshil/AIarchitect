"""Pluggable playground inference (mock now, real providers later)."""

from __future__ import annotations

from typing import Any, Protocol

from solution_planning_api.domain import RuntimeGraph


class PlaygroundInferenceSimulator(Protocol):
    def run(
        self,
        *,
        graph: RuntimeGraph,
        input_text: str,
    ) -> dict[str, Any]:
        """Return a dict compatible with `PlaygroundInferResponse` (without inference_id)."""
        ...
