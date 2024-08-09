import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlalchemy import exists, select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer, load_only

from app.config import app_settings
from app.contexts import request_ctx, response_ctx
from app.database.cache import redis_client
from app.database.service import (
    PagingDataclass,
    search_sort_paginate,
)
from app.exceptions import BadRequestException, UnauthorizedException
from app.modules.auth.jwt import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_settings,
    parse_jwt_token,
)
from app.modules.celery_task.tasks.mail_task import (
    send_verify_account_email,
)

from .config import auth_settings
from .constants import REDIS_REFRESH_TOKEN_PREFIX, REDIS_RESET_PASSWORD_PREFIX
from .models import ViotUser
from .schemas import (
    ChangePwdRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserUpdateRequest,
)
from .utils import hash_password, verify_password

logger = logging.getLogger(__name__)


async def authenticate(*, db: AsyncSession, request: LoginRequest) -> ViotUser:
    user = await get_by_email_or_raise(db=db, email=request.email)
    if not verify_password(request.password, user.password):
        logger.warning(f"Incorrect password for user with email {request.email}")
        raise UnauthorizedException(message="Wrong password")
    return user


async def login(*, db: AsyncSession, request: LoginRequest) -> dict[str, str]:
    user = await authenticate(db=db, request=request)

    response = response_ctx.get()
    refresh_token = create_refresh_token(user_id=user.id, user_email=user.email)
    response.set_cookie(**get_refresh_token_settings(refresh_token))

    key = f"{REDIS_REFRESH_TOKEN_PREFIX}:{user.id}:{refresh_token}"
    await redis_client.set(key, "1", auth_settings.VIOT_JWT_REFRESH_TOKEN_EXP)

    return {
        "access_token": create_access_token(user_id=user.id, user_email=user.email),
        "token_type": "bearer",
    }


async def logout(*, user_id: UUID, refresh_token: str) -> None:
    response = response_ctx.get()
    response.delete_cookie(**get_refresh_token_settings(refresh_token, expired=True))

    # Revoking all refresh tokens
    key = f"{REDIS_REFRESH_TOKEN_PREFIX}:{user_id}:*"
    await redis_client.delete(key)


async def renew_access_token(*, refresh_token: str) -> dict[str, str]:
    jwt_data = parse_jwt_token(refresh_token)

    key = f"{REDIS_REFRESH_TOKEN_PREFIX}:{jwt_data.sub}:{refresh_token}"
    if not await redis_client.exists(key):
        raise UnauthorizedException(message="Invalid refresh token")

    return {
        "token_type": "bearer",
        "access_token": create_access_token(user_id=jwt_data.sub),
    }


async def register(*, db: AsyncSession, request: RegisterRequest) -> ViotUser:
    if await exist_by_email(db=db, email=request.email):
        raise BadRequestException(message=f"User with email {request.email} already exists")

    user = await create(db=db, request=request)

    verify_token = create_access_token(
        user_id=user.id, user_email=user.email, expire_time=timedelta(days=1)
    )

    fastapi_request = request_ctx.get()
    base_url = str(fastapi_request.base_url).rstrip("/")

    # Celery task
    callback_url = (
        f"{base_url}{app_settings.VIOT_API_PREFIX}/auth/verify_account?token={verify_token}"
    )
    send_verify_account_email.delay(
        email=user.email,
        name=f"{user.first_name} {user.last_name}",
        callback_url=callback_url,
    )

    return user


async def forgot_pwd(*, db: AsyncSession, request: ForgotPasswordRequest) -> None:
    user = await get_by_email(db=db, email=request.email)
    if not user:
        return
    expire_time = timedelta(minutes=10)
    reset_token = create_access_token(
        user_id=user.id, user_email=user.email, expire_time=expire_time
    )
    await redis_client.set(
        f"{REDIS_RESET_PASSWORD_PREFIX}:{user.id}:{reset_token}", "1", expire_time.seconds
    )

    send_verify_account_email.delay(
        email=user.email,
        name=f"{user.first_name} {user.last_name}",
        callback_url=f"{app_settings.VIOT_UI_URL}/auth/reset-password?token={reset_token}",
    )


