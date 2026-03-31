import uuid

from sqlalchemy import select

from src.core.database.repository import BaseRepository
from src.features.sessions.models.session import Session
from src.features.sessions.models.session_refresh_token import SessionRefreshToken


class SessionRepository(BaseRepository):
    async def get_by_id(self, session_id: uuid.UUID) -> Session | None:
        return await self.get(Session, session_id)

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[Session]:
        return list(
            await self.scalars(
                select(Session)
                .where(Session.user_id == user_id)
                .order_by(Session.created_at.desc()),
            ),
        )

    async def list_active_by_user_id(self, user_id: uuid.UUID) -> list[Session]:
        return list(
            await self.scalars(
                select(Session).where(
                    Session.user_id == user_id,
                    Session.revoked_at.is_(None),
                ),
            ),
        )

    def create(self, session: Session) -> Session:
        self.add(session)
        return session


class SessionRefreshTokenRepository(BaseRepository):
    async def get_by_session_id(self, session_id: uuid.UUID) -> SessionRefreshToken | None:
        return await self.scalar(
            select(SessionRefreshToken).where(SessionRefreshToken.session_id == session_id),
        )

    async def list_by_session_id(self, session_id: uuid.UUID) -> list[SessionRefreshToken]:
        return list(
            await self.scalars(
                select(SessionRefreshToken).where(SessionRefreshToken.session_id == session_id),
            ),
        )

    def create(self, refresh_token: SessionRefreshToken) -> SessionRefreshToken:
        self.add(refresh_token)
        return refresh_token
