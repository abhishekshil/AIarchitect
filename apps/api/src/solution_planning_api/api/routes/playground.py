from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from solution_planning_api.api.deps import CurrentUser, get_inference_playground_service, get_project_service
from solution_planning_api.api.schemas.inference_playground import (
    PlaygroundInferRequest,
    PlaygroundInferResponse,
    PlaygroundInferenceHistoryEnvelope,
    PlaygroundInferenceRunSummaryResponse,
)
from solution_planning_api.application.services.inference_playground_service import InferencePlaygroundService
from solution_planning_api.application.services.project_service import ProjectService

router = APIRouter(prefix="/{project_id}/playground", tags=["playground"])


@router.get("/test", status_code=status.HTTP_200_OK)
async def playground_test(
    project_id: UUID,
    current: CurrentUser,
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> dict[str, str | bool]:
    """Lightweight probe that playground routes are reachable for this project."""
    await projects.get_project(owner_user_id=current.user_id, project_id=project_id)
    return {"playground": "ok", "mock_inference": True}


@router.post("/infer", response_model=PlaygroundInferResponse, status_code=status.HTTP_201_CREATED)
async def run_playground_inference(
    project_id: UUID,
    body: PlaygroundInferRequest,
    current: CurrentUser,
    svc: Annotated[InferencePlaygroundService, Depends(get_inference_playground_service)],
) -> PlaygroundInferResponse:
    """Run mocked architecture-aware inference against a versioned runtime graph; persist history."""
    payload = await svc.run_infer(
        owner_user_id=current.user_id,
        project_id=project_id,
        runtime_graph_version=body.runtime_graph_version,
        input_text=body.input_text,
    )
    return PlaygroundInferResponse.model_validate(payload)


@router.get("/inference-runs", response_model=PlaygroundInferenceHistoryEnvelope)
async def list_playground_inference_runs(
    project_id: UUID,
    current: CurrentUser,
    svc: Annotated[InferencePlaygroundService, Depends(get_inference_playground_service)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> PlaygroundInferenceHistoryEnvelope:
    rows = await svc.list_history(
        owner_user_id=current.user_id,
        project_id=project_id,
        limit=limit,
    )
    return PlaygroundInferenceHistoryEnvelope(
        project_id=project_id,
        runs=[PlaygroundInferenceRunSummaryResponse.from_domain(r) for r in rows],
    )


@router.get("/inference-runs/{inference_id}", response_model=PlaygroundInferResponse)
async def get_playground_inference_run(
    project_id: UUID,
    inference_id: UUID,
    current: CurrentUser,
    svc: Annotated[InferencePlaygroundService, Depends(get_inference_playground_service)],
) -> PlaygroundInferResponse:
    payload = await svc.get_inference_detail(
        owner_user_id=current.user_id,
        project_id=project_id,
        inference_id=inference_id,
    )
    return PlaygroundInferResponse.model_validate(payload)
