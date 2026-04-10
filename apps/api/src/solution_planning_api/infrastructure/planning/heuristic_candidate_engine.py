"""Heuristic candidate synthesis and explainable multi-mode scoring."""

from __future__ import annotations

import uuid
from typing import Any

from solution_planning_api.application.ports.candidate_planning import CandidatePlanningEngine
from solution_planning_api.domain import (
    ArchitectureTemplate,
    CapabilityBlock,
    ConstraintProfile,
    RequirementProfile,
    SolutionCandidate,
)
from solution_planning_api.domain.common import JsonObject
from solution_planning_api.domain.scoring import ScoringMode
from solution_planning_api.infrastructure.planning.llm_candidate_explainer import LLMCandidateExplainer

MODE_WEIGHTS: dict[ScoringMode, dict[str, float]] = {
    ScoringMode.BEST_OVERALL: {"fit": 0.25, "cost": 0.25, "launch": 0.25, "quality": 0.25},
    ScoringMode.LOWEST_COST: {"fit": 0.15, "cost": 0.55, "launch": 0.2, "quality": 0.1},
    ScoringMode.FASTEST_LAUNCH: {"fit": 0.15, "cost": 0.2, "launch": 0.55, "quality": 0.1},
    ScoringMode.HIGHEST_QUALITY: {"fit": 0.2, "cost": 0.1, "launch": 0.15, "quality": 0.55},
}

# Archetype baselines: cost/launch/quality are "higher is better" (cost = cost-efficiency).
ARCHETYPE_SCORES: dict[str, dict[str, float]] = {
    "single_llm": {"cost": 0.92, "launch": 0.95, "quality": 0.62, "complexity": 0.15},
    "rag": {"cost": 0.58, "launch": 0.62, "quality": 0.88, "complexity": 0.5},
    "structured": {"cost": 0.78, "launch": 0.82, "quality": 0.72, "complexity": 0.4},
    "hybrid": {"cost": 0.42, "launch": 0.48, "quality": 0.93, "complexity": 0.88},
}

TASK_TEMPLATE_AFFINITY: dict[str, dict[str, float]] = {
    "rag_qa": {"rag_assistant": 1.0, "rag_validator_agent_workflow": 0.85, "single_llm_assistant": 0.35},
    "general_assistant": {"single_llm_assistant": 1.0, "rag_assistant": 0.55, "classification_extraction_workflow": 0.25},
    "classification": {"classification_extraction_workflow": 1.0, "single_llm_assistant": 0.6, "rag_assistant": 0.35},
    "structured_extraction": {"classification_extraction_workflow": 0.95, "rag_assistant": 0.65, "single_llm_assistant": 0.45},
    "agentic": {"rag_validator_agent_workflow": 1.0, "rag_assistant": 0.55, "single_llm_assistant": 0.35},
}


class HeuristicCandidatePlanningEngine(CandidatePlanningEngine):
    """Rule-based planner; replace with graph search / LLM planner using the same protocol."""

    def __init__(self, explainer: LLMCandidateExplainer | None = None) -> None:
        self._explainer = explainer or LLMCandidateExplainer(None)

    async def synthesize_and_score(
        self,
        *,
        requirement: RequirementProfile,
        constraint: ConstraintProfile | None,
        templates: list[ArchitectureTemplate],
        capabilities: list[CapabilityBlock],
        generation_mode: ScoringMode,
    ) -> list[SolutionCandidate]:
        cap_by_id = {c.capability_id: c for c in capabilities}
        tpl_by_id = {t.template_id: t for t in templates}
        selected_ids = _select_template_ids(requirement, tpl_by_id)
        out: list[SolutionCandidate] = []
        for tid in selected_ids:
            tpl = tpl_by_id[tid]
            archetype = _archetype_for_template(tpl)
            base = dict(ARCHETYPE_SCORES[archetype])
            fit, fit_rationale = _fit_score(requirement, tpl)
            dim_cost, r_cost = _adjust_cost(requirement, constraint, base["cost"], tpl, cap_by_id)
            dim_launch, r_launch = _adjust_launch(requirement, base["launch"], archetype)
            dim_quality, r_quality = _adjust_quality(requirement, base["quality"], tpl)
            dimensions = {
                "fit": {"score": round(fit, 4), "rationale": fit_rationale},
                "cost": {"score": round(dim_cost, 4), "rationale": r_cost},
                "launch": {"score": round(dim_launch, 4), "rationale": r_launch},
                "quality": {"score": round(dim_quality, 4), "rationale": r_quality},
            }
            composite_by_mode: dict[str, float] = {}
            for mode, weights in MODE_WEIGHTS.items():
                composite_by_mode[mode.value] = round(
                    sum(dimensions[k]["score"] * weights[k] for k in weights),
                    4,
                )
            primary = composite_by_mode[generation_mode.value]
            score_breakdown: JsonObject = {
                "dimensions": dimensions,
                "weights_reference": {k.value: v for k, v in MODE_WEIGHTS.items()},
                "composite_by_mode": composite_by_mode,
                "generation_mode": generation_mode.value,
            }
            tradeoffs, assumptions = _tradeoffs_and_assumptions(requirement, constraint, tpl, archetype)
            summary = _summary_text(requirement, tpl, dimensions, primary)
            reasoning = _reasoning_summary(dimensions, generation_mode)
            graph = _stub_graph(tpl, cap_by_id)
            cand = SolutionCandidate(
                candidate_id=uuid.uuid4(),
                project_id=requirement.project_id,
                requirement_id=requirement.requirement_id,
                candidate_type="architecture_template",
                title=tpl.visible_label or tpl.name,
                summary=summary,
                capability_set=tpl.required_capabilities + tpl.optional_capabilities[:4],
                architecture_template_ref=tpl.template_id,
                synthesized_graph=graph,
                assumptions=assumptions,
                tradeoffs=tradeoffs,
                suitability_score=primary,
                cost_estimate=_cost_json(archetype, dim_cost, tpl),
                complexity_estimate=_complexity_json(base["complexity"], archetype),
                latency_estimate=_latency_json(dim_launch, archetype),
                governance_score=_governance_score(constraint, tpl),
                reasoning_summary=reasoning,
                score_breakdown=score_breakdown,
            )
            cand = await self._explainer.enrich(cand)
            out.append(cand)

        out.sort(
            key=lambda c: (c.score_breakdown or {}).get("composite_by_mode", {}).get(generation_mode.value, 0.0),
            reverse=True,
        )
        return out


