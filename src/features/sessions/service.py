import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status

from src.features.auth.schemas import AuthenticatedUser, MessageResponse, SessionResponse
from src.features.sessions.models.session import Session
from src.features.sessions.repository import SessionRefreshTokenRepository, SessionRepository

class SessionService:
    def __init__(
        self,
        sessions: SessionRepository,
        refresh_tokens: SessionRefreshTokenRepository,
    ):
        self.sessions = sessions
        self.refresh_tokens = refresh_tokens

    async def get_sessions(
        self,
        current_user: AuthenticatedUser,
    ) -> list[SessionResponse]:
        sessions = await self.sessions.list_by_user_id(current_user.user_id)
        return [self._serialize_session(session) for session in sessions]

    async def get_session(
        self,
        current_user: AuthenticatedUser,
        session_id: str,
    ) -> SessionResponse:
        session = await self._get_owned_session(current_user, session_id)
        return self._serialize_session(session)

    async def revoke_session(
        self,
        current_user: AuthenticatedUser,
        session_id: str,
    ) -> MessageResponse:
        session = await self._get_owned_session(current_user, session_id)
        session.revoked_at = session.revoked_at or datetime.now(UTC).replace(tzinfo=None)

        refresh_tokens = await self.refresh_tokens.list_by_session_id(session.id)
        for refresh_token in refresh_tokens:
            await self.refresh_tokens.delete(refresh_token)

        await self.sessions.commit()
        return MessageResponse(message="session revoked")

    async def _get_owned_session(
        self,
        current_user: AuthenticatedUser,
        session_id: str,
    ) -> Session:
        try:
            parsed_session_id = uuid.UUID(session_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid session id",
            ) from exc

        session = await self.sessions.get_by_id(parsed_session_id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="session not found",
            )

        if session.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="cannot access another user's session",
            )
        return session

    def _serialize_session(self, session: Session) -> SessionResponse:
        return SessionResponse(
            id=session.id,
            user_agent=session.user_agent,
            ip_address=str(session.ip_address) if session.ip_address else None,
            device_name=session.device_name,
            last_seen_at=session.last_seen_at,
            remember_me=bool(session.remember_me),
            revoked_at=session.revoked_at,
            created_at=session.created_at,
        )
