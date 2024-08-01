from abc import ABC
from datetime import datetime
from math import ceil
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, StringConstraints, computed_field

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

NameStr = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z ]+$", strip_whitespace=True, min_length=1, max_length=20),
]
QueryStr = Annotated[str, StringConstraints(pattern=r"^[ -~]+$", min_length=1)]


class BaseRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class BaseResponse(BaseModel):
    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.strftime(DATETIME_FORMAT)},
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


T = TypeVar("T", bound=BaseResponse)


class PagingResponse(BaseResponse, ABC, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @computed_field
    @property
    def pages(self) -> int:
        return ceil(self.total / self.page_size)