def _archetype_for_template(tpl: ArchitectureTemplate) -> str:
    meta = tpl.metadata or {}
    family = str(meta.get("family", "")).lower()
    if family in ARCHETYPE_SCORES:
        return family
    if tpl.template_id in ("single_llm_assistant",):
        return "single_llm"
    if tpl.template_id in ("rag_assistant",):
        return "rag"
    if tpl.template_id in ("classification_extraction_workflow",):
        return "structured"
    return "hybrid"


def _select_template_ids(
    requirement: RequirementProfile,
    tpl_by_id: dict[str, ArchitectureTemplate],
) -> list[str]:
    pt = (requirement.primary_task_type or "general_assistant").lower()
    aff = TASK_TEMPLATE_AFFINITY.get(pt, TASK_TEMPLATE_AFFINITY["general_assistant"])
    ranked = sorted(
        aff.items(),
        key=lambda kv: kv[1],
        reverse=True,
    )
    chosen: list[str] = []
    for tid, _ in ranked:
        if tid in tpl_by_id and tid not in chosen:
            chosen.append(tid)
    if "single_llm_assistant" in tpl_by_id and "single_llm_assistant" not in chosen:
        chosen.append("single_llm_assistant")
    for tid in tpl_by_id:
        if tid not in chosen and len(chosen) < 4:
            chosen.append(tid)
    return chosen[:4]


def _fit_score(req: RequirementProfile, tpl: ArchitectureTemplate) -> tuple[float, str]:
    pt = (req.primary_task_type or "general_assistant").lower()
    aff = TASK_TEMPLATE_AFFINITY.get(pt, TASK_TEMPLATE_AFFINITY["general_assistant"])
    base = aff.get(tpl.template_id, 0.45)
    notes: list[str] = []
    if req.grounding_requirement == "high" and "rag" in tpl.template_id:
        base = min(1.0, base + 0.12)
        notes.append("Grounding-sensitive requirement favors this pattern.")
    if req.latency_sensitivity == "high" and tpl.template_id == "single_llm_assistant":
        base = min(1.0, base + 0.1)
        notes.append("Latency-sensitive requirement favors a lean single-LLM path.")
    if req.tool_use_requirement == "likely" and "validator" in tpl.template_id:
        base = min(1.0, base + 0.08)
        notes.append("Tool/integration cues align with validator/agent workflows.")
    rationale = " ".join(notes) if notes else f"Template fit from primary task type `{pt}`."
    return max(0.0, min(1.0, base)), rationale


def _adjust_cost(
    req: RequirementProfile,
    con: ConstraintProfile | None,
    base: float,
    tpl: ArchitectureTemplate,
    caps: dict[str, CapabilityBlock],
) -> tuple[float, str]:
    score = base
    parts: list[str] = []
    if req.cost_sensitivity == "high":
        score += 0.08
        parts.append("Cost sensitivity boosts templates with lower operational surface.")
    if con and con.max_cost_per_request is not None:
        score += 0.05
        parts.append("Explicit per-request cost ceiling — prefer smaller graphs.")
    extra_caps = len([c for c in tpl.required_capabilities if c in caps])
    score -= 0.02 * max(0, extra_caps - 3)
    parts.append("Adjusted for number of required capabilities (more moving parts → higher cost risk).")
    return max(0.0, min(1.0, score)), " ".join(parts)


def _adjust_launch(req: RequirementProfile, base: float, archetype: str) -> tuple[float, str]:
    score = base
    if req.automation_depth in ("high", "full"):
        score -= 0.05
    if archetype == "single_llm":
        score += 0.03
    return max(0.0, min(1.0, score)), (
        "Launch score reflects integration count, template family, and automation depth."
    )


