import re
from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.schemas import (
    BaseRequest,
    BaseResponse,
    NameStr,
    PagingResponse,
)


class JwtPayload(BaseModel):
    jti: str
    exp: int
    sub: str
    email: str


PASSWORD_PATTERN = re.compile(r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{8,20}$")


class LoginRequest(BaseRequest):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not PASSWORD_PATTERN.match(password):
            raise ValueError(
                "Password must be between 8 and 20 characters and contain at least one digit and one special character"
            )
        return password


class TokenResponse(BaseResponse):
    token_type: str
    access_token: str


class LoginResponse(TokenResponse): ...


class RegisterRequest(LoginRequest):
    first_name: NameStr
    last_name: NameStr


class ForgotPasswordRequest(BaseRequest):
    email: EmailStr


class ResetPasswordRequest(BaseRequest):
    token: str
    new_password: str = Field(..., min_length=8, max_length=20)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not PASSWORD_PATTERN.match(password):
            raise ValueError(
                "Password must be between 8 and 20 characters and contain at least one digit and one special character"
            )
        return password


class ChangePwdRequest(BaseRequest):
    old_password: str = Field(..., min_length=8, max_length=20)
    new_password: str = Field(..., min_length=8, max_length=20)

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        if self.old_password == self.new_password:
            raise ValueError("Old password and new password must be different")
        return self

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not PASSWORD_PATTERN.match(password):
            raise ValueError(
                "Password must be between 8 and 20 characters and contain at least one digit and one special character"
            )
        return password


class UserUpdateRequest(BaseRequest):
    first_name: NameStr | None = Field(None)
    last_name: NameStr | None = Field(None)


class UserResponse(BaseResponse):
    id: UUID
    first_name: str
    last_name: str
    email: str
    role: str
    created_at: datetime
    updated_at: datetime | None


class PagingUserResponse(PagingResponse[UserResponse]): ...
