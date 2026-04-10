from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from solution_planning_api.api.deps import CurrentUser, get_requirement_service
from solution_planning_api.api.schemas.requirement import (
    RequirementDetailResponse,
    RequirementSubmitRequest,
    RequirementSubmitResponse,
    RequirementSummaryResponse,
    revision_to_response,
    revision_to_summary,
    submission_to_response,
)
from solution_planning_api.application.errors import NotFoundError
from solution_planning_api.application.services.requirement_service import RequirementService
from solution_planning_api.domain import ConstraintProfile

router = APIRouter(prefix="/{project_id}/requirements", tags=["requirements"])


@router.post("/", response_model=RequirementSubmitResponse, status_code=status.HTTP_201_CREATED)
async def submit_requirement(
    project_id: UUID,
    body: RequirementSubmitRequest,
    current: CurrentUser,
    svc: Annotated[RequirementService, Depends(get_requirement_service)],
) -> RequirementSubmitResponse:
    result = await svc.submit_raw_requirement(
        owner_user_id=current.user_id,
        project_id=project_id,
        raw_text=body.raw_text,
    )
    return submission_to_response(result)


@router.get("/latest", response_model=RequirementDetailResponse)
async def get_latest_requirement(
    project_id: UUID,
    current: CurrentUser,
    svc: Annotated[RequirementService, Depends(get_requirement_service)],
) -> RequirementDetailResponse:
    rev = await svc.get_latest_requirement(owner_user_id=current.user_id, project_id=project_id)
    constraint = await svc.get_constraint_for_requirement(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=rev.requirement_id,
    )
    return RequirementDetailResponse(
        revision=revision_to_response(rev),
        constraint_profile=constraint,
    )


@router.get("/", response_model=list[RequirementSummaryResponse])
async def list_requirements(
    project_id: UUID,
    current: CurrentUser,
    svc: Annotated[RequirementService, Depends(get_requirement_service)],
) -> list[RequirementSummaryResponse]:
    rows = await svc.list_requirements(owner_user_id=current.user_id, project_id=project_id)
    return [revision_to_summary(r) for r in rows]


@router.get("/{requirement_id}/constraints", response_model=ConstraintProfile)
async def get_requirement_constraints(
    project_id: UUID,
    requirement_id: UUID,
    current: CurrentUser,
    svc: Annotated[RequirementService, Depends(get_requirement_service)],
) -> ConstraintProfile:
    constraint = await svc.get_constraint_for_requirement(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
    )
    if constraint is None:
        raise NotFoundError("No constraint profile for this requirement", code="constraint_not_found")
    return constraint


@router.get("/{requirement_id}", response_model=RequirementDetailResponse)
async def get_requirement(
    project_id: UUID,
    requirement_id: UUID,
    current: CurrentUser,
    svc: Annotated[RequirementService, Depends(get_requirement_service)],
) -> RequirementDetailResponse:
    rev = await svc.get_requirement(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
    )
    constraint = await svc.get_constraint_for_requirement(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
    )
    return RequirementDetailResponse(
        revision=revision_to_response(rev),
        constraint_profile=constraint,
    )
