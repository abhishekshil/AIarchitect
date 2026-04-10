"""Rule-based onboarding TaskGraph from template + capabilities (replace with data-driven templates)."""

from __future__ import annotations

import uuid
from collections import defaultdict, deque

from solution_planning_api.domain import (
    ArchitectureTemplate,
    CapabilityBlock,
    ConstraintProfile,
    RequirementProfile,
    SolutionCandidate,
    TaskGraph,
    TaskGraphEdge,
    TaskGraphNode,
)
from solution_planning_api.domain.common import JsonObject


class HeuristicTaskGraphBuilder:
    """Builds structured onboarding nodes/edges; extensible via registry metadata later."""

    def build(
        self,
        *,
        candidate: SolutionCandidate,
        requirement: RequirementProfile,
        constraint: ConstraintProfile | None,
        template: ArchitectureTemplate,
        capabilities_by_id: dict[str, CapabilityBlock],
    ) -> TaskGraph:
        graph_id = uuid.uuid4()
        cap_set = list(dict.fromkeys(candidate.capability_set))  # preserve order, dedupe

        required = [c for c in template.required_capabilities if c in cap_set]
        optional = [c for c in template.optional_capabilities if c in cap_set]

        ordered_required = _topo_capability_order(required, capabilities_by_id)
        ordered_optional = _topo_capability_order(optional, capabilities_by_id)

        nodes: list[TaskGraphNode] = []
        edges: list[TaskGraphEdge] = []

        guidance: list[str] = []
        if template.onboarding_template_ref:
            guidance.append(template.onboarding_template_ref)
        guidance.append("blueprint/onboarding/overview")

        align_id = "task:template_alignment"
        nodes.append(
            TaskGraphNode(
                node_id=align_id,
                title="Confirm architecture pattern",
                description=(
                    f"Align implementation steps with “{template.visible_label or template.name}” "
                    f"({template.template_id})."
                ),
                task_type="template_alignment",
                metadata={"template_id": template.template_id},
                guidance_refs=[r for r in [template.onboarding_template_ref] if r],
            )
        )
        prev = align_id

        last_required_node: str | None = None
        for cid in ordered_required:
            nid = f"task:capability:{cid}"
            block = capabilities_by_id.get(cid)
            title = block.name if block else cid.replace("_", " ").title()
            desc = block.description if block else None
            nodes.append(
                TaskGraphNode(
                    node_id=nid,
                    title=f"Configure: {title}",
                    description=desc,
                    task_type="capability_onboarding",
                    metadata={"capability_id": cid, "category": block.category if block else None},
                    guidance_refs=[f"registry/capability/{cid}"],
                )
            )
            edges.append(TaskGraphEdge(source_id=prev, target_id=nid))
            prev = nid
            last_required_node = nid

        anchor = last_required_node or align_id
        for cid in ordered_optional:
            nid = f"task:capability:{cid}"
            block = capabilities_by_id.get(cid)
            title = block.name if block else cid.replace("_", " ").title()
            desc = block.description if block else None
            nodes.append(
                TaskGraphNode(
                    node_id=nid,
                    title=f"Optional: {title}",
                    description=desc,
                    task_type="optional_capability_onboarding",
                    metadata={"capability_id": cid, "optional": True},
                    guidance_refs=[f"registry/capability/{cid}"],
                    condition="optional_capability",
                )
            )
            edges.append(TaskGraphEdge(source_id=anchor, target_id=nid))

        cross_cutting: list[JsonObject] = []

        if constraint and constraint.privacy_level == "elevated":
            nid = "task:privacy_controls"
            nodes.append(
                TaskGraphNode(
                    node_id=nid,
                    title="Privacy & data controls",
                    description="Document residency, retention, and access boundaries for sensitive data.",
                    task_type="compliance_review",
                    metadata={"trigger": "constraint.privacy_level_elevated"},
                    guidance_refs=["blueprint/constraints/privacy"],
                    condition="privacy_elevated",
                )
            )
            edges.append(TaskGraphEdge(source_id=align_id, target_id=nid))
            cross_cutting.append({"node_id": nid, "condition": "privacy_elevated"})

        if requirement.grounding_requirement == "high" and "retrieval" in cap_set:
            nid = "task:grounding_citations"
            nodes.append(
                TaskGraphNode(
                    node_id=nid,
                    title="Grounding & citation policy",
                    description="Define citation format, chunk attribution, and fallback when evidence is weak.",
                    task_type="quality_gate",
                    metadata={"trigger": "requirement.grounding_high"},
                    guidance_refs=["blueprint/quality/grounding"],
                    condition="high_grounding",
                )
            )
            edges.append(TaskGraphEdge(source_id=anchor, target_id=nid))
            cross_cutting.append({"node_id": nid, "condition": "high_grounding"})

        if requirement.human_in_loop_requirement == "required":
            nid = "task:human_review"
            nodes.append(
                TaskGraphNode(
                    node_id=nid,
                    title="Human-in-the-loop workflow",
                    description="Specify approval points, escalations, and audit trail for human reviewers.",
                    task_type="governance_onboarding",
                    metadata={"trigger": "requirement.human_in_loop_required"},
                    guidance_refs=["blueprint/governance/human_in_loop"],
                    condition="human_in_loop_required",
                )
            )
            edges.append(TaskGraphEdge(source_id=anchor, target_id=nid))
            cross_cutting.append({"node_id": nid, "condition": "human_in_loop_required"})

        dependencies: JsonObject = {
            "template_id": template.template_id,
            "capability_execution_order": ordered_required + ordered_optional,
            "required_capabilities": ordered_required,
            "optional_capabilities": ordered_optional,
            "cross_cutting": cross_cutting,
        }

        validation_rules: JsonObject = {
            "mandatory_path": "complete_template_alignment_and_required_capabilities",
            "conditional_nodes": "evaluate_condition_flags_in_phase_9",
            "extensibility": "add_nodes_via_task_graph_builder_implementation",
        }

        return TaskGraph(
            task_graph_id=graph_id,
            project_id=candidate.project_id,
            candidate_id=candidate.candidate_id,
            nodes=nodes,
            edges=edges,
            dependencies=dependencies,
            validation_rules=validation_rules,
            user_guidance_refs=guidance,
        )


def _topo_capability_order(
    cap_ids: list[str],
    cap_by_id: dict[str, CapabilityBlock],
) -> list[str]:
    present = set(cap_ids)
    if not present:
        return []

    indegree: dict[str, int] = {c: 0 for c in cap_ids}
    adj: dict[str, list[str]] = defaultdict(list)

    for c in cap_ids:
        block = cap_by_id.get(c)
        if not block:
            continue
        for p in block.prerequisites:
            if p in present:
                adj[p].append(c)
                indegree[c] += 1

    order_index = {c: i for i, c in enumerate(cap_ids)}
    queue = deque(sorted([c for c in cap_ids if indegree[c] == 0], key=lambda x: order_index[x]))
    out: list[str] = []

    while queue:
        n = queue.popleft()
        out.append(n)
        for m in sorted(adj[n], key=lambda x: order_index[x]):
            indegree[m] -= 1
            if indegree[m] == 0:
                queue.append(m)

    if len(out) != len(cap_ids):
        return list(cap_ids)
    return out
