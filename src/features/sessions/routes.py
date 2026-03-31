from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_async_session
from src.features.auth.dependencies import get_current_user
from src.features.auth.schemas import AuthenticatedUser
from src.features.sessions.repository import SessionRefreshTokenRepository, SessionRepository
from src.features.sessions.service import SessionService


router = APIRouter()
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def get_session_service(
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> SessionService:
    return SessionService(
        sessions=SessionRepository(db),
        refresh_tokens=SessionRefreshTokenRepository(db),
    )


SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]

@router.get('/')
async def get_sessions(
    service: SessionServiceDep,
    current_user: CurrentUser,
):
    return await service.get_sessions(current_user)


@router.get('/{session_id}')
async def get_session(
    session_id: str,
    service: SessionServiceDep,
    current_user: CurrentUser,
):
    return await service.get_session(current_user, session_id)


@router.delete('/{session_id}')
async def revoke_session(
    session_id: str,
    service: SessionServiceDep,
    current_user: CurrentUser,
):
    return await service.revoke_session(current_user, session_id)
