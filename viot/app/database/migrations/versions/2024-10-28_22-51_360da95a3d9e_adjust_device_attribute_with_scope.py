"""adjust device attribute with scope

Revision ID: 360da95a3d9e
Revises: 5da426951002
Create Date: 2024-10-28 22:51:29.092538

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "360da95a3d9e"
down_revision: str | None = "5da426951002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("device_attribute", sa.Column("scope", sa.SMALLINT(), nullable=False))
    op.drop_index("device_attribute_device_id_idx", table_name="device_attribute")
    op.drop_index("device_attribute_device_id_key_idx", table_name="device_attribute")
    op.drop_column("device_attribute", "device_can_edit")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "device_attribute",
        sa.Column("device_can_edit", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    op.create_index(
        "device_attribute_device_id_key_idx", "device_attribute", ["device_id", "key"], unique=False
    )
    op.create_index(
        "device_attribute_device_id_idx", "device_attribute", ["device_id"], unique=False
    )
    op.drop_column("device_attribute", "scope")
    # ### end Alembic commands ###
