from unittest.mock import AsyncMock, patch

from redis.exceptions import AuthenticationError, TimeoutError

from app.database.cache import RedisClient


async def test_open_success():
    client = RedisClient()
    # Mock the ping method to simulate a successful connection
    with patch.object(client, "ping", new_callable=AsyncMock) as mock_ping:
        await client.open()  # Should not raise an exception
        mock_ping.assert_awaited_once()


async def test_open_timeout_error():
    client = RedisClient()

    # Mock the ping method to raise a TimeoutError
    with patch.object(client, "ping", side_effect=TimeoutError):
        with patch("app.database.cache.logger.error") as mock_error:
            with patch("sys.exit") as mock_exit:
                await client.open()
                mock_error.assert_called_with("Redis connection timeout")
                mock_exit.assert_called_once_with(1)


async def test_open_authentication_error():
    client = RedisClient()

    # Mock the ping method to raise an AuthenticationError
    with patch.object(client, "ping", side_effect=AuthenticationError):
        with patch("app.database.cache.logger.error") as mock_error:
            with patch("sys.exit") as mock_exit:
                await client.open()
                mock_error.assert_called_with("Redis authentication error")
                mock_exit.assert_called_once_with(1)


async def test_open_general_error():
    client = RedisClient()

    # Mock the ping method to raise a general exception
    with patch.object(client, "ping", side_effect=Exception("General error")):
        with patch("app.database.cache.logger.error") as mock_error:
            with patch("sys.exit") as mock_exit:
                await client.open()
                mock_error.assert_called_with("Redis connection error: General error")
                mock_exit.assert_called_once_with(1)
