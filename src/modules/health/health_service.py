from src.core.config import get_config
from src.modules.health.dtos import HealthResponse

config = get_config()

class HealthService:
    def check_health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="health",
            version=config.VERSION,
            env=config.ENV,
        )

