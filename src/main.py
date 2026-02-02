from fastapi import FastAPI
from src.core.config import get_config
from src.api.router import api_router

config = get_config()

def create_app() -> FastAPI:

    app = FastAPI(
        title=config.APP_NAME,
        version=config.VERSION,
    )

    app.include_router(api_router)

    return app


app = create_app()