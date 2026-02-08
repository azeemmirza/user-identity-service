from fastapi import APIRouter

from src.modules.users.user_service import UserService


router = APIRouter()
service = UserService()

@router.get('/')
async def get_user():
    return await service.get_user()


@router.put('/')
async def update_user():
    return await service.update_user()


@router.delete('/')
async def delete_user():
    return await service.delete_user()
