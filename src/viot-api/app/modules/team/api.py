from uuid import UUID

from fastapi import APIRouter, Path, status

from app.database.dependencies import DbSession
from app.modules.auth.dependencies import CurrentActiveUser

# from app.modules.invitation import service as org_invitation_service
from . import service as team_service
from .schemas import TeamCreateRequest, TeamListResponse, TeamResponse

router = APIRouter()


@router.get(
    "",
    response_model=TeamListResponse,
    summary="Get all teams of current user",
    status_code=status.HTTP_200_OK,
    dependencies=[],
)
async def get_all(*, db: DbSession, user: CurrentActiveUser):
    teams = await team_service.get_all(db=db, user_id=user.id)
    return {
        "items": teams,
    }


@router.post(
    "",
    response_model=TeamResponse,
    summary="Create team",
    status_code=status.HTTP_201_CREATED,
)
async def create_team(*, db: DbSession, user: CurrentActiveUser, request: TeamCreateRequest):
    return await team_service.create(db=db, request=request, user_id=user.id)


@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update team",
    status_code=status.HTTP_200_OK,
)
async def update_team(
    *,
    db: DbSession,
    user: CurrentActiveUser,
    team_id: UUID = Path(...),
    request: TeamCreateRequest,
):
    return await team_service.update(db=db, team_id=team_id, request=request, user_id=user.id)


@router.delete(
    "/{team_id}",
    summary="Delete team",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_team(
    *,
    db: DbSession,
    user: CurrentActiveUser,
    team_id: UUID = Path(...),
):
    await team_service.delete(db=db, team_id=team_id, user_id=user.id)


# Invitations


# @router.get(
#     "/{team_id}/invitations",
#     response_model=PagingInvitationResponse,
#     summary="Get all invitations of team",
#     dependencies=[],
# )
# async def get_invitations(
#     *,
#     db: DbSession,
#     team_id: UUID = Path(...),
#     status: InvitationStatus | None = Query(None, description="Filter by status"),
#     page: int = Query(1, gt=0),
#     page_size: int = Query(10, gt=0, lt=100),
#     sort_by: list[str] = Query([], alias="sort_by[]"),
#     descending: list[bool] = Query([], alias="descending[]"),
# ):
#     return
#     # return await org_invitation_service.get_all(
#     #     db=db,
#     #     org_id=org_id,
#     #     status=status,
#     #     page=page,
#     #     page_size=page_size,
#     #     sort_by=sort_by,
#     #     descending=descending,
#     # )


# @router.post(
#     "/{team_id}/invitations",
#     response_model=InvitationResponse,
#     summary="Invite user to team",
#     dependencies=[],
# )
# async def invite_user_to_org(
#     *,
#     db: DbSession,
#     user: CurrentActiveUser,
#     team_id: UUID = Path(...),
#     request: InvitationCreateRequest,
# ):
#     return
#     if user.id != request.inviter_id:
#         raise BadRequestException("You can only invite user as yourself")
#     # return await org_invitation_service.create(db=db, org_id=org_id, request=request)
