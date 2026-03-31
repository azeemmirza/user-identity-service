from fastapi import APIRouter
from src.core.config import get_config
from src.features.health.schemas import HealthResponse
from src.features.health.service import HealthService

router = APIRouter()
config = get_config()
service = HealthService()


# health check endpoint
@router.get(
    '/health',
    response_model=HealthResponse,
    tags=["health"],
)
async def health_check() -> HealthResponse:
    return service.check_health()