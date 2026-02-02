from fastapi import APIRouter
from src.core.config import get_config


router = APIRouter()
config = get_config()


# health check endpoint
@router.get("/health")
async def health_check() -> dict:
    return {
        'status': 'ok',
        'service': config.APP_NAME,
        'version': config.VERSION,
        'env': config.ENV,
    }