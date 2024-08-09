from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import ViotUser, ViotUserTeam
from app.modules.team.models import Team

from .constants import TEAM_ROLE_OWNER, TEAM_ROLE_OWNER_DESCRIPTION
from .models import Permission, Role, RolePermission


async def is_team_owner(*, db: AsyncSession, user_id: UUID, team_id: UUID) -> bool:
    stmt = select(
        select(Role)
        .join(ViotUserTeam, Role.team_id == ViotUserTeam.team_id)
        .join(Team, Role.team_id == Team.id)
        .join(ViotUser, ViotUserTeam.viot_user_id == ViotUser.id)
        .where(
            ViotUser.id == user_id,
            Team.id == team_id,
            Role.name == TEAM_ROLE_OWNER,
        )
        .exists()
    )
    return (await db.execute(stmt)).scalar()


async def is_user_has_permission(
    *,
    db: AsyncSession,
    user_id: UUID,
    scope: str,
    action: str,
    org_id: UUID,
) -> bool:
    stmt = (
        select(Permission)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .join(Role, RolePermission.role_id == Role.id)
        .join(ViotUserTeam, Role.team_id == ViotUserTeam.team_id)
        .join(Team, Role.team_id == Team.id)
        .join(ViotUser, ViotUserTeam.viot_user_id == ViotUser.id)
        .where(
            ViotUser.id == user_id,
            Permission.scope == scope,
            Permission.action == action,
            Team.id == org_id,
        )
    )

    stmt = select(stmt.exists())
    return (await db.execute(stmt)).scalar()


# async def create(*, db: AsyncSession, request: RoleCreateRequest, team_id: UUID) -> Role:
#     role = Role(name=request.name, description=request.description, team_id=team_id)
#     # Need to validate something
#     db.add(role)
#     await db.flush()
#     return role


async def create_owner_role(*, db: AsyncSession, team_id: UUID, user_id: UUID) -> Role:
    role = Role(
        name=TEAM_ROLE_OWNER,
        description=TEAM_ROLE_OWNER_DESCRIPTION,
        team_id=team_id,
    )

    # Assign all permissions to the owner role
    permissions = await get_all_permissions(db=db)
    role.permissions.extend(permissions)
    db.add(role)
    await db.flush()

    # Assign the owner role to the user
    stmt = insert(ViotUserTeam).values(viot_user_id=user_id, team_id=team_id, role_id=role.id)
    await db.execute(stmt)

    return role


async def get_all_permissions(*, db: AsyncSession) -> list[Permission]:
    stmt = select(Permission)
    return (await db.execute(stmt)).scalars().all()
