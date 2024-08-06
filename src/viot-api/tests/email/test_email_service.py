import pytest

from app.modules.email.enums import MessageType
from app.modules.email.exceptions import TemplateNotFoundException


def test_get_template():
    from app.modules.email.service import get_template

    # Test get template
    template = get_template(MessageType.VERIFY_ACCOUNT)
    assert template is not None

    # Test get template with invalid message type
    with pytest.raises(TemplateNotFoundException):
        get_template("invalid")


def test_render():
    from app.modules.email.service import get_template, render

    # Test render
    template = get_template(MessageType.VERIFY_ACCOUNT)
    html_content = render(template=template, ctx={"name": "John"})
    assert "John" in html_content
