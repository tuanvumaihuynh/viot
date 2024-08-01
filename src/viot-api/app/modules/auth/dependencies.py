from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database.dependencies import DbSession
from app.exceptions import PermissionDeniedException, UnauthorizedException
from app.modules.auth.constants import AuthErrorCode
from app.modules.auth.models import ViotUser

from . import service as auth_service
from .jwt import JwtPayload, parse_jwt_token

_http_bearer = HTTPBearer(auto_error=False)


def get_jwt_data(
    header: HTTPAuthorizationCredentials | None = Depends(_http_bearer),
) -> JwtPayload:
    if header is None:
        raise UnauthorizedException(message="Invalid token")
    return parse_jwt_token(header.credentials)


# TODO: Implement caching here
async def get_current_user(
    *, db: DbSession, jwt_payload: JwtPayload = Depends(get_jwt_data)
) -> ViotUser:
    user = await auth_service.get(db=db, user_id=jwt_payload.sub)
    if user is None:
        raise UnauthorizedException(message="Not authorized")

    return user


# async def _get_verified_user(user: ViotUser = Depends(_get_current_user)) -> ViotUser:
#     if not user.verified:
#         raise UnauthorizedException("User is not verified")
#     return user


def get_active_user(user: ViotUser = Depends(get_current_user)) -> ViotUser:
    if not user.verified:
        raise UnauthorizedException(code=AuthErrorCode.NOT_VERIFIED, message="User is not verified")
    if user.disabled:
        raise UnauthorizedException(
            code=AuthErrorCode.ACCOUNT_DISABLED, message="User is not active"
        )
    return user


def get_admin_user(user: ViotUser = Depends(get_current_user)) -> ViotUser:
    if not user.is_admin:
        raise PermissionDeniedException(message="You don't have permission to access this resource")
    return user


JwtData = Annotated[JwtPayload, Depends(get_jwt_data)]
CurrentUser = Annotated[ViotUser, Depends(get_current_user)]
CurrentActiveUser = Annotated[ViotUser, Depends(get_active_user)]


RequiredAdminUserDependency = Depends(get_admin_user)
