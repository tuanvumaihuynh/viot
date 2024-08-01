import logging

from fastapi import FastAPI, Request, status

from app.utils.serializer import MsgSpecJSONResponse

logger = logging.getLogger(__name__)


class CommonError:
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"


class ViotException(Exception): ...


class ViotHttpException(ViotException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        code: str = CommonError.INTERNAL_SERVER_ERROR,
        message: str = "Something went wrong",
        headers: dict | None = None,
    ) -> None:
        self.status_code = self.STATUS_CODE
        self.code = code
        self.message = message
        self.headers = headers
        super().__init__(message)


class BadRequestException(ViotHttpException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST

    def __init__(self, *, code=CommonError.BAD_REQUEST, message: str = "Bad request") -> None:
        super().__init__(code=code, message=message)


class UnauthorizedException(ViotHttpException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, code=CommonError.UNAUTHORIZED, message: str = "Unauthorized") -> None:
        super().__init__(
            code=code,
            message=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(ViotHttpException):
    STATUS_CODE = status.HTTP_403_FORBIDDEN

    def __init__(
        self, *, code=CommonError.PERMISSION_DENIED, message: str = "Permission denied"
    ) -> None:
        super().__init__(code=code, message=message)


class NotFoundException(ViotHttpException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND

    def __init__(self, *, code=CommonError.NOT_FOUND, message: str = "Resource not found") -> None:
        super().__init__(code=code, message=message)


class ConflictException(ViotHttpException):
    STATUS_CODE = status.HTTP_409_CONFLICT

    def __init__(self, *, code=CommonError.CONFLICT, message: str = "Conflict") -> None:
        super().__init__(code=code, message=message)


def _handle_base_exception(_: Request, exc: ViotHttpException) -> MsgSpecJSONResponse:
    return MsgSpecJSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
        headers=exc.headers,
    )


def _handle_all_exception(request: Request, exc: Exception) -> MsgSpecJSONResponse:
    logger.error(f"Error: {str(exc)}")
    return MsgSpecJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": CommonError.INTERNAL_SERVER_ERROR,
            "message": "Something went wrong",
        },
    )


def register_exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(ViotHttpException, _handle_base_exception)
    app.add_exception_handler(Exception, _handle_all_exception)
