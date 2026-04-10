from __future__ import annotations

import json

from solution_planning_api.application.ports.llm import LLMTask
from solution_planning_api.domain import TaskGraphNode
from solution_planning_api.infrastructure.llm import LLMOrchestrator, OnboardingGuidanceOutput


class LLMOnboardingGuidance:
    def __init__(self, llm: LLMOrchestrator | None) -> None:
        self._llm = llm

    async def enrich(
        self,
        *,
        node: TaskGraphNode,
        suggestions: list[str],
        placeholder: str,
    ) -> tuple[list[str], str]:
        if self._llm is None:
            return suggestions, placeholder
        try:
            out = await self._llm.run_structured(
                task=LLMTask.ONBOARDING_GUIDANCE,
                values={
                    "task_json": json.dumps(node.model_dump(mode="json")),
                    "suggestions_json": json.dumps(suggestions),
                },
                schema=OnboardingGuidanceOutput,
            )
        except Exception:  # noqa: BLE001
            return suggestions, placeholder

        merged: list[str] = []
        merged.extend(suggestions[:2])
        merged.extend(out.suggestions[:3])
        merged.extend([f"Tip: {x}" for x in out.tips[:2]])
        merged.extend([f"Warning: {x}" for x in out.warnings[:1]])
        dedup: list[str] = []
        seen: set[str] = set()
        for item in merged:
            if item not in seen:
                dedup.append(item)
                seen.add(item)
        return dedup[:5], (out.example_placeholder or placeholder)
