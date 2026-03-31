from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base import Base
from src.core.database.mixins import UUIDMixin, TimeMixin


class UserProfile(Base, TimeMixin, UUIDMixin):
    __tablename__ = 'user_profiles'

    user_id: Mapped[int] = mapped_column(Integer, index=True)
    bio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)


    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<UserProfile id={self.id!r} user_id={self.user_id!r}>"
