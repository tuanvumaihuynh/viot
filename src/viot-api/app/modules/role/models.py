from sqlalchemy import TEXT, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, DateTimeMixin, UUIDMixin


class Role(Base, UUIDMixin, DateTimeMixin):
    __tablename__ = "role"

    team_id: Mapped[UUID] = mapped_column(ForeignKey("team.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permission", back_populates="roles", init=False
    )

    __table_args__ = (UniqueConstraint("name", "team_id"),)


class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("role.id", ondelete="CASCADE"), primary_key=True
    )

    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"), primary_key=True)


class Permission(Base, DateTimeMixin, UUIDMixin):
    __tablename__ = "permission"

    scope: Mapped[str] = mapped_column(TEXT, nullable=False)
    action: Mapped[str] = mapped_column(TEXT, nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        secondary="role_permission", back_populates="permissions", init=False
    )

    __table_args__ = (UniqueConstraint("scope", "action"),)
