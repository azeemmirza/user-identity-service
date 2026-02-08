from datetime import datetime

from sqlalchemy import ForeignKey, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base import Base
from src.core.database.mixins import TimeMixin, UUIDMixin


class Session(Base, TimeMixin, UUIDMixin):
    __tablename__ = 'sessions'

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    device_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(nullable=True)
    remember_me: Mapped[bool] = mapped_column(Boolean, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<Session id={getattr(self, 'id', None)!r} "
            f"user_id={self.user_id!r} ip={self.ip_address!r}>"
        )