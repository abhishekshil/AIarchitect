from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import SolutionCandidateRepository
from solution_planning_api.domain import SolutionCandidate
from solution_planning_api.domain.scoring import ScoringMode
from solution_planning_api.infrastructure.persistence.mappers import (
    solution_candidate_from_record,
    solution_candidate_to_json,
)
from solution_planning_api.infrastructure.persistence.orm_models import SolutionCandidateRecord


def _sort_key(candidate: SolutionCandidate, mode: ScoringMode) -> float:
    breakdown = candidate.score_breakdown or {}
    composite = breakdown.get("composite_by_mode")
    if isinstance(composite, dict) and mode.value in composite:
        return float(composite[mode.value])
    return float(candidate.suitability_score or 0.0)


class SqlAlchemySolutionCandidateRepository(SolutionCandidateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_in_batch(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        generation_batch_id: UUID,
        candidates: list[SolutionCandidate],
    ) -> list[SolutionCandidate]:
        for c in candidates:
            self._session.add(
                SolutionCandidateRecord(
                    id=c.candidate_id,
                    project_id=project_id,
                    requirement_profile_id=requirement_profile_id,
                    generation_batch_id=generation_batch_id,
                    payload=solution_candidate_to_json(c),
                )
            )
        await self._session.flush()
        return candidates

    async def list_latest_batch(
        self,
        requirement_profile_id: UUID,
        *,
        sort_mode: ScoringMode,
    ) -> list[SolutionCandidate]:
        latest_batch_stmt = (
            select(SolutionCandidateRecord.generation_batch_id)
            .where(SolutionCandidateRecord.requirement_profile_id == requirement_profile_id)
            .where(SolutionCandidateRecord.generation_batch_id.is_not(None))
            .order_by(SolutionCandidateRecord.created_at.desc())
            .limit(1)
        )
        batch_id = await self._session.scalar(latest_batch_stmt)
        if batch_id is None:
            return []

        stmt = (
            select(SolutionCandidateRecord)
            .where(SolutionCandidateRecord.requirement_profile_id == requirement_profile_id)
            .where(SolutionCandidateRecord.generation_batch_id == batch_id)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        candidates = [solution_candidate_from_record(r) for r in rows]
        candidates.sort(key=lambda c: _sort_key(c, sort_mode), reverse=True)
        return candidates

    async def get_by_id(self, project_id: UUID, candidate_id: UUID) -> SolutionCandidate | None:
        stmt = select(SolutionCandidateRecord).where(
            SolutionCandidateRecord.id == candidate_id,
            SolutionCandidateRecord.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return solution_candidate_from_record(row) if row else None
