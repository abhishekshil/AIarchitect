"""Application-layer task guidance hints for onboarding UI."""

from __future__ import annotations

from solution_planning_api.domain import TaskGraphNode


def ui_hints_for_node(node: TaskGraphNode) -> tuple[list[str], str]:
    """Return (suggestions, example_placeholder) for forms."""
    tt = node.task_type or "default"
    key = tt.lower()

    catalog: dict[str, tuple[list[str], str]] = {
        "template_alignment": (
            [
                "Name the primary user journeys this architecture must support.",
                "List non-negotiable SLAs or compliance drivers.",
                "Call out integrations you already have vs net-new.",
            ],
            "e.g. Confirm this RAG assistant pattern for internal policy Q&A with 5s P95 latency...",
        ),
        "capability_onboarding": (
            [
                "Document provider choice and why it fits your data residency rules.",
                "Note authentication method (API keys, IAM roles, VPC).",
                "Capture rollback / fallback if the capability is unavailable.",
            ],
            "e.g. Using OpenAI-compatible endpoint in us-east-1 with org-level key rotation...",
        ),
        "optional_capability_onboarding": (
            [
                "Skip if not needed for MVP; capture when you plan to enable it.",
                "Link to the runbook or ticket that tracks optional rollout.",
            ],
            "e.g. Defer reranking until corpus exceeds 50k chunks...",
        ),
        "compliance_review": (
            [
                "List data classes handled (PII, PHI, financial).",
                "Specify retention windows and encryption expectations.",
            ],
            "e.g. Customer emails only; 90-day retention; TLS 1.2+ in transit...",
        ),
        "quality_gate": (
            [
                "Define citation format and minimum evidence thresholds.",
                "Describe behavior when retrieval returns low-confidence chunks.",
            ],
            "e.g. Require inline [doc_id] citations; abstain if score < 0.35...",
        ),
        "governance_onboarding": (
            [
                "Map approval roles and escalation paths.",
                "Reference audit log destination and review cadence.",
            ],
            "e.g. Manager approves production prompts weekly via Jira workflow PROD-...",
        ),
        "default": (
            [
                "Summarize what you configured and any open risks.",
                "Link artifacts (diagrams, config repos) if available.",
            ],
            "e.g. Completed index provisioning; pending security review ticket #123...",
        ),
    }

    suggestions, placeholder = catalog.get(key, catalog["default"])
    return list(suggestions), placeholder
