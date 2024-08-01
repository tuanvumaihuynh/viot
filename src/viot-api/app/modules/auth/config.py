from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    VIOT_JWT_SECRET: str
    VIOT_JWT_ALG: str = "HS256"
    VIOT_JWT_ACCESS_TOKEN_EXP: int = 60 * 5  # 5 minutes

    VIOT_JWT_REFRESH_TOKEN_EXP: int = 60 * 60 * 24 * 21  # 21 days
    VIOT_JWT_REFRESH_TOKEN_SAMESITE: Literal["Strict", "Lax", "None"] = "Lax"
    VIOT_JWT_REFRESH_TOKEN_DOMAIN: str
    VIOT_JWT_REFRESH_TOKEN_SECURE: bool = False


@lru_cache
def _get_settings() -> AuthSettings:
    return AuthSettings()


auth_settings = _get_settings()
