from typing import TYPE_CHECKING

from sqlalchemy import TEXT, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, DateTimeMixin, UUIDMixin

if TYPE_CHECKING:
    from app.modules.auth.models import ViotUser


class Team(Base, DateTimeMixin, UUIDMixin):
    __tablename__ = "team"

    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    default: Mapped[bool] = mapped_column(Boolean, nullable=False)

    users: Mapped[list["ViotUser"]] = relationship(
        secondary="viot_user_team", back_populates="teams", init=False
    )
