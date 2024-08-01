from celery import Celery
from celery.app.trace import reset_worker_optimizations

from .config import task_settings


def init_celery() -> Celery:
    reset_worker_optimizations()

    app = Celery(
        "viot_celery",
        broker=task_settings.BROKER_URL,
        backend=task_settings.RESULT_BACKEND,
        broker_connection_retry_on_startup=True,
        include=task_settings.VIOT_CELERY_TASK_PACKAGES,
    )

    return app


celery_app = init_celery()
