"""add device permission data and update owner role permissions

Permissions included:
- Team Devices
    - READ
    - MANAGE
    - DELETE

We also need to add permissions to team Owner role and team Member role.


Revision ID: 3d19e8d3338d
Revises: 5fce78f4bb4f
Create Date: 2024-09-30 09:51:45.776581

"""

from collections.abc import Sequence
from typing import Any

from alembic import op
from sqlalchemy import delete, insert, select
from sqlalchemy.orm.session import Session

from app.models import Permission, Role, RolePermission
from app.module.auth.permission import TeamDevicePermission
from app.module.team.constants import TEAM_ROLE_OWNER

# revision identifiers, used by Alembic.
revision: str = "3d19e8d3338d"
down_revision: str | None = "5fce78f4bb4f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


permissions = [
    Permission(scope=p.scope)
    for p in [
        # Team Devices
        TeamDevicePermission.READ,
        TeamDevicePermission.MANAGE,
        TeamDevicePermission.DELETE,
    ]
]

role_owner_ids_stmt = select(Role.id).where(Role.name == TEAM_ROLE_OWNER)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    print("Starting data migration for team device permissions")
    session = Session(bind=op.get_bind())

    # Add all permissions to the database
    print("Adding permissions to the database")
    session.add_all(permissions)
    session.commit()

    # Update team Owner role permissions
    print("Updating team Owner role permissions")
    team_owner_ids = session.execute(role_owner_ids_stmt).scalars().all()
    print("Team Owner role IDs:", team_owner_ids)

    values: list[dict[str, Any]] = []
    for permission in permissions:
        for role_id in team_owner_ids:
            values.append({"role_id": role_id, "permission_id": permission.id})

    stmt = insert(RolePermission).values(values)
    session.execute(stmt)

    print("Data migration for team device permissions completed")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    print("Starting data rollback for team device permissions")
    session = Session(bind=op.get_bind())

    team_owner_ids = session.execute(role_owner_ids_stmt).scalars().all()
    print("Team Owner role IDs:", team_owner_ids)

    scopes = [p.scope for p in permissions]
    permission_ids = (
        session.execute(select(Permission.id).where(Permission.scope.in_(scopes))).scalars().all()
    )
    print("Permission IDs:", permission_ids)

    stmt = delete(RolePermission).where(
        RolePermission.role_id.in_(team_owner_ids),
        RolePermission.permission_id.in_(permission_ids),
    )
    session.execute(stmt)

    stmt = delete(Permission).where(Permission.scope.in_(scopes))
    session.execute(stmt)
    session.commit()

    print("Data rollback for team device permissions completed")
    # ### end Alembic commands ###
