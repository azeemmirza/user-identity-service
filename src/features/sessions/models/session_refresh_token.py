from datetime import datetime
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID


from src.core.database.base import Base
from src.core.database.mixins import TimeMixin, UUIDMixin

class SessionRefreshToken(Base, TimeMixin, UUIDMixin):
    __tablename__ = 'session_refresh_tokens'

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('sessions.id', ondelete='CASCADE'),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<SessionRefreshToken id={getattr(self, 'id', None)!r} "
            f"session_id={self.session_id!r}>"
        )
