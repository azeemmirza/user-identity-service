import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.repository import BaseRepository
from src.core.database.session import get_async_session
from src.core.security.jwt import decode_token
from src.features.auth.service import AuthService
from src.features.auth.repository import PasswordResetTokenRepository
from src.features.auth.schemas import AuthenticatedUser
from src.features.sessions.repository import SessionRepository, SessionRefreshTokenRepository
from src.features.users.repository import UserRepository
from src.shared.errors import TokenError


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthenticatedUser:
    '''
    Get the currently authenticated user.

    :param credentials: The HTTP authorization credentials extracted from the request header.
    :param db: The asynchronous database session for querying user and session information.

    :return: An AuthenticatedUser object representing the currently authenticated user.
    '''
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )
    return await _authenticate_credentials(credentials, db)


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthenticatedUser | None:
    if credentials is None:
        return None
    return await _authenticate_credentials(credentials, db)


async def _authenticate_credentials(
    credentials: HTTPAuthorizationCredentials,
    db: AsyncSession,
) -> AuthenticatedUser:
    users = UserRepository(db)
    sessions = SessionRepository(db)

    try:
        payload = decode_token(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid access token",
        ) from exc

    if payload.get("type") != "access" or payload.get("identity_type") != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid access token",
        )

    try:
        user_id = uuid.UUID(payload["sub"])
        session_id = uuid.UUID(payload["session_id"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid access token",
        ) from exc

    user = await users.get_by_id(user_id)
    session = await sessions.get_by_id(session_id)
    if user is None or session is None or not user.is_active or session.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="session is no longer active",
        )

    return AuthenticatedUser(
        user_id=user_id,
        session_id=session_id,
        identity_type="user",
    )


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthService:
    repository = BaseRepository(db)
    return AuthService(
        repository=repository,
        users=UserRepository(db),
        sessions=SessionRepository(db),
        refresh_tokens=SessionRefreshTokenRepository(db),
        password_reset_tokens=PasswordResetTokenRepository(db),
    )
