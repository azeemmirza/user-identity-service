from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, DateTime


from src.core.database.base import Base
from src.core.database.mixins import TimeMixin, UUIDMixin

class SessionRefreshToken(Base, TimeMixin, UUIDMixin):
    __tablename__ = 'session_refresh_tokens'

    session_id: Mapped[str] = mapped_column(
        ForeignKey('sessions.id', ondelete='CASCADE'),
        nullable=False,
    )
    token_hash: Mapped[str | None] = mapped_column(
        String,
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<Session id={getattr(self, 'id', None)!r} "
            f"user_id={self.user_id!r} ip={self.ip_address!r}>"
        )

