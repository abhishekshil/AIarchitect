"""Application-level errors mapped to HTTP responses in the API layer."""


class ServiceError(Exception):
    """Base error for use-case failures (no FastAPI imports here)."""

    def __init__(self, message: str, *, code: str = "error", status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class UnauthorizedError(ServiceError):
    def __init__(self, message: str = "Invalid credentials", *, code: str = "unauthorized") -> None:
        super().__init__(message, code=code, status_code=401)


class ForbiddenError(ServiceError):
    def __init__(self, message: str = "Forbidden", *, code: str = "forbidden") -> None:
        super().__init__(message, code=code, status_code=403)


class NotFoundError(ServiceError):
    def __init__(self, message: str = "Not found", *, code: str = "not_found") -> None:
        super().__init__(message, code=code, status_code=404)


class ConflictError(ServiceError):
    def __init__(self, message: str = "Conflict", *, code: str = "conflict") -> None:
        super().__init__(message, code=code, status_code=409)
