from __future__ import annotations

import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from solution_planning_api.api.deps import CurrentUser, get_runtime_build_service
from solution_planning_api.api.schemas.runtime_build import (
    RuntimeBuildJobResponse,
    RuntimeGraphDetailEnvelope,
    RuntimeGraphListEnvelope,
    RuntimeGraphVersionSummaryResponse,
)
from solution_planning_api.application.services.runtime_build_service import RuntimeBuildService
from solution_planning_api.infrastructure.jobs.runtime_build_runner import run_runtime_build_job

router = APIRouter(prefix="/{project_id}", tags=["runtime-build"])


@router.post(
    "/requirements/{requirement_id}/runtime-build",
    response_model=RuntimeBuildJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_runtime_build(
    project_id: UUID,
    requirement_id: UUID,
    request: Request,
    current: CurrentUser,
    svc: Annotated[RuntimeBuildService, Depends(get_runtime_build_service)],
) -> RuntimeBuildJobResponse:
    """Queue a mocked async build that compiles a versioned RuntimeGraph from selection + onboarding."""
    factory = getattr(request.app.state, "session_factory", None)
    if factory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured",
        )
    job = await svc.enqueue_build(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
    )
    # Schedule background execution directly on the event loop; this is
    # more reliable than response-coupled BackgroundTasks for this endpoint.
    asyncio.create_task(run_runtime_build_job(job.job_id, factory))
    return RuntimeBuildJobResponse.from_domain(job)


@router.get("/runtime-builds/{job_id}", response_model=RuntimeBuildJobResponse)
async def get_runtime_build_job(
    project_id: UUID,
    job_id: UUID,
    current: CurrentUser,
    svc: Annotated[RuntimeBuildService, Depends(get_runtime_build_service)],
) -> RuntimeBuildJobResponse:
    job = await svc.get_job(
        owner_user_id=current.user_id,
        project_id=project_id,
        job_id=job_id,
    )
    return RuntimeBuildJobResponse.from_domain(job)


@router.get("/runtime-graphs", response_model=RuntimeGraphListEnvelope)
async def list_runtime_graphs(
    project_id: UUID,
    current: CurrentUser,
    svc: Annotated[RuntimeBuildService, Depends(get_runtime_build_service)],
) -> RuntimeGraphListEnvelope:
    rows = await svc.list_runtime_graph_versions(
        owner_user_id=current.user_id,
        project_id=project_id,
    )
    return RuntimeGraphListEnvelope(
        project_id=project_id,
        versions=[
            RuntimeGraphVersionSummaryResponse(
                version=v,
                runtime_graph_id=gid,
                created_at=ts,
            )
            for v, gid, ts in rows
        ],
    )


@router.get("/runtime-graphs/{version}", response_model=RuntimeGraphDetailEnvelope)
async def get_runtime_graph_by_version(
    project_id: UUID,
    version: int,
    current: CurrentUser,
    svc: Annotated[RuntimeBuildService, Depends(get_runtime_build_service)],
) -> RuntimeGraphDetailEnvelope:
    if version < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="version must be >= 1")
    graph = await svc.get_runtime_graph_version(
        owner_user_id=current.user_id,
        project_id=project_id,
        version=version,
    )
    return RuntimeGraphDetailEnvelope(project_id=project_id, graph=graph)
