"""Rule-based normalization — swap for LLM-backed analyzer without changing the service API."""

from __future__ import annotations

import uuid

from solution_planning_api.application.ports.requirement_normalization import (
    NormalizationContext,
    NormalizationResult,
)
from solution_planning_api.domain import ConstraintProfile, RequirementProfile


class HeuristicRequirementNormalizer:
    """
    Lightweight keyword / phrase signals. Tuned for MVP demos, not production accuracy.

    TODO(LLM): Replace or chain with model-based extraction; keep outputs Pydantic-valid.
    """

    async def normalize(self, context: NormalizationContext) -> NormalizationResult:
        text = context.raw_text.strip()
        low = text.lower()
        rationale: list[str] = []

        primary_task_type, secondary = _infer_task_type(low, rationale)
        grounding_requirement = _flag_grounding(low, rationale)
        latency_sensitivity = _flag_latency(low, rationale)
        cost_sensitivity = _flag_cost(low, rationale)
        security_sensitivity, privacy_level = _flag_privacy(low, rationale)
        human_in_loop_requirement = _flag_hitl(low, rationale)
        tool_use_requirement = _flag_tools(low, rationale)
        deployment_preference = _flag_deployment(low, rationale)

        confidence = 0.35
        if len(rationale) >= 2:
            confidence = 0.5
        if len(rationale) >= 4:
            confidence = 0.62

        req_id = uuid.uuid4()
        requirement = RequirementProfile(
            requirement_id=req_id,
            project_id=context.project_id,
            raw_text=text,
            primary_task_type=primary_task_type,
            secondary_task_types=secondary,
            grounding_requirement=grounding_requirement,
            latency_sensitivity=latency_sensitivity,
            cost_sensitivity=cost_sensitivity,
            security_sensitivity=security_sensitivity,
            human_in_loop_requirement=human_in_loop_requirement,
            tool_use_requirement=tool_use_requirement,
            confidence_score=confidence,
        )

        constraint: ConstraintProfile | None = None
        if any(
            v is not None
            for v in (
                privacy_level,
                deployment_preference,
            )
        ):
            cid = uuid.uuid4()
            constraint = ConstraintProfile(
                constraint_id=cid,
                project_id=context.project_id,
                requirement_id=req_id,
                privacy_level=privacy_level,
                deployment_preference=deployment_preference,
            )
            rationale.append("Derived constraint profile from privacy / deployment cues")

        return NormalizationResult(
            requirement_profile=requirement,
            constraint_profile=constraint,
            method="heuristic_v1",
            rationale=rationale,
        )


def _infer_task_type(low: str, rationale: list[str]) -> tuple[str, list[str]]:
    secondary: list[str] = []
    if any(
        k in low
        for k in (
            "retrieve",
            "retrieval",
            "knowledge base",
            "documents",
            "corpus",
            "sources",
            "rag",
        )
    ):
        rationale.append("Knowledge / retrieval language → primary_task_type=rag_qa")
        return "rag_qa", secondary
    if any(k in low for k in ("classify", "classification", "label", "categor")):
        rationale.append("Classification language → primary_task_type=classification")
        return "classification", secondary
    if any(k in low for k in ("extract", "extraction", "structured", "fields", "schema")):
        rationale.append("Extraction language → primary_task_type=structured_extraction")
        return "structured_extraction", secondary
    if any(k in low for k in ("agent", "orchestrat", "multi-step", "planner")):
        rationale.append("Agentic language → primary_task_type=agentic")
        secondary.append("tool_use_likely")
        return "agentic", secondary
    rationale.append("No strong task cue → primary_task_type=general_assistant")
    return "general_assistant", secondary


def _flag_grounding(low: str, rationale: list[str]) -> str | None:
    if any(
        k in low
        for k in (
            "citation",
            "cite",
            "ground",
            "source",
            "hallucinat",
            "audit",
            "compliance",
            "evidence",
        )
    ):
        rationale.append("Audit / grounding language → grounding_requirement=high")
        return "high"
    return None


def _flag_latency(low: str, rationale: list[str]) -> str | None:
    if any(
        k in low
        for k in (
            "real-time",
            "realtime",
            "low latency",
            "milliseconds",
            "interactive",
            "live",
            "sub-second",
        )
    ):
        rationale.append("Latency language → latency_sensitivity=high")
        return "high"
    return None


def _flag_cost(low: str, rationale: list[str]) -> str | None:
    if any(k in low for k in ("cheap", "low cost", "budget", "cost-sensitive", "minimize cost")):
        rationale.append("Cost language → cost_sensitivity=high")
        return "high"
    return None


def _flag_privacy(low: str, rationale: list[str]) -> tuple[str | None, str | None]:
    if any(k in low for k in ("pii", "hipaa", "gdpr", "phi", "classified", "confidential")):
        rationale.append("Sensitive-data language → security_sensitivity=high, privacy_level=elevated")
        return "high", "elevated"
    return None, None


def _flag_hitl(low: str, rationale: list[str]) -> str | None:
    if any(
        k in low
        for k in (
            "human review",
            "human-in-the-loop",
            "human in the loop",
            "manual approval",
            "approve before",
        )
    ):
        rationale.append("HITL language → human_in_loop_requirement=required")
        return "required"
    return None


def _flag_tools(low: str, rationale: list[str]) -> str | None:
    if any(
        k in low
        for k in (
            "api integration",
            "call an api",
            "function calling",
            "tool use",
            "external system",
        )
    ):
        rationale.append("Integration language → tool_use_requirement=likely")
        return "likely"
    return None


def _flag_deployment(low: str, rationale: list[str]) -> str | None:
    if "on-prem" in low or "on prem" in low or "onpremises" in low or "on premises" in low:
        rationale.append("On-prem language → deployment_preference=on_premises")
        return "on_premises"
    if "vpc" in low or "private cloud" in low:
        rationale.append("Private network language → deployment_preference=private_cloud")
        return "private_cloud"
    return None
