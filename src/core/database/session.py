from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import get_config

config = get_config()

if not (
        config.DATABASE_URL
        or config.DATABASE_NAME
        or config.DATABASE_PASSWORD
        or config.DATABASE_USERNAME):
    raise RuntimeError('MUST provide DATABASE_URL or DATABASE_NAME or DATABASE_PASSWORD or DATABASE_USERNAME')

# STRING FORMAT: postgresql+asyncpg://user:pass@localhost:5432/db
database_connection_str = f'postgresql+asyncpg://{config.DATABASE_USERNAME}:{config.DATABASE_PASSWORD}@{config.DATABASE_URL}/{config.DATABASE_NAME}'

database_engine = create_async_engine(
    database_connection_str,
    pool_pre_ping=True,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=database_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncSession:
    return AsyncSessionLocal()