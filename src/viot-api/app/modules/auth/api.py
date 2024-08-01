from uuid import UUID

from fastapi import APIRouter, Body, Cookie, Query, status
from fastapi.responses import RedirectResponse

from app.config import app_settings
from app.contexts import RequestCtxDependency, ResponseCtxDependency
from app.database.dependencies import DbSession

from . import service as auth_service
from .dependencies import CurrentActiveUser, JwtData
from .schemas import (
    ChangePwdRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    PagingUserResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserUpdateRequest,
)

auth_router = APIRouter()
user_router = APIRouter()


@auth_router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    status_code=status.HTTP_200_OK,
    dependencies=[ResponseCtxDependency],
)
async def login_user(*, db: DbSession, request: LoginRequest = Body(...)):
    return await auth_service.login(db=db, request=request)


@auth_router.post(
    "/logout",
    summary="Logout user",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[ResponseCtxDependency],
)
async def logout_user(
    *, jwt_data: JwtData, refresh_token: str = Cookie(..., alias="refresh_token")
):
    await auth_service.logout(user_id=jwt_data.sub, refresh_token=refresh_token)


@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renew access token",
    status_code=status.HTTP_200_OK,
    dependencies=[ResponseCtxDependency],
)
async def renew_access_token(
    *,
    refresh_token: str = Cookie(..., alias="refresh_token"),
):
    return await auth_service.renew_access_token(refresh_token=refresh_token)


@auth_router.post(
    "/register",
    response_model=UserResponse,
    summary="Register user",
    status_code=status.HTTP_201_CREATED,
    dependencies=[RequestCtxDependency],
)
async def register_user(
    *,
    db: DbSession,
    request: RegisterRequest = Body(...),
):
    return await auth_service.register(db=db, request=request)


@auth_router.post("/forgot_pwd", status_code=status.HTTP_204_NO_CONTENT, summary="Forgot password")
async def forgot_pwd(*, db: DbSession, request: ForgotPasswordRequest = Body(...)):
    await auth_service.forgot_pwd(db=db, request=request)


@auth_router.post("/reset_pwd", status_code=status.HTTP_204_NO_CONTENT, summary="Reset password")
async def reset_pwd(*, db: DbSession, request: ResetPasswordRequest = Body(...)):
    await auth_service.reset_pwd(db=db, request=request)


@auth_router.get(
    "/verify_account",
    summary="Verify account",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    include_in_schema=False,
)
async def verify_account(*, db: DbSession, token: str = Query(...)):
    await auth_service.verify_account(db=db, token=token)
    return RedirectResponse(url=app_settings.VIOT_UI_URL + "/auth/login")


@user_router.get("/me", response_model=UserResponse, summary="Get current user info")
async def get_current_user_info(*, user: CurrentActiveUser):
    return user


@user_router.put(
    "/me/change_pwd",
    summary="Change password of current user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_pwd(*, db: DbSession, user: CurrentActiveUser, request: ChangePwdRequest):
    await auth_service.change_pwd(db=db, user_id=user.id, request=request)


@user_router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
)
async def update_user_current_user(
    *, db: DbSession, user: CurrentActiveUser, request: UserUpdateRequest
):
    return await auth_service.update(db=db, user_id=user.id, request=request)


@user_router.delete(
    "/me",
    summary="Delete current user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_account(*, db: DbSession, user: CurrentActiveUser):
    await auth_service.delete(db=db, user_id=user.id)


@user_router.get("", response_model=PagingUserResponse, summary="Get users in team")
async def get_users(
    *,
    db: DbSession,
    _: CurrentActiveUser,
    team_id: UUID = Query(...),
    query_str: str = Query(
        None, alias="q", pattern=r"^[ -~]+$", description="Search query by email"
    ),
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, lt=100),
    sort_by: list[str] = Query([], alias="sort_by[]"),
    descending: list[bool] = Query([], alias="descending[]"),
):
    return await auth_service.get_all(
        db=db,
        team_id=team_id,
        query_str=query_str,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        descending=descending,
    )


@user_router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by id in team",
)
async def get_user(
    *,
    db: DbSession,
    _: CurrentActiveUser,
    user_id: UUID,
    team_id: UUID = Query(...),
):
    return await auth_service.get_or_raise(db=db, user_id=user_id, team_id=team_id)
