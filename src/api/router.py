from fastapi import APIRouter
from src.modules.health.routes import router as health_router
from src.modules.users.routes import router as user_router

api_router = APIRouter()

api_router.include_router(health_router, tags=['health'])
api_router.include_router(user_router, prefix='/user', tags=['user'])
api_router.include_router(user_router, prefix='/auth', tags=['auth'])
api_router.include_router(user_router, prefix='/session', tags=['session'])