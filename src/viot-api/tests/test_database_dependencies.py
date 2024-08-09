from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db as _get_db


@pytest_asyncio.fixture
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in _get_db():
        yield session
        await session.commit()


async def test_get_db_exception(get_db: AsyncSession):
    with patch.object(get_db, "execute", side_effect=Exception("Test exception")):
        with pytest.raises(Exception) as exc_info:
            await get_db.execute(text("SELECT 1"))
        assert str(exc_info.value) == "Test exception"
