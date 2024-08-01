from datetime import datetime
from uuid import UUID

from app.schemas import BaseRequest, BaseResponse, PagingResponse


class InvitationCreateRequest(BaseRequest):
    invitee_id: UUID
    inviter_id: UUID


class InvitationResponse(BaseResponse):
    id: UUID
    invitee_id: UUID
    inviter_id: UUID
    organization_id: UUID
    status: str
    invited_at: datetime
    response_at: datetime | None


class PagingInvitationResponse(PagingResponse[InvitationResponse]): ...
