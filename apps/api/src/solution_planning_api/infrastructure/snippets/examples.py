"""Architecture-aware example request/response bodies for docs and snippets."""

from __future__ import annotations

from typing import Any


def playground_example_for_pattern(
    *,
    architecture_pattern: str,
    project_id_str: str,
    runtime_graph_version: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (infer_request_body, infer_response_body) shaped like the live API."""
    req = {
        "runtime_graph_version": runtime_graph_version,
        "input_text": "What is the refund policy for enterprise accounts?",
    }
    base_resp = {
        "schema_version": "1.0",
        "inference_id": "00000000-0000-4000-8000-000000000001",
        "runtime_graph_id": "00000000-0000-4000-8000-000000000002",
        "runtime_graph_version": runtime_graph_version,
        "architecture_pattern": architecture_pattern,
        "output_text": "[example] Model output text…",
        "metadata": {
            "mock": True,
            "latency_ms": 12.5,
            "architecture_template_id": "example-template",
            "graph_node_count": 4,
        },
    }
    if architecture_pattern == "single_llm":
        resp = {
            **base_resp,
            "structured_output": None,
            "citations": [],
            "traces": [
                {
                    "step_index": 0,
                    "node_id": "primary_model",
                    "component_type": "model",
                    "action": "generate",
                    "detail": {"temperature": 0.2},
                }
            ],
        }
    elif architecture_pattern == "rag":
        resp = {
            **base_resp,
            "structured_output": None,
            "citations": [
                {
                    "citation_id": "c1",
                    "source_ref": f"doc://project/{project_id_str}/policy",
                    "snippet": "Refunds within 30 days…",
                    "score": 0.9,
                }
            ],
            "traces": [
                {
                    "step_index": 0,
                    "node_id": "knowledge_retriever",
                    "component_type": "retriever",
                    "action": "vector_search",
                    "detail": {"top_k": 5},
                }
            ],
            "metadata": {**base_resp["metadata"], "retrieval_hits": 1},
        }
    elif architecture_pattern == "structured":
        resp = {
            **base_resp,
            "output_text": "[example] See structured_output.",
            "structured_output": {
                "intent": "extract",
                "labels": [{"name": "topic", "value": "refund"}],
                "extracted_fields": {"summary": "User asks about refunds.", "confidence": 0.88},
            },
            "citations": [],
            "traces": [
                {
                    "step_index": 0,
                    "node_id": "intent_router",
                    "component_type": "router",
                    "action": "classify_intent",
                    "detail": {},
                }
            ],
        }
    else:  # hybrid
        resp = {
            **base_resp,
            "output_text": "[example] Refined answer after validation.",
            "structured_output": {"validator_warnings": [], "agent_steps": 1},
            "citations": [
                {
                    "citation_id": "h1",
                    "source_ref": "doc://evidence/section-3",
                    "snippet": "Evidence snippet…",
                    "score": 0.79,
                }
            ],
            "traces": [
                {
                    "step_index": 2,
                    "node_id": "answer_validator",
                    "component_type": "validator",
                    "action": "policy_check",
                    "detail": {"result": "pass"},
                },
                {
                    "step_index": 3,
                    "node_id": "refine_agent",
                    "component_type": "agent",
                    "action": "tool_refine",
                    "detail": {"tools": ["critic"]},
                },
            ],
            "metadata": {
                **base_resp["metadata"],
                "pipeline": "retriever→model→validator→agent→formatter",
            },
        }
    return req, resp
