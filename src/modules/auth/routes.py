from fastapi import APIRouter

from src.modules.auth.auth_service import AuthService
from src.modules.auth.request_models import LoginRequest, RegisterRequest

router = APIRouter()
service = AuthService()

@router.post('/login', tags=["auth"])
async def login(body: LoginRequest):
    return service.login(body)


@router.post('/register', tags=["auth"])
async def register(body: RegisterRequest):
    return service.register(body)


@router.get('/logout', tags=["auth"])
async def logout():
    return service.logout()