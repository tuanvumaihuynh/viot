from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

import jwt
import pytest

from app.exceptions import UnauthorizedException
from app.modules.auth.config import auth_settings
from app.modules.auth.constants import AuthErrorCode
from app.modules.auth.jwt import (
    create_refresh_token,
    get_refresh_token_settings,
    parse_jwt_token,
)
from app.modules.auth.schemas import JwtPayload


def test_create_refresh_token():
    user_id = uuid4()
    user_email = "test@example.com"
    expire_time = timedelta(minutes=10)

    with patch("app.modules.auth.jwt.create_access_token") as mock_create_access_token:
        mock_create_access_token.return_value = "encoded_refresh_token"

        token = create_refresh_token(
            user_id=user_id, user_email=user_email, expire_time=expire_time
        )

        assert token == "encoded_refresh_token"
        mock_create_access_token.assert_called_once_with(
            user_id=user_id, user_email=user_email, expire_time=expire_time
        )


@patch("app.modules.auth.jwt.jwt.decode")
def test_parse_jwt_token(mock_decode):
    token = "valid_token"
    payload = {
        "jti": "some_uuid",
        "exp": 1234567890,
        "sub": str(uuid4()),
        "email": "test@example.com",
    }

    mock_decode.return_value = payload

    result = parse_jwt_token(token)

    assert isinstance(result, JwtPayload)
    assert result.model_dump() == payload


@patch("app.modules.auth.jwt.jwt.decode")
def test_parse_jwt_token_expired(mock_decode):
    mock_decode.side_effect = jwt.ExpiredSignatureError()

    with pytest.raises(UnauthorizedException) as excinfo:
        parse_jwt_token("expired_token")

    assert excinfo.value.code == AuthErrorCode.TOKEN_EXPIRED


@patch("app.modules.auth.jwt.jwt.decode")
def test_parse_jwt_token_invalid(mock_decode):
    mock_decode.side_effect = Exception("Invalid token")

    with pytest.raises(UnauthorizedException) as excinfo:
        parse_jwt_token("invalid_token")

    assert excinfo.value.code == AuthErrorCode.INVALID_TOKEN


def test_get_refresh_token_settings():
    refresh_token = "sample_refresh_token"

    settings = get_refresh_token_settings(refresh_token=refresh_token, expired=False)

    assert settings == {
        "key": "refresh_token",
        "httponly": True,
        "samesite": auth_settings.VIOT_JWT_REFRESH_TOKEN_SAMESITE,
        "secure": auth_settings.VIOT_JWT_REFRESH_TOKEN_SECURE,
        "domain": auth_settings.VIOT_JWT_REFRESH_TOKEN_DOMAIN,
        "value": refresh_token,
        "max_age": 86400000,
    }

    settings_expired = get_refresh_token_settings(refresh_token=refresh_token, expired=True)

    assert settings_expired == {
        "key": "refresh_token",
        "httponly": True,
        "samesite": auth_settings.VIOT_JWT_REFRESH_TOKEN_SAMESITE,
        "secure": auth_settings.VIOT_JWT_REFRESH_TOKEN_SECURE,
        "domain": auth_settings.VIOT_JWT_REFRESH_TOKEN_DOMAIN,
    }
