from sqlalchemy import TEXT, UUID, Boolean, Computed, ForeignKey, Index, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.types import TSVectorType
from app.models import Base, DateTimeMixin, UUIDMixin
from app.modules.team.models import Team

from .enums import ViotUserRole

# About full-text search: https://stackoverflow.com/questions/13361161/sqlalchemy-with-postgresql-and-full-text-search/73999486#73999486


class ViotUser(Base, UUIDMixin, DateTimeMixin):
    __tablename__ = "viot_user"

    first_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    last_name: Mapped[str] = mapped_column(TEXT, nullable=False)
    email: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False, index=True)
    email_vector: Mapped[str] = mapped_column(
        TSVectorType("email", regconfig="pg_catalog.simple", weights={"email": "A"}),
        Computed("to_tsvector('pg_catalog.simple', \"email\")", persisted=True),
        nullable=False,
        init=False,
    )
    password: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    role: Mapped[ViotUserRole] = mapped_column(
        TEXT, nullable=False, default=ViotUserRole.USER.value
    )
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    teams: Mapped[list[Team]] = relationship(
        secondary="viot_user_team", back_populates="users", init=False
    )

    @property
    def is_admin(self) -> bool:
        return self.role == ViotUserRole.ADMIN.value

    __table_args__ = (Index("viot_user_email_vector_idx", email_vector, postgresql_using="gin"),)


class ViotUserTeam(Base, DateTimeMixin):
    __tablename__ = "viot_user_team"

    viot_user_id: Mapped[UUID] = mapped_column(ForeignKey("viot_user.id"), primary_key=True)
    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("role.id", ondelete="CASCADE"), primary_key=True
    )
