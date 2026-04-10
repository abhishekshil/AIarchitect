"""
Authentication primitives — swap implementations for enterprise IdP / OIDC.

MVP: `BcryptPasswordHasher` + `JwtAccessTokenIssuer` in infrastructure.
Future: replace `AccessTokenIssuer` with an OIDC token validator that maps
`sub` → internal user id, or add a separate `ExternalIdentityMapper` port.
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID


class PasswordHasher(Protocol):
    """Hash and verify passwords (local accounts)."""

    def hash(self, plain_password: str) -> str: ...
    def verify(self, plain_password: str, password_hash: str) -> bool: ...


class AccessTokenIssuer(Protocol):
    """Issue and verify bearer tokens presented by the API."""

    def issue(self, *, user_id: UUID, email: str) -> str:
        """Return an opaque-to-clients access token (e.g. JWT)."""
        ...

    def verify_and_get_user_id(self, token: str) -> UUID:
        """Validate token and return the authenticated user's id."""
        ...
