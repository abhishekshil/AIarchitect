"""SQLAlchemy declarative base for persistence models (ORM only)."""

from sqlalchemy.orm import DeclarativeBase


class MappedBase(DeclarativeBase):
    """ORM base — keep separate from Pydantic domain models."""
