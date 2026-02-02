from sqlalchemy import Column, String, Integer, Boolean, DateTime, func
from sqlalchemy.testing.schema import mapped_column

from src.core.database.base import Base
from src.core.database.time_mixin import TimeMixin


class User(Base, TimeMixin):
    __tablename__ = 'users'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[String] = mapped_column(String(255), nullable=False, unique=True)
    first_name: Mapped[String] = mapped_column(String(120), nullable=True)
    last_name: Mapped[String] = mapped_column(String(120), nullable=True)
    username: Mapped[String] = mapped_column(String(80), nullable=False, unique=True, index=True)
    password: Mapped[String] = mapped_column(String(255), nullable=False)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<User id={self.id!r} username={self.username!r} email={self.email!r}>"
