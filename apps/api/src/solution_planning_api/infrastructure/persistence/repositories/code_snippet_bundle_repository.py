from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import CodeSnippetBundleRepository
from solution_planning_api.domain import CodeSnippetBundleSummary
from solution_planning_api.infrastructure.persistence.mappers import code_snippet_bundle_summary_from_record
from solution_planning_api.infrastructure.persistence.orm_models import CodeSnippetBundleRecord


class SqlAlchemyCodeSnippetBundleRepository(CodeSnippetBundleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_bundle(
        self,
        *,
        bundle_id: UUID,
        project_id: UUID,
        runtime_graph_id: UUID | None,
        runtime_graph_version: int,
        architecture_pattern: str,
        payload: dict[str, Any],
    ) -> CodeSnippetBundleSummary:
        row = CodeSnippetBundleRecord(
            id=bundle_id,
            project_id=project_id,
            runtime_graph_id=runtime_graph_id,
            runtime_graph_version=runtime_graph_version,
            architecture_pattern=architecture_pattern,
            payload=payload,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return code_snippet_bundle_summary_from_record(row)

    async def list_bundles(self, project_id: UUID, *, limit: int = 20) -> list[CodeSnippetBundleSummary]:
        stmt = (
            select(CodeSnippetBundleRecord)
            .where(CodeSnippetBundleRecord.project_id == project_id)
            .order_by(desc(CodeSnippetBundleRecord.created_at))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [code_snippet_bundle_summary_from_record(r) for r in rows]

    async def get_payload(self, project_id: UUID, bundle_id: UUID) -> dict[str, Any] | None:
        stmt = select(CodeSnippetBundleRecord).where(
            CodeSnippetBundleRecord.id == bundle_id,
            CodeSnippetBundleRecord.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return dict(row.payload) if row else None
