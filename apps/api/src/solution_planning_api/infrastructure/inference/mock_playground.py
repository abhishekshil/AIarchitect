"""Architecture-aware mocked inference for the playground (Phase 11)."""

from __future__ import annotations

import hashlib
import time
from typing import Any

from solution_planning_api.application.ports.inference_simulation import PlaygroundInferenceSimulator
from solution_planning_api.domain import RuntimeGraph
from solution_planning_api.domain.architecture_pattern import infer_architecture_pattern_from_runtime_graph


def _base_metadata(graph: RuntimeGraph, started: float) -> dict[str, Any]:
    pb = graph.provider_bindings or {}
    return {
        "mock": True,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "architecture_template_id": pb.get("architecture_template_id"),
        "runtime_template_ref": pb.get("runtime_template_ref"),
        "graph_node_count": len(graph.nodes),
        "graph_edge_count": len(graph.edges),
    }


class MockPlaygroundInferenceSimulator(PlaygroundInferenceSimulator):
    """Returns deterministic-ish payloads per runtime graph shape."""

    def run(self, *, graph: RuntimeGraph, input_text: str) -> dict[str, Any]:
        started = time.perf_counter()
        pattern = infer_architecture_pattern_from_runtime_graph(graph)
        if pattern == "hybrid":
            body = _run_hybrid(graph, input_text, started)
        elif pattern == "rag":
            body = _run_rag(graph, input_text, started)
        elif pattern == "structured":
            body = _run_structured(graph, input_text, started)
        else:
            body = _run_single_llm(graph, input_text, started)
        body["architecture_pattern"] = pattern
        return body


def _run_single_llm(graph: RuntimeGraph, input_text: str, started: float) -> dict[str, Any]:
    traces = [
        _trace(0, "primary_model", "model", "generate", {"temperature": 0.2}),
        _trace(1, "response_formatter", "formatter", "format_output", {"style": "markdown"}),
    ]
    return {
        "output_text": f"[mock single_llm] {input_text.strip()[:500]}",
        "structured_output": None,
        "citations": [],
        "traces": traces,
        "metadata": _base_metadata(graph, started),
    }


def _run_rag(graph: RuntimeGraph, input_text: str, started: float) -> dict[str, Any]:
    qhash = hashlib.sha256(input_text.encode()).hexdigest()[:12]
    traces = [
        _trace(0, "knowledge_retriever", "retriever", "vector_search", {"top_k": 5}),
        _trace(1, "generation_model", "model", "grounded_generate", {"citations": True}),
        _trace(2, "citation_formatter", "formatter", "attach_citations", {}),
    ]
    citations = [
        _citation("c1", f"doc://policies/chunk-{qhash[:6]}", "Policy excerpt A (mock retrieval hit).", 0.91),
        _citation("c2", f"doc://kb/faq-{qhash[6:12]}", "FAQ snippet B supporting the answer.", 0.84),
    ]
    return {
        "output_text": (
            f"[mock rag] Based on retrieved context, here is a concise answer about: "
            f"{input_text.strip()[:120]}…"
        ),
        "structured_output": None,
        "citations": citations,
        "traces": traces,
        "metadata": {**_base_metadata(graph, started), "retrieval_hits": len(citations)},
    }


def _run_structured(graph: RuntimeGraph, input_text: str, started: float) -> dict[str, Any]:
    traces = [
        _trace(0, "intent_router", "router", "classify_intent", {"candidates": ["label", "extract"]}),
        _trace(1, "structured_model", "model", "structured_completion", {"schema": "mock_v1"}),
        _trace(2, "schema_formatter", "formatter", "validate_json", {"strict": True}),
    ]
    structured = {
        "intent": "extract",
        "labels": [{"name": "topic", "value": "general"}],
        "extracted_fields": {
            "summary": input_text.strip()[:240],
            "confidence": 0.88,
        },
    }
    return {
        "output_text": "[mock structured] See structured_output for machine-readable result.",
        "structured_output": structured,
        "citations": [],
        "traces": traces,
        "metadata": _base_metadata(graph, started),
    }


def _run_hybrid(graph: RuntimeGraph, input_text: str, started: float) -> dict[str, Any]:
    traces = [
        _trace(0, "hybrid_retriever", "retriever", "hybrid_search", {"index": "mock_hybrid"}),
        _trace(1, "draft_model", "model", "draft_answer", {}),
        _trace(2, "answer_validator", "validator", "policy_check", {"result": "pass_with_warnings"}),
        _trace(3, "refine_agent", "agent", "tool_refine", {"tools": ["mock_critic"]}),
        _trace(4, "final_formatter", "formatter", "final_format", {"citations": True}),
    ]
    citations = [
        _citation("h1", "doc://evidence/section-3", "Supporting evidence used after validation.", 0.79),
    ]
    return {
        "output_text": (
            f"[mock rag+validator+agent] Refined answer after validation loop for: "
            f"{input_text.strip()[:100]}…"
        ),
        "structured_output": {"validator_warnings": ["tone slightly informal"], "agent_steps": 1},
        "citations": citations,
        "traces": traces,
        "metadata": {
            **_base_metadata(graph, started),
            "pipeline": "retriever→model→validator→agent→formatter",
        },
    }


def _trace(
    step_index: int,
    node_id: str | None,
    component_type: str | None,
    action: str,
    detail: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step_index": step_index,
        "node_id": node_id,
        "component_type": component_type,
        "action": action,
        "detail": detail,
    }


def _citation(citation_id: str, source_ref: str, snippet: str, score: float) -> dict[str, Any]:
    return {
        "citation_id": citation_id,
        "source_ref": source_ref,
        "snippet": snippet,
        "score": score,
    }
