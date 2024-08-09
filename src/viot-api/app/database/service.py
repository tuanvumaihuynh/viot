import logging
from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.database.types import TSVectorType
from app.models import Base

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Base)


@dataclass
class PagingDataclass(ABC, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


async def search_sort_paginate(
    *,
    db: AsyncSession,
    stmt: Select | None,
    model_cls: type[T],
    page: int = 1,
    page_size: int = 10,
    query_str: str | None = None,
    search_attr: InstrumentedAttribute | None = None,
    sort_by: list[str] | None = None,
    descending: list[bool] | None = None,
) -> PagingDataclass[T]:
    """Common functionality for searching, sorting, and pagination."""

    if stmt is None:
        stmt = select(model_cls)

    if query_str and isinstance(search_attr, InstrumentedAttribute):
        if not hasattr(model_cls, search_attr.key):
            logger.exception(f"Model {model_cls} has no attribute {search_attr.key}")
            raise ValueError(f"Model {model_cls} has no attribute {search_attr.key}")

        if isinstance(search_attr.type, TSVectorType):
            logger.debug("Using full-text search")
            stmt = stmt.filter(search_attr.match(query_str))
        else:
            logger.debug("Using normal search")
            stmt = stmt.filter(search_attr.ilike(f"%{query_str}%"))

    count_stmt = select(func.count()).select_from(stmt.subquery())

    if sort_by:
        for sort_field, desc in zip(sort_by or [], descending or [], strict=False):
            sort_attr = getattr(model_cls, sort_field)
            if desc:
                sort_attr = sort_attr.desc()
            stmt = stmt.order_by(sort_attr)

    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    total = (await db.execute(count_stmt)).scalar()
    items = (await db.execute(stmt)).scalars().all()

    return PagingDataclass(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
