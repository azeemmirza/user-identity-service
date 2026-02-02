from datetime import datetime

from sqlalchemy.testing.schema import mapped_column
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped


class TimeMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )