from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    DOUBLE_PRECISION,
    SMALLINT,
    TEXT,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

from ..constants import DeviceAttributeScope


class DeviceAttribute(Base):
    __tablename__ = "device_attribute"

    device_id: Mapped[UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"), primary_key=True
    )
    key: Mapped[str] = mapped_column(TEXT, primary_key=True)
    scope: Mapped[DeviceAttributeScope] = mapped_column(SMALLINT, primary_key=True)
    last_update: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    bool_v: Mapped[bool | None] = mapped_column(BOOLEAN)
    str_v: Mapped[str | None] = mapped_column(TEXT)
    long_v: Mapped[int | None] = mapped_column(BIGINT)
    double_v: Mapped[float | None] = mapped_column(DOUBLE_PRECISION)
    json_v: Mapped[dict[str, Any] | None] = mapped_column(JSONB(none_as_null=True))

    __table_args__ = (
        UniqueConstraint(
            "device_id", "key", "scope", name="device_attribute_device_id_key_scope_unique"
        ),
    )

    @property
    def value(self) -> bool | str | int | float | dict[str, Any] | None:
        if self.bool_v is not None:
            return self.bool_v
        if self.str_v is not None:
            return self.str_v
        if self.long_v is not None:
            return self.long_v
        if self.double_v is not None:
            return self.double_v
        if self.json_v is not None:
            return self.json_v
        return None
