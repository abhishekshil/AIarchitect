from __future__ import annotations

from uuid import UUID

from solution_planning_api.application.errors import UnauthorizedError
from solution_planning_api.application.ports.auth import AccessTokenIssuer, PasswordHasher
from solution_planning_api.application.ports.repositories import UserRepository
from solution_planning_api.config import Settings
from solution_planning_api.domain import User


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        password_hasher: PasswordHasher,
        token_issuer: AccessTokenIssuer,
        settings: Settings,
    ) -> None:
        self._users = users
        self._hasher = password_hasher
        self._issuer = token_issuer
        self._settings = settings

    @property
    def access_token_expire_seconds(self) -> int:
        return int(self._settings.access_token_expire_minutes * 60)

    async def register(self, *, email: str, password: str) -> User:
        password_hash = self._hasher.hash(password)
        return await self._users.create(email=email, password_hash=password_hash)

    async def login(self, *, email: str, password: str) -> tuple[str, User]:
        user = await self._users.get_by_email(email)
        if user is None or user.password_hash is None:
            raise UnauthorizedError("Invalid email or password")
        if not self._hasher.verify(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        token = self._issuer.issue(user_id=user.user_id, email=user.email)
        return token, user

    async def get_user(self, user_id: UUID) -> User | None:
        return await self._users.get_by_id(user_id)
