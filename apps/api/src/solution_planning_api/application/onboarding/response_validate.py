"""Application-layer onboarding response validation policies."""

from __future__ import annotations

from typing import Any

from solution_planning_api.domain.common import JsonObject


def validate_onboarding_response(
    *,
    task_type: str | None,
    response: JsonObject | None,
) -> tuple[list[str], list[str]]:
    """
    Return (errors, warnings). Empty errors means acceptable.
    Expects response shape: { "notes": str, ... }.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if response is None or not isinstance(response, dict):
        errors.append("Response must be a JSON object.")
        return errors, warnings

    notes = response.get("notes")
    if not isinstance(notes, str):
        errors.append('Field "notes" is required and must be a string.')
        return errors, warnings

    n = len(notes.strip())
    tt = (task_type or "").lower()

    min_len = 20
    if tt == "optional_capability_onboarding":
        min_len = 8
    elif tt == "template_alignment":
        min_len = 15
    elif tt in ("compliance_review", "quality_gate", "governance_onboarding"):
        min_len = 25

    if n < min_len:
        errors.append(f"Notes must be at least {min_len} non-whitespace characters for this task.")

    if n > 8000:
        errors.append("Notes must be at most 8000 characters.")

    artifacts = response.get("artifacts")
    if artifacts is not None and not isinstance(artifacts, list):
        errors.append('If provided, "artifacts" must be a list of strings or objects.')

    if isinstance(artifacts, list) and any(not isinstance(a, (str, dict)) for a in artifacts):
        errors.append("Each artifact entry must be a string or object.")

    if n > min_len * 4 and not errors:
        warnings.append("Consider linking concrete artifacts or tickets in addition to narrative notes.")

    return errors, warnings


def feedback_object(*, errors: list[str], warnings: list[str], status: str) -> dict[str, Any]:
    return {"status": status, "errors": errors, "warnings": warnings}
