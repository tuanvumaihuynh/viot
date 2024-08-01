from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import app_settings
from app.database.cache import redis_client
from app.exceptions import register_exception_handler
from app.routes import router
from app.utils.serializer import MsgSpecJSONResponse


@asynccontextmanager
async def _lifespan(app: FastAPI):
    await redis_client.open()

    yield

    await redis_client.close()


def create_app() -> FastAPI:
    from app import models  # noqa: F401

    app = FastAPI(
        **app_settings.FASTAPI_CONFIG,
        default_response_class=MsgSpecJSONResponse,
        lifespan=_lifespan,
    )

    register_middleware(app)

    register_router(app)

    register_exception_handler(app)

    return app


def register_middleware(app: FastAPI) -> None:
    # CORS needs to be added last
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.VIOT_API_CORS_ORIGINS,
        allow_credentials=app_settings.VIOT_API_ALLOW_CREDENTIALS,
        allow_methods=app_settings.VIOT_API_ALLOW_METHODS,
        allow_headers=app_settings.VIOT_API_CORS_HEADERS,
    )


def register_router(app: FastAPI) -> None:
    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    app.include_router(router, prefix=app_settings.VIOT_API_PREFIX)
