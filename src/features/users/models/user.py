from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.base import Base
from src.core.database.mixins import TimeMixin, UUIDMixin


class User(Base, TimeMixin, UUIDMixin):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<User id={self.id!r} username={self.username!r} email={self.email!r}>"
