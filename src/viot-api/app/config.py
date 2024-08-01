from functools import lru_cache
from typing import Any

from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import EnvConfig


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    VIOT_API_ENV: EnvConfig = EnvConfig.DEV

    VIOT_API_PORT: int = 8000
    VIOT_API_PREFIX: str = "/api/v1"

    VIOT_API_ALLOW_CREDENTIALS: bool = True
    VIOT_API_CORS_ORIGINS: list[AnyHttpUrl | str] = [
        "http://localhost",
        "http://localhost:5173",
    ]
    VIOT_API_ALLOW_METHODS: list[str] = ["*"]
    VIOT_API_CORS_HEADERS: list[str] = ["*"]

    VIOT_UI_URL: str = "http://localhost:5173"

    @computed_field
    @property
    def FASTAPI_CONFIG(self) -> dict[str, Any]:
        return {
            "title": "Viot API",
            "description": "Viot API documentation",
            "version": "0.1.0",
            "redoc_url": None,
            "docs_url": "/docs",
            "openapi_url": "/docs/openapi.json",
        }

    @computed_field
    @property
    def IS_DEV_ENV(self) -> bool:
        return self.VIOT_API_ENV == EnvConfig.DEV


@lru_cache
def _get_settings() -> AppSettings:
    return AppSettings()


app_settings = _get_settings()
