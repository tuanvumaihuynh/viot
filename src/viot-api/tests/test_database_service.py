from unittest.mock import Mock

import pytest
from sqlalchemy import Computed, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, Mapped, mapped_column

from app.database.service import PagingDataclass, search_sort_paginate
from app.database.types import TSVectorType
from app.models import Base, DateTimeMixin, UUIDMixin


class MockModel(Base, UUIDMixin, DateTimeMixin):
    __tablename__ = "mock_model"

    some_attr: Mapped[str] = mapped_column(String, nullable=False)
    attr_with_tsvector: Mapped[str] = mapped_column(
        TSVectorType("some_attr", regconfig="pg_catalog.simple", weights={"some_attr": "A"}),
        Computed("to_tsvector('pg_catalog.simple', \"some_attr\")", persisted=True),
        nullable=False,
        init=False,
    )


async def test_search_sort_paginate_no_query_str(db: AsyncSession):
    result = await search_sort_paginate(
        db=db,
        stmt=None,
        model_cls=MockModel,
        page=1,
        page_size=10,
    )
    assert isinstance(result, PagingDataclass)
    assert result.page == 1
    assert result.page_size == 10
    assert result.items == []
    assert result.total == 0


async def test_search_sort_paginate_with_query_str(db: AsyncSession):
    result = await search_sort_paginate(
        db=db,
        stmt=select(MockModel),
        model_cls=MockModel,
        query_str="test",
        search_attr=MockModel.some_attr,
        page=1,
        page_size=10,
    )
    assert isinstance(result, PagingDataclass)
    assert result.page == 1
    assert result.page_size == 10


async def test_search_sort_paginate_with_sorting(db: AsyncSession):
    result = await search_sort_paginate(
        db=db,
        stmt=select(MockModel),
        model_cls=MockModel,
        sort_by=["created_at"],
        descending=[True],
        page=1,
        page_size=10,
    )
    assert isinstance(result, PagingDataclass)
    assert result.page == 1
    assert result.page_size == 10
    assert result.items == []
    assert result.total == 0


async def test_search_sort_paginate_with_errors(db: AsyncSession):
    fake_attr = Mock(spec=InstrumentedAttribute)
    fake_attr.key = "invalid_attr"
    fake_attr.type = InstrumentedAttribute

    with pytest.raises(ValueError):
        await search_sort_paginate(
            db=db,
            stmt=select(MockModel),
            model_cls=MockModel,
            query_str="test",
            search_attr=fake_attr,
        )


async def test_search_sort_paginate_with_tsvector(db: AsyncSession):
    result = await search_sort_paginate(
        db=db,
        stmt=select(MockModel),
        model_cls=MockModel,
        query_str="test",
        search_attr=MockModel.attr_with_tsvector,
        page=1,
        page_size=10,
    )
    assert isinstance(result, PagingDataclass)
    assert result.page == 1
    assert result.page_size == 10
    assert result.items == []
    assert result.total == 0
