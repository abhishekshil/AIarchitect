"""Mock-structured RuntimeGraph from architecture template + onboarding TaskGraph (Phase 10)."""

from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from solution_planning_api.application.ports.runtime_graph_building import RuntimeGraphBuilder
from solution_planning_api.domain import (
    ArchitectureTemplate,
    RuntimeGraph,
    RuntimeGraphEdge,
    RuntimeGraphNode,
    SolutionCandidate,
    TaskGraph,
)
from solution_planning_api.domain.common import JsonObject
from solution_planning_api.domain.runtime_component import RuntimeComponentType


def _edge(source_id: str, target_id: str, relation: str = "dataflow") -> RuntimeGraphEdge:
    return RuntimeGraphEdge(
        source_id=source_id,
        target_id=target_id,
        relation=relation,
        metadata={"mock": True},
    )


def _node(
    node_id: str,
    component_type: RuntimeComponentType,
    label: str,
    **config: Any,
) -> RuntimeGraphNode:
    cfg: JsonObject = {"mock": True, **config}
    return RuntimeGraphNode(
        node_id=node_id,
        component_type=component_type.value,
        label=label,
        config=cfg,
    )


class HeuristicRuntimeGraphBuilder(RuntimeGraphBuilder):
    """Deterministic graph shapes per template family; swap for codegen / LLM later."""

    def build(
        self,
        *,
        requirement_id: UUID | None,
        template: ArchitectureTemplate,
        candidate: SolutionCandidate,
        task_graph: TaskGraph | None,
    ) -> RuntimeGraph:
        meta = template.metadata or {}
        family = str(meta.get("family", "")).lower()
        tid = template.template_id.lower()

        if "rag_validator" in tid or family == "hybrid":
            nodes, edges = _hybrid_chain(template, candidate)
        elif "rag" in tid or family == "rag":
            nodes, edges = _rag_chain(template, candidate)
        elif "classification" in tid or family == "structured":
            nodes, edges = _structured_chain(template, candidate)
        else:
            nodes, edges = _single_llm_chain(template, candidate)

        onboarding_nodes = len(task_graph.nodes) if task_graph else 0
        return RuntimeGraph(
            runtime_graph_id=uuid.uuid4(),
            project_id=candidate.project_id,
            candidate_id=candidate.candidate_id,
            requirement_id=requirement_id,
            version=1,
            nodes=nodes,
            edges=edges,
            provider_bindings={
                "mode": "mock",
                "architecture_template_id": template.template_id,
                "runtime_template_ref": template.runtime_graph_template_ref,
                "capability_set": candidate.capability_set,
            },
            observability={
                "build_engine": "heuristic_runtime_graph_v1",
                "onboarding_task_node_count": onboarding_nodes,
            },
            failure_handling={"default_strategy": "abort", "retryable": False},
        )


def _single_llm_chain(
    template: ArchitectureTemplate, candidate: SolutionCandidate
) -> tuple[list[RuntimeGraphNode], list[RuntimeGraphEdge]]:
    nodes = [
        _node(
            "primary_model",
            RuntimeComponentType.MODEL,
            "Primary LLM",
            role="generation",
            template_id=template.template_id,
        ),
        _node(
            "response_formatter",
            RuntimeComponentType.FORMATTER,
            "Output formatter",
            format="markdown_or_json",
        ),
    ]
    edges = [_edge("primary_model", "response_formatter")]
    return nodes, edges


def _rag_chain(
    template: ArchitectureTemplate, candidate: SolutionCandidate
) -> tuple[list[RuntimeGraphNode], list[RuntimeGraphEdge]]:
    nodes = [
        _node(
            "knowledge_retriever",
            RuntimeComponentType.RETRIEVER,
            "Knowledge retriever",
            index="mock_vector_index",
        ),
        _node(
            "generation_model",
            RuntimeComponentType.MODEL,
            "RAG generation model",
            role="grounded_generation",
            template_id=template.template_id,
        ),
        _node(
            "citation_formatter",
            RuntimeComponentType.FORMATTER,
            "Citations & answer formatter",
            citations=True,
        ),
    ]
    edges = [
        _edge("knowledge_retriever", "generation_model"),
        _edge("generation_model", "citation_formatter"),
    ]
    return nodes, edges


def _structured_chain(
    template: ArchitectureTemplate, candidate: SolutionCandidate
) -> tuple[list[RuntimeGraphNode], list[RuntimeGraphEdge]]:
    nodes = [
        _node(
            "intent_router",
            RuntimeComponentType.ROUTER,
            "Intent / route selector",
            routes=["classify", "extract"],
        ),
        _node(
            "structured_model",
            RuntimeComponentType.MODEL,
            "Classification / extraction model",
            role="structured_output",
            template_id=template.template_id,
        ),
        _node(
            "schema_formatter",
            RuntimeComponentType.FORMATTER,
            "Schema-normalized output",
            strict_json=True,
        ),
    ]
    edges = [
        _edge("intent_router", "structured_model"),
        _edge("structured_model", "schema_formatter"),
    ]
    return nodes, edges


def _hybrid_chain(
    template: ArchitectureTemplate, candidate: SolutionCandidate
) -> tuple[list[RuntimeGraphNode], list[RuntimeGraphEdge]]:
    nodes = [
        _node(
            "hybrid_retriever",
            RuntimeComponentType.RETRIEVER,
            "Retriever",
            index="mock_hybrid_index",
        ),
        _node(
            "draft_model",
            RuntimeComponentType.MODEL,
            "Draft generator",
            role="draft",
        ),
        _node(
            "answer_validator",
            RuntimeComponentType.VALIDATOR,
            "Answer validator",
            policy="mock_policy_pack",
        ),
        _node(
            "refine_agent",
            RuntimeComponentType.AGENT,
            "Refinement agent",
            tools=["mock_critic", "mock_search"],
        ),
        _node(
            "final_formatter",
            RuntimeComponentType.FORMATTER,
            "Final response formatter",
            citations=True,
        ),
    ]
    edges = [
        _edge("hybrid_retriever", "draft_model"),
        _edge("draft_model", "answer_validator"),
        _edge("answer_validator", "refine_agent"),
        _edge("refine_agent", "final_formatter"),
    ]
    return nodes, edges
