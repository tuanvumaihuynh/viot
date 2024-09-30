"""device gateway subdevice

Revision ID: 5fce78f4bb4f
Revises: 52e3a6414408
Create Date: 2024-09-30 08:46:01.557524

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5fce78f4bb4f"
down_revision: str | None = "d311bfe58214"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.TEXT(), nullable=False, unique=True),
        sa.Column("description", sa.TEXT(), nullable=False),
        sa.Column("device_type", sa.SMALLINT(), nullable=False),
        sa.Column("token", sa.TEXT(), nullable=False),
        sa.Column("status", sa.SMALLINT(), nullable=False),
        sa.Column("image_url", sa.TEXT(), nullable=True),
        sa.Column("disabled", sa.Boolean(), nullable=False),
        sa.Column("last_connection", sa.DateTime(True), nullable=True),
        sa.Column("meta_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("team_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(True), nullable=False),
        sa.Column("updated_at", sa.DateTime(True), nullable=True),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "gateways",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["id"], ["devices.id"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sub_devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("uplink_protocol", sa.SMALLINT(), nullable=False),
        sa.Column("gateway_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["gateway_id"], ["gateways.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["id"], ["devices.id"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sub_devices")
    op.drop_table("gateways")
    op.drop_table("devices")
    # ### end Alembic commands ###
