from fastapi import HTTPException, status

from src.features.auth.schemas import AuthenticatedUser, UserResponse
from src.features.users.repository import UserRepository


class UserService:
    def __init__(self, users: UserRepository):
        self.users = users

    async def get_user(
        self,
        current_user: AuthenticatedUser,
    ) -> UserResponse:
        user = await self.users.get_by_id(current_user.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found",
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
        )


    async def update_user(self):
        # Update a user (not implemented).'''
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )


    async def delete_user(self):
        # Delete a user (not implemented).'''
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="method not implemented",
        )
