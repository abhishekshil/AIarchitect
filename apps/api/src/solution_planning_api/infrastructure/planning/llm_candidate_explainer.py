from __future__ import annotations

import json

from solution_planning_api.application.ports.llm import LLMTask
from solution_planning_api.domain import SolutionCandidate
from solution_planning_api.infrastructure.llm import CandidateExplanationOutput, LLMOrchestrator


class LLMCandidateExplainer:
    def __init__(self, llm: LLMOrchestrator | None) -> None:
        self._llm = llm

    async def enrich(self, candidate: SolutionCandidate) -> SolutionCandidate:
        if self._llm is None:
            return candidate
        try:
            out = await self._llm.run_structured(
                task=LLMTask.CANDIDATE_EXPLANATION,
                values={"candidate_json": json.dumps(candidate.model_dump(mode="json"))},
                schema=CandidateExplanationOutput,
            )
        except Exception:  # noqa: BLE001
            return candidate

        summary = out.user_friendly_summary or candidate.summary
        tradeoffs = out.plain_tradeoffs or candidate.tradeoffs
        assumptions = list(candidate.assumptions)
        assumptions.extend([f"when_not_to_use: {x}" for x in out.when_not_to_use[:2]])
        reasoning = candidate.reasoning_summary
        if out.why_fit:
            fit_msg = "; ".join(out.why_fit[:3])
            reasoning = f"{reasoning} | LLM explanation: {fit_msg}" if reasoning else fit_msg
        return candidate.model_copy(
            update={
                "summary": summary,
                "tradeoffs": tradeoffs,
                "assumptions": assumptions,
                "reasoning_summary": reasoning,
            }
        )
