"""Infer high-level architecture pattern from a compiled runtime graph."""

from __future__ import annotations

from solution_planning_api.domain.runtime_graph import RuntimeGraph


def infer_architecture_pattern_from_runtime_graph(graph: RuntimeGraph) -> str:
    """Rough pattern used for mock inference and client snippet hints."""
    types = {n.component_type for n in graph.nodes}
    if "retriever" in types and "validator" in types and "agent" in types:
        return "hybrid"
    if "retriever" in types:
        return "rag"
    if "router" in types:
        return "structured"
    return "single_llm"
