from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TaskSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    VIOT_REDIS_SERVER: str = "localhost"
    VIOT_REDIS_PORT: int = 6379

    VIOT_CELERY_BROKER_REDIS_DATABASE: int
    VIOT_CELERY_BACKEND_REDIS_DATABASE: int

    VIOT_CELERY_TASK_MAX_RETRIES: int = 5
    VIOT_CELERY_BACKEND_REDIS_PREFIX: str = "viot_celery"
    VIOT_CELERY_BACKEND_REDIS_TIMEOUT: float = 5.0

    VIOT_CELERY_TASK_PACKAGES: list[str] = [
        "app.modules.celery_task.tasks.mail_task",
    ]

    @computed_field
    @property
    def BROKER_URL(self) -> str:
        return f"redis://{self.VIOT_REDIS_SERVER}:{self.VIOT_REDIS_PORT}/{self.VIOT_CELERY_BROKER_REDIS_DATABASE}"

    @computed_field
    @property
    def RESULT_BACKEND(self) -> str:
        return f"redis://{self.VIOT_REDIS_SERVER}:{self.VIOT_REDIS_PORT}/{self.VIOT_CELERY_BACKEND_REDIS_DATABASE}"


@lru_cache
def _get_settings() -> TaskSettings:
    return TaskSettings()


task_settings = _get_settings()
