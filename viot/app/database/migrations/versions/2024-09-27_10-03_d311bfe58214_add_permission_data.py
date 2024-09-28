"""add permission data (team profile, team member, team invitation)

Permissions included:
- Team Profile
    - READ
    - MANAGE
- Team Member
    - READ
    - MANAGE
    - DELETE
- Team Invitation
    - READ
    - MANAGE
    - REVOKE

Revision ID: d311bfe58214
Revises: 851c84f685bc
Create Date: 2024-09-27 10:03:29.968056

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy.orm.session import Session

from app.models import Permission
from app.module.auth.permission import (
    TeamInvitationPermission,
    TeamMemberPermission,
    TeamProfilePermission,
)

# revision identifiers, used by Alembic.
revision: str = "d311bfe58214"
down_revision: str | None = "851c84f685bc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

permissions = [
    Permission(scope=p.scope)
    for p in [
        # Team Profile
        TeamProfilePermission.READ,
        TeamProfilePermission.MANAGE,
        # Team Member
        TeamMemberPermission.READ,
        TeamMemberPermission.MANAGE,
        TeamMemberPermission.DELETE,
        # Team Invitation
        TeamInvitationPermission.READ,
        TeamInvitationPermission.MANAGE,
        TeamInvitationPermission.REVOKE,
    ]
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    print("Starting data migration")
    session = Session(bind=op.get_bind())

    # Add all permissions to the database
    session.add_all(permissions)
    session.commit()

    print("Data migration completed")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    print("Starting data migration rollback")

    session = Session(bind=op.get_bind())
    scopes = [permission.scope for permission in permissions]
    session.query(Permission).filter(Permission.scope.in_(scopes)).delete(synchronize_session=False)
    session.commit()

    print("Data migration rollback completed")
    # ### end Alembic commands ###
