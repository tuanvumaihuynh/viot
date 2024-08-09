import logging
from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestException, PermissionDeniedException
from app.modules.auth.models import ViotUserTeam
from app.modules.role import service as role_service

from .models import Team
from .schemas import TeamCreateRequest, TeamUpdateRequest

logger = logging.getLogger(__name__)


async def get_all(*, db: AsyncSession, user_id: UUID) -> list[Team]:
    stmt = (
        select(Team)
        .join(ViotUserTeam, Team.id == ViotUserTeam.team_id)
        .where(ViotUserTeam.viot_user_id == user_id)
    )
    return (await db.execute(stmt)).scalars().all()


async def get(*, db: AsyncSession, id: UUID) -> Team | None:
    stmt = select(Team).where(Team.id == id)
    return (await db.execute(stmt)).scalar()


async def get_or_raise(*, db: AsyncSession, id: UUID) -> Team:
    org = await get(db=db, id=id)
    if not org:
        raise BadRequestException(message="Team not found")
    return org


async def exist_by_id(*, db: AsyncSession, id: UUID) -> bool:
    stmt = select(exists().where(Team.id == id))
    return (await db.execute(stmt)).scalar()


async def is_user_belong_to_any_team(*, db: AsyncSession, user_id: UUID) -> bool:
    stmt = select(exists().where(ViotUserTeam.viot_user_id == user_id))
    return (await db.execute(stmt)).scalar()


async def create(*, db: AsyncSession, request: TeamCreateRequest, user_id: UUID) -> Team:
    """Create Team, allow duplicate team name

    Flow:
    - Create Team
    - Create owner role for the user

    Args:
        db (AsyncSession): db session
        request (TeamCreateRequest): request body
        user_id (UUID): user id

    Raises:
        BadRequestException: Team with this name already exist.

    Returns:
        Team: created Team
    """

    default = not await is_user_belong_to_any_team(db=db, user_id=user_id)
    team = Team(name=request.name, description=request.description, default=default)

    db.add(team)
    await db.flush()

    await role_service.create_owner_role(db=db, team_id=team.id, user_id=user_id)

    return team


async def update(
    *, db: AsyncSession, request: TeamUpdateRequest, team_id: UUID, user_id: UUID
) -> Team:
    team = await get_or_raise(db=db, id=team_id)

    # Validate if user is owner of Team
    if not await role_service.is_team_owner(db=db, team_id=team_id, user_id=user_id):
        logger.warning(f"User {user_id} is not owner of team {team_id}")
        raise PermissionDeniedException(message="User is not owner of this team")

    for field, value in request.model_dump(exclude_none=True).items():
        setattr(team, field, value)

    await db.flush()
    await db.refresh(team)
    return team


async def delete(*, db: AsyncSession, team_id: UUID, user_id: UUID) -> None:
    team = await get_or_raise(db=db, id=team_id)

    # Validate if user is owner of Team
    if not await role_service.is_team_owner(db=db, team_id=team_id, user_id=user_id):
        logger.warning(f"User {user_id} is not owner of team {team_id}")
        raise PermissionDeniedException(message="User is not owner of this team")

    if team.default:
        raise BadRequestException(message="Cannot delete default team")

    stmt = sa_delete(Team).where(Team.id == team_id)
    await db.execute(stmt)
