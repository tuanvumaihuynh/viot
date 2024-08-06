import pytest
import pytest_asyncio
import uvloop
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import model_include  # noqa: F401
from app.main import app
from app.models import Base
from app.modules.auth.schemas import RegisterRequest

from .database import async_engine


@pytest.fixture(scope="session")
def event_loop_policy():
    return uvloop.EventLoopPolicy()


@pytest_asyncio.fixture(scope="session")
async def engine_fixture():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db(engine_fixture):
    async_session = AsyncSession(engine_fixture)
    async_session.begin_nested()
    yield async_session
    await async_session.rollback()
    await async_session.close()


@pytest_asyncio.fixture(scope="module")
async def client():
    """Fixture to create a FastAPI test client."""
    # instead of app = app, use this to avoid the DeprecationWarning:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def user(db: AsyncSession):
    from app.modules.auth.service import create

    request = RegisterRequest(
        email="test@gmail.com",
        first_name="Test",
        last_name="User",
        password="!Test123",
    )
    user = await create(db=db, request=request)
    return user
