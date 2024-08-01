import logging
import sys

import redis.asyncio as redis
from redis.exceptions import AuthenticationError, TimeoutError

from .config import db_settings

logger = logging.getLogger(__name__)


class RedisClient(redis.Redis):
    def __init__(self):
        super().__init__(
            host=db_settings.VIOT_REDIS_SERVER,
            port=db_settings.VIOT_REDIS_PORT,
            socket_timeout=5,
            decode_responses=True,
        )

    async def open(self):
        try:
            await self.ping()
        except TimeoutError:
            logger.error("Redis connection timeout")
            sys.exit(1)
        except AuthenticationError:
            logger.error("Redis authentication error")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            sys.exit(1)
        logger.info("Connected to Redis")


redis_client = RedisClient()
