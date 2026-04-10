"""JWT access tokens — replace with OIDC validation + internal subject mapping when needed."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from solution_planning_api.application.errors import UnauthorizedError
from solution_planning_api.config import Settings


class JwtAccessTokenIssuer:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._expire = timedelta(minutes=settings.access_token_expire_minutes)

    def issue(self, *, user_id: UUID, email: str) -> str:
        now = datetime.now(UTC)
        iat = int(now.timestamp())
        exp = int((now + self._expire).timestamp())
        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": iat,
            "exp": exp,
            "typ": "access",
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify_and_get_user_id(self, token: str) -> UUID:
        try:
            decoded = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"require": ["exp", "sub", "typ"]},
            )
        except jwt.PyJWTError as e:
            raise UnauthorizedError("Invalid or expired token") from e

        if decoded.get("typ") != "access":
            raise UnauthorizedError("Invalid token type")

        try:
            return UUID(decoded["sub"])
        except (ValueError, TypeError) as e:
            raise UnauthorizedError("Invalid subject in token") from e
