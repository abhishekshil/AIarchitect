"""Compatibility wrapper for onboarding validation helpers.

Prefer imports from `solution_planning_api.application.onboarding`.
"""

from solution_planning_api.application.onboarding.response_validate import (
    feedback_object,
    validate_onboarding_response,
)

__all__ = ["feedback_object", "validate_onboarding_response"]
