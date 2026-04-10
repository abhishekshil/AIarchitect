from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from solution_planning_api.api.deps import CurrentUser, get_candidate_service
from solution_planning_api.api.schemas.recommendation import (
    ArchitectureRecommendationDetail,
    ArchitectureRecommendationOption,
    ArchitectureRecommendationsEnvelope,
    envelope_for_candidates,
)
from solution_planning_api.application.services.candidate_service import CandidateService
from solution_planning_api.domain.scoring import ScoringMode

router = APIRouter(prefix="/{project_id}/recommendations", tags=["recommendations"])


@router.post(
    "/generate",
    response_model=ArchitectureRecommendationsEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def generate_recommendations_for_project(
    project_id: UUID,
    current: CurrentUser,
    svc: Annotated[CandidateService, Depends(get_candidate_service)],
    scoring_mode: ScoringMode = ScoringMode.BEST_OVERALL,
    requirement_id: UUID | None = None,
) -> ArchitectureRecommendationsEnvelope:
    """Generate and persist architecture options (defaults to the latest requirement in the project)."""
    candidates = await svc.generate_recommendations_for_project(
        owner_user_id=current.user_id,
        project_id=project_id,
        scoring_mode=scoring_mode,
        requirement_id=requirement_id,
    )
    return envelope_for_candidates(
        project_id=project_id,
        sort_mode=scoring_mode,
        candidates=candidates,
    )


@router.get("/", response_model=ArchitectureRecommendationsEnvelope)
async def list_recommendations_for_project(
    project_id: UUID,
    current: CurrentUser,
    svc: Annotated[CandidateService, Depends(get_candidate_service)],
    sort_mode: ScoringMode = ScoringMode.BEST_OVERALL,
    requirement_id: UUID | None = None,
) -> ArchitectureRecommendationsEnvelope:
    """List persisted options: one requirement, or aggregated latest batches across the project."""
    candidates = await svc.list_recommendations_for_project(
        owner_user_id=current.user_id,
        project_id=project_id,
        sort_mode=sort_mode,
        requirement_id=requirement_id,
    )
    return envelope_for_candidates(
        project_id=project_id,
        sort_mode=sort_mode,
        candidates=candidates,
    )


@router.get("/{candidate_id}", response_model=ArchitectureRecommendationDetail)
async def get_recommendation_option(
    project_id: UUID,
    candidate_id: UUID,
    current: CurrentUser,
    svc: Annotated[CandidateService, Depends(get_candidate_service)],
) -> ArchitectureRecommendationDetail:
    """Fetch one persisted option by id (for detail views / selection flows)."""
    c = await svc.get_recommendation_option(
        owner_user_id=current.user_id,
        project_id=project_id,
        candidate_id=candidate_id,
    )
    return ArchitectureRecommendationDetail(
        option=ArchitectureRecommendationOption.from_candidate(c),
    )
