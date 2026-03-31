import uuid

from sqlalchemy import func, select

from src.core.database.repository import BaseRepository
from .models.user import User


class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self.scalar(
            select(User).where(func.lower(User.email) == email.strip().lower()),
        )

    async def get_by_username(self, username: str) -> User | None:
        return await self.scalar(select(User).where(User.username == username))

    def create(self, user: User) -> User:
        self.add(user)
        return user
