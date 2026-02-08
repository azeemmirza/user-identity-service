from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.router import api_router
from src.core.config import get_config
from src.core.logger import logger


config = get_config()

async def initialize_app():
    pass

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    title = app_instance.title
    version = app_instance.version

    # STARTUP
    logger.info("starting %s[%s]", title, version)

    # If you want: init db/redis clients here
    await initialize_app()
    yield

    # SHUTDOWN
    logger.info("shutting down %s[%s]", title, version)

    # If you want: close db/redis clients here


def bootstrap() -> FastAPI:
    application = FastAPI(
        title=config.APP_NAME,
        version=config.VERSION,
        lifespan=lifespan,
    )

    application.include_router(api_router)

    logger.info("started %s[%s]", application.title, application.version)

    return application


app = bootstrap()

