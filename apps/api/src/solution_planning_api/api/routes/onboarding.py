from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from solution_planning_api.api.deps import CurrentUser, get_onboarding_service
from solution_planning_api.api.schemas.onboarding import (
    OnboardingProgressResponse,
    OnboardingTaskGraphEdgeResponse,
    OnboardingTaskItemResponse,
    OnboardingTasksEnvelope,
    SubmitOnboardingTaskRequest,
)
from solution_planning_api.application.services.onboarding_service import OnboardingService

router = APIRouter(
    prefix="/{project_id}/requirements/{requirement_id}/onboarding",
    tags=["onboarding"],
)


@router.get("/tasks", response_model=OnboardingTasksEnvelope)
async def list_onboarding_tasks(
    project_id: UUID,
    requirement_id: UUID,
    current: CurrentUser,
    svc: Annotated[OnboardingService, Depends(get_onboarding_service)],
) -> OnboardingTasksEnvelope:
    tg, items = await svc.list_tasks(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
    )
    return OnboardingTasksEnvelope(
        task_graph_id=tg.task_graph_id,
        tasks=[OnboardingTaskItemResponse.model_validate(x) for x in items],
        edges=[
            OnboardingTaskGraphEdgeResponse(
                source_id=e.source_id, target_id=e.target_id, relation=e.relation
            )
            for e in tg.edges
        ],
    )


@router.get("/tasks/{node_id}", response_model=OnboardingTaskItemResponse)
async def get_onboarding_task(
    project_id: UUID,
    requirement_id: UUID,
    node_id: str,
    current: CurrentUser,
    svc: Annotated[OnboardingService, Depends(get_onboarding_service)],
) -> OnboardingTaskItemResponse:
    item = await svc.get_task(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
        node_id=node_id,
    )
    return OnboardingTaskItemResponse.model_validate(item)


@router.post(
    "/tasks/{node_id}/start",
    response_model=OnboardingTaskItemResponse,
    status_code=status.HTTP_200_OK,
)
async def start_onboarding_task(
    project_id: UUID,
    requirement_id: UUID,
    node_id: str,
    current: CurrentUser,
    svc: Annotated[OnboardingService, Depends(get_onboarding_service)],
) -> OnboardingTaskItemResponse:
    item = await svc.start_task(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
        node_id=node_id,
    )
    return OnboardingTaskItemResponse.model_validate(item)


@router.post(
    "/tasks/{node_id}/submit",
    response_model=OnboardingTaskItemResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_onboarding_task(
    project_id: UUID,
    requirement_id: UUID,
    node_id: str,
    body: SubmitOnboardingTaskRequest,
    current: CurrentUser,
    svc: Annotated[OnboardingService, Depends(get_onboarding_service)],
) -> OnboardingTaskItemResponse:
    item = await svc.submit_task(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
        node_id=node_id,
        response=body.response,
    )
    return OnboardingTaskItemResponse.model_validate(item)


@router.get("/progress", response_model=OnboardingProgressResponse)
async def get_onboarding_progress(
    project_id: UUID,
    requirement_id: UUID,
    current: CurrentUser,
    svc: Annotated[OnboardingService, Depends(get_onboarding_service)],
) -> OnboardingProgressResponse:
    snap = await svc.progress_snapshot(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
    )
    return OnboardingProgressResponse.model_validate(snap)
