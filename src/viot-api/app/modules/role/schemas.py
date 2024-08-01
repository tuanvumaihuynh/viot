from uuid import UUID

from pydantic import Field

from app.schemas import BaseRequest, BaseResponse, NameStr


class PermissionResponse(BaseResponse):
    resource: str
    action: str
    description: str | None


class RoleCreateRequest(BaseRequest):
    name: NameStr
    description: str | None = Field(None, min_length=3, max_length=255)
    permission_ids: list[UUID]


class RoleResponse(BaseResponse):
    name: NameStr
    description: str | None = Field(None, min_length=3, max_length=255)
    permissions: list[PermissionResponse]
