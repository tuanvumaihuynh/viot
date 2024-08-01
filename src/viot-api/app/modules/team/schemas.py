from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas import BaseRequest, BaseResponse, NameStr


class TeamCreateRequest(BaseRequest):
    name: NameStr
    description: str | None = Field(None, min_length=3, max_length=255)


class TeamUpdateRequest(BaseRequest):
    team_id: UUID
    name: NameStr | None = Field(None)
    description: str | None = Field(None, min_length=3, max_length=255)


class TeamResponse(BaseResponse):
    id: UUID
    name: str
    description: str | None
    default: bool
    created_at: datetime
    updated_at: datetime | None


# Pagination nani???
class TeamListResponse(BaseResponse):
    items: list[TeamResponse]
