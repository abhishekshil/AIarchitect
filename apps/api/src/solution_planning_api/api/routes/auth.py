from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from solution_planning_api.api.deps import CurrentUser, get_auth_service
from solution_planning_api.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from solution_planning_api.application.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    user = await auth.register(email=str(body.email), password=body.password)
    return UserResponse.from_domain(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    token, _ = await auth.login(email=str(body.email), password=body.password)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=auth.access_token_expire_seconds,
    )


@router.get("/me", response_model=UserResponse)
async def me(current: CurrentUser) -> UserResponse:
    return UserResponse.from_domain(current)
