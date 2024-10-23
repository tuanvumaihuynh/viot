"""add rule permission data

Revision ID: 5da426951002
Revises: d39146d49608
Create Date: 2024-10-23 08:28:28.593578

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy.orm.session import Session

from app.database.migrations.repository import (
    delete_permissions,
    get_permission_ids_by_scopes,
    get_role_owner_ids,
    remove_owner_permissions,
    save_permissions,
    update_owner_permissions,
)
from app.models import Permission
from app.module.auth.permission import TeamRulePermission

# revision identifiers, used by Alembic.
revision: str = "5da426951002"
down_revision: str | None = "d39146d49608"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


permissions = [
    Permission(scope=p.scope, title=p.title, description=p.description)
    for p in [
        # Team Rules
        TeamRulePermission.READ,
        TeamRulePermission.MANAGE,
        TeamRulePermission.DELETE,
    ]
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    print("Starting data migration for team rule permissions")
    session = Session(bind=op.get_bind())

    # Add all permissions to the database
    save_permissions(session, permissions)

    # Update team Owner role permissions
    role_owner_ids = get_role_owner_ids(session)

    update_owner_permissions(session, role_owner_ids, permissions)

    session.commit()
    print("Data migration for team rule permissions completed")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    print("Starting data rollback for team rule permissions")
    session = Session(bind=op.get_bind())

    role_owner_ids = get_role_owner_ids(session)

    scopes = [p.scope for p in permissions]
    permission_ids = get_permission_ids_by_scopes(session, scopes)

    remove_owner_permissions(session, role_owner_ids, permission_ids)

    delete_permissions(session, permission_ids)

    session.commit()

    print("Data rollback for team rule permissions completed")
    # ### end Alembic commands ###