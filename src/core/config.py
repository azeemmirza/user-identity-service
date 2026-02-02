from anyio.functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    APP_NAME: str = 'User Identity Service'
    VERSION: str = '1.0.0'
    ENV: str = 'dev'

    DATABASE_URL: str = None
    DATABASE_USERNAME: str = None
    DATABASE_PASSWORD: str = None
    DATABASE_NAME: str = None

    JWT_SECRET: str = None
    JWT_ALGORITHM: str = 'HS256'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


@lru_cache
def get_config() -> Config:
    return Config()