async def reset_pwd(*, db: AsyncSession, request: ResetPasswordRequest) -> None:
    try:
        jwt_data = parse_jwt_token(request.token)
    except Exception as e:
        logger.exception(e)
        raise BadRequestException(message="Invalid token") from None

    stmt = (
        select(ViotUser)
        .options(load_only(ViotUser.id, ViotUser.password))
        .where(ViotUser.id == jwt_data.sub)
    )
    user = (await db.execute(stmt)).scalar()

    if user is None:
        raise BadRequestException(message="Invalid token")

    if verify_password(request.new_password, user.password):
        raise BadRequestException(
            message="New password must be different from the current password"
        )

    stmt = (
        sa_update(ViotUser)
        .where(ViotUser.email == jwt_data.email)
        .values(password=hash_password(request.new_password))
    )
    await db.execute(stmt)

    # Revoking all refresh tokens
    key = f"{REDIS_REFRESH_TOKEN_PREFIX}:{user.id}:*"
    await redis_client.delete(key)


async def verify_account(*, db: AsyncSession, token: str) -> None:
    try:
        jwt_data = parse_jwt_token(token)
    except Exception as e:
        logger.exception(e)
        raise BadRequestException(message="Invalid token") from None

    stmt = sa_update(ViotUser).where(ViotUser.email == jwt_data.email).values(verified=True)
    await db.execute(stmt)


async def change_pwd(*, db: AsyncSession, user_id: UUID, request: ChangePwdRequest) -> None:
    stmt = select(ViotUser.password).where(ViotUser.id == user_id)
    current_pwd = (await db.execute(stmt)).scalar()
    if not verify_password(request.old_password, current_pwd):
        raise BadRequestException(message="Current password is incorrect")

    stmt = (
        sa_update(ViotUser)
        .where(ViotUser.id == user_id)
        .values(password=hash_password(request.new_password))
    )
    await db.execute(stmt)


################################################################################
# Belong to user
################################################################################


async def get_all(
    *,
    db: AsyncSession,
    team_id: UUID,
    query_str: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: list[str] | None = None,
    descending: list[bool] | None = None,
) -> PagingDataclass[ViotUser]:
    stmt = (
        select(ViotUser)
        .options(defer(ViotUser.password), defer(ViotUser.email_vector))
        .where(ViotUser.teams.any(id=team_id))
    )
    return await search_sort_paginate(
        db=db,
        stmt=stmt,
        model_cls=ViotUser,
        page=page,
        page_size=page_size,
        search_attr=ViotUser.email_vector,
        query_str=query_str,
        sort_by=sort_by,
        descending=descending,
    )


async def exist_by_id(*, db: AsyncSession, id: UUID) -> bool:
    stmt = select(exists().where(ViotUser.id == id))
    return (await db.execute(stmt)).scalar()


async def exist_by_email(*, db: AsyncSession, email: str) -> bool:
    stmt = select(exists().where(ViotUser.email == email))
    return (await db.execute(stmt)).scalar()


async def get_by_email(*, db: AsyncSession, email: str) -> ViotUser | None:
    stmt = select(ViotUser).where(ViotUser.email == email)
    return (await db.execute(stmt)).scalar()


async def get_by_email_or_raise(*, db: AsyncSession, email: str) -> ViotUser:
    user = await get_by_email(db=db, email=email)
    if user is None:
        logger.warning(f"User with email {email} not found")
        raise BadRequestException(message="User with this email not exist")
    return user


async def get(*, db: AsyncSession, user_id: UUID, team_id: UUID | None = None) -> ViotUser | None:
    stmt = select(ViotUser).where(ViotUser.id == user_id)
    if team_id:
        stmt = stmt.where(ViotUser.teams.any(id=team_id))
    return (await db.execute(stmt)).scalar()


async def get_or_raise(*, db: AsyncSession, user_id: UUID, team_id: UUID | None = None) -> ViotUser:
    user = await get(db=db, user_id=user_id, team_id=team_id)
    if user is None:
        logger.warning(f"User with id {user_id} not found")
        raise BadRequestException(message="User with this id not exist")
    return user


async def create(*, db: AsyncSession, request: RegisterRequest) -> ViotUser:
    user = ViotUser(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        password=hash_password(request.password),
    )
    db.add(user)
    await db.flush()
    return user


async def update(*, db: AsyncSession, request: UserUpdateRequest, user_id: UUID) -> ViotUser:
    stmt = (
        sa_update(ViotUser)
        .where(ViotUser.id == user_id)
        .values(first_name=request.first_name, last_name=request.last_name)
    )
    await db.execute(stmt)

    return await get(db=db, user_id=user_id)


async def delete(*, db: AsyncSession, user_id: UUID) -> None:
    stmt = sa_delete(ViotUser).where(ViotUser.id == user_id).returning(ViotUser.id)
    result = (await db.execute(stmt)).scalar()
    if result is None:
        raise BadRequestException(message="User with this id not found")
