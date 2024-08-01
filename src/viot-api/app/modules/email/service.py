import logging
from pathlib import Path

import yagmail
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from .config import email_settings
from .enums import MessageType
from .exceptions import TemplateNotFoundException

logger = logging.getLogger(__name__)


_yagmail = yagmail.SMTP(email_settings.VIOT_EMAIL_USER, email_settings.VIOT_EMAIL_PASSWORD)
_template_dir = Path(__file__).parent / "templates"
_env = Environment(loader=FileSystemLoader(_template_dir), autoescape=select_autoescape(["html"]))


template_map: dict[MessageType, str] = {
    MessageType.VERIFY_ACCOUNT: "verify-account.html",
    MessageType.RESET_PASSWORD: "reset-password.html",
}


def get_template(message_type: MessageType) -> Template:
    template_key = template_map.get(message_type, None)
    if not template_key:
        raise TemplateNotFoundException(f"Template not found for message type: {message_type}")
    template = _env.get_template(template_key)
    return template


def render(*, template: Template, ctx: dict[str, any]) -> str:
    return template.render(**ctx)


# TODO: Need to handle errors
def send(*, to: str, subject: str, html_content: str) -> None:
    _yagmail.send(to=to, subject=subject, contents=[html_content])
    logger.info(f"Email sent to {to}")
