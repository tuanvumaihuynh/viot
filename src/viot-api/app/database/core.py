import logging
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from .config import db_settings

logger = logging.getLogger(__name__)


def create_engine():
    try:
        async_engine = create_async_engine(
            db_settings.SQLALCHEMY_DATABASE_URI,
            pool_pre_ping=True,
            pool_size=16,
            pool_recycle=60 * 20,  # 20 minutes
            echo=db_settings.IS_DEV_ENV,
        )
    except Exception as e:
        logger.error(f"Error while creating async engine: {e}")
        sys.exit(1)
    return async_engine


async_engine = create_engine()


AsyncSessionFactory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=async_engine,
    class_=AsyncSession,
)
