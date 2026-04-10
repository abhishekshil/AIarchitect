from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.errors import ConflictError
from solution_planning_api.application.ports.repositories import UserRepository
from solution_planning_api.domain import User
from solution_planning_api.infrastructure.persistence.mappers import user_from_record
from solution_planning_api.infrastructure.persistence.orm_models import UserRecord


def _normalize_email(email: str) -> str:
    return email.strip().lower()


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, email: str, password_hash: str) -> User:
        row = UserRecord(email=_normalize_email(email), password_hash=password_hash)
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            raise ConflictError("Email already registered", code="email_taken") from e

        await self._session.refresh(row)
        return user_from_record(row)

    async def get_by_id(self, user_id: UUID) -> User | None:
        row = await self._session.get(UserRecord, user_id)
        return user_from_record(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserRecord).where(UserRecord.email == _normalize_email(email))
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return user_from_record(row) if row else None
