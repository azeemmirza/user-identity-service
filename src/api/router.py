from fastapi import APIRouter
from src.features.health.routes import router as health_router
from src.features.users.routes import router as user_router
from src.features.sessions.routes import router as session_router
from src.features.auth.routes import router as auth_router


api_router = APIRouter()

api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
api_router.include_router(user_router, prefix='/users', tags=['user'])
api_router.include_router(session_router, prefix='/sessions', tags=['session'])
api_router.include_router(health_router, tags=['health'])
