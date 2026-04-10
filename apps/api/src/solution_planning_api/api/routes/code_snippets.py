from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from solution_planning_api.api.deps import CurrentUser, get_code_snippet_service
from solution_planning_api.api.schemas.code_snippets import (
    CodeSnippetBundleListEnvelope,
    CodeSnippetBundleResponse,
    CodeSnippetBundleSummaryResponse,
    GenerateCodeSnippetsRequest,
)
from solution_planning_api.application.services.code_snippet_service import CodeSnippetService

router = APIRouter(prefix="/{project_id}/code-snippets", tags=["code-snippets"])


@router.post("/generate", response_model=CodeSnippetBundleResponse, status_code=status.HTTP_201_CREATED)
async def generate_code_snippets(
    project_id: UUID,
    body: GenerateCodeSnippetsRequest,
    current: CurrentUser,
    svc: Annotated[CodeSnippetService, Depends(get_code_snippet_service)],
) -> CodeSnippetBundleResponse:
    """Create architecture-aware cURL / JavaScript / Python snippets and persist the bundle."""
    payload = await svc.generate_and_persist(
        owner_user_id=current.user_id,
        project_id=project_id,
        runtime_graph_version=body.runtime_graph_version,
    )
    return CodeSnippetBundleResponse.model_validate(payload)


@router.get("/", response_model=CodeSnippetBundleListEnvelope)
async def list_code_snippet_bundles(
    project_id: UUID,
    current: CurrentUser,
    svc: Annotated[CodeSnippetService, Depends(get_code_snippet_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> CodeSnippetBundleListEnvelope:
    rows = await svc.list_bundles(
        owner_user_id=current.user_id,
        project_id=project_id,
        limit=limit,
    )
    return CodeSnippetBundleListEnvelope(
        project_id=project_id,
        bundles=[CodeSnippetBundleSummaryResponse.from_domain(r) for r in rows],
    )


@router.get("/{bundle_id}", response_model=CodeSnippetBundleResponse)
async def get_code_snippet_bundle(
    project_id: UUID,
    bundle_id: UUID,
    current: CurrentUser,
    svc: Annotated[CodeSnippetService, Depends(get_code_snippet_service)],
) -> CodeSnippetBundleResponse:
    payload = await svc.get_bundle_payload(
        owner_user_id=current.user_id,
        project_id=project_id,
        bundle_id=bundle_id,
    )
    return CodeSnippetBundleResponse.model_validate(payload)
