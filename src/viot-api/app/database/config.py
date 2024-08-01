from functools import lru_cache

from pydantic import computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.enums import EnvConfig


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    VIOT_API_ENV: EnvConfig = EnvConfig.DEV

    VIOT_POSTGRES_SERVER: str = "localhost"
    VIOT_POSTGRES_PORT: int = 5432
    VIOT_POSTGRES_USER: str = "postgres"
    VIOT_POSTGRES_PASSWORD: str = "postgres"
    VIOT_POSTGRES_DB: str = "postgres"

    VIOT_REDIS_SERVER: str = "localhost"
    VIOT_REDIS_PORT: int = 6379

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.VIOT_POSTGRES_USER,
            password=self.VIOT_POSTGRES_PASSWORD,
            host=self.VIOT_POSTGRES_SERVER,
            port=self.VIOT_POSTGRES_PORT,
            path=self.VIOT_POSTGRES_DB,
        ).unicode_string()

    @computed_field
    @property
    def IS_DEV_ENV(self) -> bool:
        return self.VIOT_API_ENV == EnvConfig.DEV


@lru_cache
def _get_settings() -> DatabaseSettings:
    return DatabaseSettings()


db_settings = _get_settings()
