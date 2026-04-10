from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe; extend with dependency checks in later phases."""
    return {"status": "healthy", "time": datetime.now(UTC).isoformat()}
