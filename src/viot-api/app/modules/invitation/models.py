from datetime import datetime

from sqlalchemy import TEXT, UUID, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base, UUIDMixin

from .enums import InvitationStatus


class Invitation(Base, UUIDMixin):
    __tablename__ = "invitation"

    team_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("team.id", ondelete="CASCADE"), nullable=False
    )
    inviter_id: Mapped[UUID | None] = mapped_column(UUID, ForeignKey("viot_user.id"), nullable=True)
    invitee_id: Mapped[UUID | None] = mapped_column(UUID, ForeignKey("viot_user.id"), nullable=True)
    status: Mapped[InvitationStatus] = mapped_column(
        TEXT, nullable=False, default=InvitationStatus.PENDING.value, init=False
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), init=False
    )
    responsed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, init=False)
