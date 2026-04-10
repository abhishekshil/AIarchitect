from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from solution_planning_api.api.deps import CurrentUser, get_candidate_service
from solution_planning_api.api.schemas.recommendation import (
    ArchitectureRecommendationsEnvelope,
    envelope_for_candidates,
)
from solution_planning_api.application.services.candidate_service import CandidateService
from solution_planning_api.domain.scoring import ScoringMode

router = APIRouter(
    prefix="/{project_id}/requirements/{requirement_id}/candidates",
    tags=["candidates"],
)


@router.post(
    "/generate",
    response_model=ArchitectureRecommendationsEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def generate_candidates(
    project_id: UUID,
    requirement_id: UUID,
    current: CurrentUser,
    svc: Annotated[CandidateService, Depends(get_candidate_service)],
    scoring_mode: ScoringMode = ScoringMode.BEST_OVERALL,
) -> ArchitectureRecommendationsEnvelope:
    candidates = await svc.generate_candidates(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
        scoring_mode=scoring_mode,
    )
    return envelope_for_candidates(
        project_id=project_id,
        sort_mode=scoring_mode,
        candidates=candidates,
    )


@router.get("/", response_model=ArchitectureRecommendationsEnvelope)
async def list_candidates(
    project_id: UUID,
    requirement_id: UUID,
    current: CurrentUser,
    svc: Annotated[CandidateService, Depends(get_candidate_service)],
    sort_mode: ScoringMode = ScoringMode.BEST_OVERALL,
) -> ArchitectureRecommendationsEnvelope:
    candidates = await svc.list_candidates(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
        sort_mode=sort_mode,
    )
    return envelope_for_candidates(
        project_id=project_id,
        sort_mode=sort_mode,
        candidates=candidates,
    )
