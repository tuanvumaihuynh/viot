from unittest import mock
from uuid import UUID

import pytest

from app.module.emqx.service.mqtt_whitelist_service import MqttWhitelistService


@pytest.fixture
def mock_valid_whitelist_content() -> str:
    return (
        "123e4567-e89b-12d3-a456-426614174000:token123\n"
        + "123e4567-e89b-12d3-a456-426614174001:token456\n"
    )


@pytest.fixture
def mock_malformed_whitelist_content() -> str:
    return "123e4567-e89b-12d3-a456-426614174000:token123\n" + "invalid_line_without_colon\n"


@pytest.fixture
def mock_invalid_uuid_content() -> str:
    return "invalid-uuid-format:token123\n" + "123e4567-e89b-12d3-a456-426614174001:token456\n"


def test_load_valid_whitelist(mock_valid_whitelist_content: str) -> None:
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_valid_whitelist_content)):
        service = MqttWhitelistService()

        assert len(service._whitelist) == 2  # type: ignore
        assert (
            service._whitelist[UUID("123e4567-e89b-12d3-a456-426614174000")]  # type: ignore
            == "token123"
        )
        assert (
            service._whitelist[UUID("123e4567-e89b-12d3-a456-426614174001")]  # type: ignore
            == "token456"
        )


def test_load_malformed_line(
    mock_malformed_whitelist_content: str, caplog: pytest.LogCaptureFixture
) -> None:
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_malformed_whitelist_content)):
        with caplog.at_level("WARNING"):
            service = MqttWhitelistService()

            assert len(service._whitelist) == 1  # type: ignore
            assert UUID("123e4567-e89b-12d3-a456-426614174000") in service._whitelist  # type: ignore
            # Check that a warning about the malformed line was logged
            assert any("Malformed line" in record.message for record in caplog.records)


def test_load_invalid_uuid(
    mock_invalid_uuid_content: str, caplog: pytest.LogCaptureFixture
) -> None:
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_invalid_uuid_content)):
        with caplog.at_level("WARNING"):
            service = MqttWhitelistService()

            assert len(service._whitelist) == 1  # type: ignore
            assert UUID("123e4567-e89b-12d3-a456-426614174001") in service._whitelist  # type: ignore

            # Check that a warning about the invalid UUID was logged
            assert any("Invalid UUID format" in record.message for record in caplog.records)


def test_file_not_found() -> None:
    with mock.patch("builtins.open", side_effect=FileNotFoundError):
        service = MqttWhitelistService()

        assert len(service._whitelist) == 0  # type: ignore


def test_load_empty_line() -> None:
    mock_content = "123e4567-e89b-12d3-a456-426614174000:token123\n\n"
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_content)):
        service = MqttWhitelistService()
        assert len(service._whitelist) == 1  # type: ignore
        assert UUID("123e4567-e89b-12d3-a456-426614174000") in service._whitelist  # type: ignore


def test_load_unknown_exception(caplog: pytest.LogCaptureFixture) -> None:
    with mock.patch("builtins.open", mock.Mock(side_effect=Exception("Unexpected Error"))):
        MqttWhitelistService()
        assert "Failed to load MQTT whitelist" in caplog.text
        assert "Unexpected Error" in caplog.text


def test_is_in_whitelist(mock_valid_whitelist_content: str) -> None:
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_valid_whitelist_content)):
        service = MqttWhitelistService()

        assert service.is_in_whitelist(UUID("123e4567-e89b-12d3-a456-426614174000")) is True
        assert service.is_in_whitelist(UUID("123e4567-e89b-12d3-a456-426614174001")) is True
        assert service.is_in_whitelist(UUID("123e4567-e89b-12d3-a456-426614174999")) is False


def test_validate_mqtt_client(mock_valid_whitelist_content: str) -> None:
    with mock.patch("builtins.open", mock.mock_open(read_data=mock_valid_whitelist_content)):
        service = MqttWhitelistService()

        # Valid check
        assert (
            service.validate_mqtt_client(UUID("123e4567-e89b-12d3-a456-426614174000"), "token123")
            is True
        )
        # Invalid token check
        assert (
            service.validate_mqtt_client(UUID("123e4567-e89b-12d3-a456-426614174000"), "wrongtoken")
            is False
        )
        # Non-existent device_id
        assert (
            service.validate_mqtt_client(UUID("123e4567-e89b-12d3-a456-426614174999"), "token999")
            is False
        )
