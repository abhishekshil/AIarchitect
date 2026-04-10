"""Sentinel for partial updates (exclude field vs set null vs set value)."""


class UnsetType:
    __slots__ = ()


UNSET: UnsetType = UnsetType()
