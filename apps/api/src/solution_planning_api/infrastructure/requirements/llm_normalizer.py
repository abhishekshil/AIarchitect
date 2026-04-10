from __future__ import annotations

import json
import uuid

from solution_planning_api.application.ports.llm import LLMTask
from solution_planning_api.application.ports.requirement_normalization import (
    NormalizationContext,
    NormalizationResult,
    RequirementNormalizer,
)
from solution_planning_api.domain import ConstraintProfile, RequirementProfile
from solution_planning_api.infrastructure.llm import (
    ClarificationQuestionsOutput,
    LLMOrchestrator,
    RequirementUnderstandingOutput,
)
from solution_planning_api.infrastructure.requirements.heuristic_normalizer import (
    HeuristicRequirementNormalizer,
)


class LLMEnhancedRequirementNormalizer(RequirementNormalizer):
    def __init__(
        self,
        *,
        llm: LLMOrchestrator | None,
        heuristic: RequirementNormalizer | None = None,
        min_confidence: float = 0.55,
    ) -> None:
        self._llm = llm
        self._heuristic = heuristic or HeuristicRequirementNormalizer()
        self._min_confidence = min_confidence

    async def normalize(self, context: NormalizationContext) -> NormalizationResult:
        fallback = await self._heuristic.normalize(context)
        if self._llm is None:
            return fallback

        try:
            parsed = await self._llm.run_structured(
                task=LLMTask.REQUIREMENT_UNDERSTANDING,
                values={"raw_text": context.raw_text},
                schema=RequirementUnderstandingOutput,
            )
        except Exception:  # noqa: BLE001
            return fallback

        if parsed.confidence_score < self._min_confidence:
            return fallback

        req_id = uuid.uuid4()
        merged = _merge_with_fallback(context=context, requirement_id=req_id, llm=parsed, fallback=fallback)
        clarifications = await self._clarifications_if_needed(context=context, parsed=parsed)
        rationale = list(merged.rationale)
        rationale.append(
            f"LLM normalized (confidence={parsed.confidence_score:.2f}); deterministic fallback retained as guardrail."
        )
        if clarifications:
            rationale.append(f"Generated {len(clarifications)} clarification question(s) for ambiguous fields.")
        audit = {
            "raw_input": context.raw_text,
            "llm_output": parsed.model_dump(mode="json"),
            "fallback_method": fallback.method,
            "fallback_rationale": fallback.rationale,
        }
        return NormalizationResult(
            requirement_profile=merged.requirement_profile,
            constraint_profile=merged.constraint_profile,
            method=merged.method,
            rationale=rationale,
            clarification_questions=clarifications,
            audit=audit,
        )

    async def _clarifications_if_needed(
        self,
        *,
        context: NormalizationContext,
        parsed: RequirementUnderstandingOutput,
    ) -> list[str]:
        if self._llm is None:
            return []
        if parsed.confidence_score >= 0.7 and not parsed.ambiguity_signals:
            return []
        try:
            out = await self._llm.run_structured(
                task=LLMTask.CLARIFICATION_QUESTIONS,
                values={
                    "raw_text": context.raw_text,
                    "ambiguity_signals": json.dumps(parsed.ambiguity_signals),
                },
                schema=ClarificationQuestionsOutput,
            )
        except Exception:  # noqa: BLE001
            return []
        return [q.question for q in out.questions]


def _merge_with_fallback(
    *,
    context: NormalizationContext,
    requirement_id: uuid.UUID,
    llm: RequirementUnderstandingOutput,
    fallback: NormalizationResult,
) -> NormalizationResult:
    req = RequirementProfile(
        requirement_id=requirement_id,
        project_id=context.project_id,
        raw_text=context.raw_text.strip(),
        business_goal=llm.business_goal or fallback.requirement_profile.business_goal,
        primary_task_type=llm.primary_task_type or fallback.requirement_profile.primary_task_type,
        secondary_task_types=llm.secondary_task_types or fallback.requirement_profile.secondary_task_types,
        grounding_requirement=llm.grounding_requirement
        or fallback.requirement_profile.grounding_requirement,
        behavior_specialization_requirement=llm.behavior_specialization_requirement
        or fallback.requirement_profile.behavior_specialization_requirement,
        security_sensitivity=llm.security_sensitivity or fallback.requirement_profile.security_sensitivity,
        latency_sensitivity=llm.latency_sensitivity or fallback.requirement_profile.latency_sensitivity,
        cost_sensitivity=llm.cost_sensitivity or fallback.requirement_profile.cost_sensitivity,
        human_in_loop_requirement=llm.human_in_loop_requirement
        or fallback.requirement_profile.human_in_loop_requirement,
        automation_depth="high"
        if llm.agentic_decomposition_helpful
        else fallback.requirement_profile.automation_depth,
        confidence_score=llm.confidence_score,
    )
    constraint: ConstraintProfile | None = None
    if llm.privacy_level or fallback.constraint_profile:
        fallback_c = fallback.constraint_profile
        constraint = ConstraintProfile(
            constraint_id=uuid.uuid4(),
            project_id=context.project_id,
            requirement_id=requirement_id,
            privacy_level=llm.privacy_level or (fallback_c.privacy_level if fallback_c else None),
            deployment_preference=fallback_c.deployment_preference if fallback_c else None,
            required_auditability="high" if llm.grounding_requirement == "high" else None,
        )
    return NormalizationResult(
        requirement_profile=req,
        constraint_profile=constraint,
        method="llm_assisted_v1",
        rationale=[],
    )