def _adjust_quality(req: RequirementProfile, base: float, tpl: ArchitectureTemplate) -> tuple[float, str]:
    score = base
    if req.grounding_requirement == "high" and "rag" in tpl.template_id:
        score += 0.1
    if "validation" in tpl.required_capabilities:
        score += 0.07
    if req.traceability_requirement == "high":
        score += 0.05
    return max(0.0, min(1.0, score)), (
        "Quality score emphasizes grounding, validation gates, and traceability hooks when present."
    )


def _tradeoffs_and_assumptions(
    req: RequirementProfile,
    con: ConstraintProfile | None,
    tpl: ArchitectureTemplate,
    archetype: str,
) -> tuple[list[str], list[str]]:
    tradeoffs: list[str] = []
    assumptions: list[str] = []
    if archetype == "single_llm":
        tradeoffs.append("Fastest path, but weaker factual grounding without retrieval.")
    elif archetype == "rag":
        tradeoffs.append("Better grounding; higher latency and indexing toil.")
    elif archetype == "structured":
        tradeoffs.append("Great for structured I/O; less flexible for open-ended chat.")
    else:
        tradeoffs.append("Highest assurance; most moving parts and operational cost.")
    if con and con.privacy_level == "elevated":
        assumptions.append("Assumes data residency and access controls can be enforced for all components.")
    assumptions.append(f"Assumes providers exist for: {', '.join(tpl.required_capabilities[:5])}.")
    if req.human_in_loop_requirement == "required":
        tradeoffs.append("Human approvals add latency but reduce governance risk.")
    return tradeoffs, assumptions


def _summary_text(
    req: RequirementProfile,
    tpl: ArchitectureTemplate,
    dimensions: dict[str, Any],
    primary: float,
) -> str:
    return (
        f"{tpl.name} for a `{req.primary_task_type or 'general'}` workload. "
        f"Composite ({primary:.2f}) balances fit ({dimensions['fit']['score']:.2f}), "
        f"cost efficiency ({dimensions['cost']['score']:.2f}), "
        f"time-to-launch ({dimensions['launch']['score']:.2f}), "
        f"and quality ({dimensions['quality']['score']:.2f})."
    )


def _reasoning_summary(dimensions: dict[str, Any], mode: ScoringMode) -> str:
    w = MODE_WEIGHTS[mode]
    ranked = sorted(
        dimensions.items(),
        key=lambda kv: kv[1]["score"] * w.get(kv[0], 0.0),
        reverse=True,
    )
    top = ranked[0][0]
    second = ranked[1][0] if len(ranked) > 1 else top
    return (
        f"Mode `{mode.value}` up-weights {top} and {second}. "
        f"{dimensions[top]['rationale']} {dimensions[second]['rationale']}"
    )


def _stub_graph(
    tpl: ArchitectureTemplate,
    caps: dict[str, CapabilityBlock],
) -> JsonObject:
    nodes: list[JsonObject] = [
        {"id": "ingress", "component_type": "api_gateway", "label": "Ingress"},
        {
            "id": "core",
            "component_type": "llm_orchestrator",
            "label": tpl.name,
            "template_id": tpl.template_id,
        },
        {"id": "egress", "component_type": "response_sink", "label": "Client"},
    ]
    for i, cid in enumerate(tpl.required_capabilities[:5]):
        c = caps.get(cid)
        nodes.append(
            {
                "id": f"cap_{i}",
                "component_type": "capability",
                "capability_id": cid,
                "label": c.name if c else cid,
            }
        )
    edges: list[JsonObject] = [
        {"source_id": "ingress", "target_id": "core"},
        {"source_id": "core", "target_id": "egress"},
    ]
    return {"template_id": tpl.template_id, "nodes": nodes, "edges": edges}


def _cost_json(archetype: str, dim_cost: float, tpl: ArchitectureTemplate) -> JsonObject:
    tier = "low" if archetype == "single_llm" else "medium" if archetype in ("structured", "rag") else "high"
    return {
        "tier": tier,
        "score": round(dim_cost, 4),
        "notes": f"Relative cost efficiency for `{tpl.template_id}`; not a currency estimate.",
    }


def _complexity_json(complexity: float, archetype: str) -> JsonObject:
    return {
        "relative": round(complexity, 4),
        "archetype": archetype,
        "notes": "0=minimal moving parts, 1=heavy orchestration.",
    }


def _latency_json(dim_launch: float, archetype: str) -> JsonObject:
    return {
        "relative": round(1.0 - (1.0 - dim_launch) * 0.5, 4),
        "notes": "Proxy for end-to-end latency risk (higher launch score → lower latency risk).",
        "archetype": archetype,
    }


def _governance_score(con: ConstraintProfile | None, tpl: ArchitectureTemplate) -> float:
    score = 0.55
    if "validation" in tpl.required_capabilities:
        score += 0.15
    if con and con.required_auditability:
        score += 0.1
    if con and con.privacy_level == "elevated":
        score += 0.1
    return max(0.0, min(1.0, score))
