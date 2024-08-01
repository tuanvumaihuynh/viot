from enum import StrEnum


class MessageType(StrEnum):
    VERIFY_ACCOUNT = "verify_account"
    RESET_PASSWORD = "change_password"
