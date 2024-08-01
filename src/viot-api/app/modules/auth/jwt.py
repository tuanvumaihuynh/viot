import logging
import uuid
from datetime import datetime, timedelta
from uuid import UUID

import jwt

from app.exceptions import UnauthorizedException

from .config import auth_settings
from .constants import AuthErrorCode
from .schemas import JwtPayload

logger = logging.getLogger(__name__)


def create_access_token(
    *,
    user_id: UUID,
    user_email: str,
    expire_time: timedelta = timedelta(seconds=auth_settings.VIOT_JWT_ACCESS_TOKEN_EXP),
) -> str:
    data = JwtPayload(
        jti=str(uuid.uuid4()),
        exp=int((datetime.now() + expire_time).timestamp()),
        sub=str(user_id),
        email=user_email,
    )
    return jwt.encode(
        data.model_dump(), auth_settings.VIOT_JWT_SECRET, algorithm=auth_settings.VIOT_JWT_ALG
    )


def create_refresh_token(
    *,
    user_id: UUID,
    user_email: str,
    expire_time: timedelta = timedelta(seconds=auth_settings.VIOT_JWT_REFRESH_TOKEN_EXP),
) -> str:
    return create_access_token(user_id=user_id, user_email=user_email, expire_time=expire_time)


def parse_jwt_token(token: str) -> JwtPayload:
    try:
        payload = jwt.decode(
            token, auth_settings.VIOT_JWT_SECRET, algorithms=[auth_settings.VIOT_JWT_ALG]
        )
        return JwtPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(
            code=AuthErrorCode.TOKEN_EXPIRED, message="Token expired"
        ) from None
    except Exception as e:
        logger.error("Invalid token")
        logger.exception(e)
        raise UnauthorizedException(
            code=AuthErrorCode.INVALID_TOKEN, message="Invalid token"
        ) from e


def get_refresh_token_settings(refresh_token: str, expired: bool = False) -> dict[str, any]:
    base_cookie = {
        "key": "refresh_token",
        "httponly": True,
        "samesite": auth_settings.VIOT_JWT_REFRESH_TOKEN_SAMESITE,
        "secure": auth_settings.VIOT_JWT_REFRESH_TOKEN_SECURE,
        "domain": auth_settings.VIOT_JWT_REFRESH_TOKEN_DOMAIN,
    }
    if expired:
        return base_cookie

    return {
        **base_cookie,
        "value": refresh_token,
        "max_age": 86400000,
    }
