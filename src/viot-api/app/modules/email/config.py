from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    VIOT_DOMAIN_URL: str
    VIOT_API_PREFIX: str = "/api/v1"

    VIOT_EMAIL_USER: str
    VIOT_EMAIL_PASSWORD: str


@lru_cache
def _get_settings() -> EmailSettings:
    return EmailSettings()


email_settings = _get_settings()
