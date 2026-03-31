from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response

from .service import AuthService
from src.features.auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_optional_current_user,
)
from src.features.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    AuthenticatedUser
)

router = APIRouter()
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
OptionalCurrentUser = Annotated[AuthenticatedUser | None, Depends(get_optional_current_user)]

@router.post('/login', tags=["auth"])
async def login(
    body: LoginRequest,
    request: Request,
    service: AuthServiceDep,
):
    return await service.login(body, request)


@router.post('/register', tags=["auth"])
async def register(
    body: RegisterRequest,
    request: Request,
    service: AuthServiceDep,
):
    return await service.register(body, request)


@router.post('/token', tags=["auth"])
async def refresh_token(
    body: RefreshTokenRequest,
    request: Request,
    service: AuthServiceDep,
):
    return await service.refresh_token(body.refresh_token, request)


@router.post('/logout', tags=["auth"])
async def logout(
    body: LogoutRequest,
    service: AuthServiceDep,
    current_user: OptionalCurrentUser,
):
    return await service.logout(body.refresh_token, current_user)


@router.post('/password/forgot', tags=["auth"])
async def forgot_password(
    body: ForgotPasswordRequest,
    service: AuthServiceDep,
    response: Response,
):
    message, reset_token = await service.forgot_password(body)
    if reset_token is not None:
        response.headers["X-Debug-Reset-Token"] = reset_token
    return message


@router.post('/password/reset', tags=["auth"])
async def reset_password(
    body: ResetPasswordRequest,
    service: AuthServiceDep,
):
    return await service.reset_password(body)
