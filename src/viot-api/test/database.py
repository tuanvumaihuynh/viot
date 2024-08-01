from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.database.config import db_settings

# ref: https://stackoverflow.com/questions/75252097/fastapi-testing-runtimeerror-task-attached-to-a-different-loop
async_engine = async_engine = create_async_engine(
    db_settings.SQLALCHEMY_DATABASE_URI,
    poolclass=NullPool,
)
