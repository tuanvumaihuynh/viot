from app.modules.email.enums import MessageType
from app.modules.email.service import get_template, render, send

from ..celery import celery_app
from ..config import task_settings


@celery_app.task(
    name="send_verify_account_email",
    bind=True,
    retry_backoff=True,
    max_retries=task_settings.VIOT_CELERY_TASK_MAX_RETRIES,
)
def send_verify_account_email(self, *, email: str, name: str, callback_url: str) -> None:
    template = get_template(MessageType.VERIFY_ACCOUNT)
    html_content = render(template=template, ctx={"name": name, "link": callback_url})
    send(to=email, subject="Verify your account", html_content=html_content)


@celery_app.task(
    name="send_reset_password_email",
    bind=True,
    retry_backoff=True,
    max_retries=task_settings.VIOT_CELERY_TASK_MAX_RETRIES,
)
def send_reset_password_email(self, *, email: str, name: str, ui_url: str) -> None:
    template = get_template(MessageType.RESET_PASSWORD)
    html_content = render(template=template, ctx={"name": name, "link": ui_url})
    send(to=email, subject="Reset your password", html_content=html_content)
