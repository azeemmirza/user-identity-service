from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_async_session
from src.features.auth.dependencies import get_current_user
from src.features.auth.schemas import AuthenticatedUser
from src.features.users.repository import UserRepository
from .service import UserService


router = APIRouter()
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def get_user_service(
    db: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserService:
    return UserService(users=UserRepository(db))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]

@router.get('/me')
async def get_user(
    service: UserServiceDep,
    current_user: CurrentUser,
):
    return await service.get_user(current_user)


@router.put('/')
async def update_user(service: UserServiceDep):
    return await service.update_user()


@router.delete('/')
async def delete_user(service: UserServiceDep):
    return await service.delete_user()
