import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.types import UUID


class UUIDMixin(MappedAsDataclass):
    id = Column(
        "id",
        UUID(as_uuid=True),
        default=uuid.uuid4,
        index=True,
        primary_key=True,
        unique=True,
        nullable=False,
    )


class DateTimeMixin(MappedAsDataclass):
    created_at = Column("created_at", DateTime, server_default=func.now(), nullable=False)
    updated_at = Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())


class Base(DeclarativeBase, MappedAsDataclass, AsyncAttrs):
    __abstract__ = True

    def to_dict(self) -> dict[str, any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
