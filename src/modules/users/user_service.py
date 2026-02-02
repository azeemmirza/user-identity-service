from sqlalchemy.testing.pickleable import User


class UserService:
    async def get_user(self) -> User:
        return NotImplemented()

    async def update_user(self, user: User) -> User:
        return NotImplemented()

    async def delete_user(self, user_id: str) -> User:
        return NotImplemented()