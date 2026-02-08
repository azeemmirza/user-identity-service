from fastapi import APIRouter

from src.modules.auth.auth_service import AuthService


router = APIRouter()
service = AuthService()

@router.get('/login', tags=["auth"])
async def login():
    return service.login()


@router.get('/register', tags=["auth"])
async def register():
    return service.register()


@router.get('/logout', tags=["auth"])
async def logout():
    return service.logout()