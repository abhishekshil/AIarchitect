"""Background execution entrypoint for runtime graph builds (Phase 10 skeleton)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def run_runtime_build_job(
    job_id: UUID,
    session_factory: async_sessionmaker[AsyncSession] | None,
) -> None:
    """Runs in FastAPI BackgroundTasks with a fresh DB session (separate from the request)."""
    if session_factory is None:
        return

    from solution_planning_api.api.deps import runtime_build_service_from_session
    from solution_planning_api.infrastructure.persistence.database import session_scope

    async with session_scope(session_factory) as session:
        svc = runtime_build_service_from_session(session)
        await svc.execute_build(job_id)
