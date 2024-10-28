from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.common.dto import BaseOutDto

from ..constants import DeviceAttributeScope
from ..model.device_attribute import DeviceAttribute
from ..repository.device_attribute_repository import KeyWithScope


class DeviceAttributeDto(BaseOutDto):
    last_update: datetime
    key: str
    value: Any

    @classmethod
    def from_model(cls, model: DeviceAttribute) -> "DeviceAttributeDto":
        return cls(last_update=model.last_update, key=model.key, value=model.value)


class ScopeKeysDto(BaseModel):
    server_scope: set[str] = Field(set(), alias="SERVER_SCOPE")
    shared_scope: set[str] = Field(set(), alias="SHARED_SCOPE")
    client_scope: set[str] = Field(set(), alias="CLIENT_SCOPE")

    @classmethod
    def from_key_with_scopes(cls, kws: list[KeyWithScope]) -> "ScopeKeysDto":
        return cls(
            SERVER_SCOPE={k.key for k in kws if k.scope == DeviceAttributeScope.SERVER_SCOPE},
            SHARED_SCOPE={k.key for k in kws if k.scope == DeviceAttributeScope.SHARED_SCOPE},
            CLIENT_SCOPE={k.key for k in kws if k.scope == DeviceAttributeScope.CLIENT_SCOPE},
        )
