from sqlalchemy.testing.schema import mapped_column
from sqlalchemy import Integer, String

from src.core.database.time_mixin import TimeMixin
from src.core.database.base import Base


class UserProfile(Base, TimeMixin):
    id: Mapped[Integer] = mapped_column(Integer)