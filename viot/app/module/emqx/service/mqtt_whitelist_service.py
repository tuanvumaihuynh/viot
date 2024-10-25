import logging
from typing import NamedTuple
from uuid import UUID

from ..config import emqx_settings

logger = logging.getLogger(__name__)


class MqttWhiteListAccount(NamedTuple):
    device_id: str
    access_token: str


class MqttWhitelistService:
    def __init__(self) -> None:
        self._whitelist: dict[UUID, str] = {}
        self._load(emqx_settings.MQTT_WHITELIST_FILE_PATH)

    def is_in_whitelist(self, device_id: UUID) -> bool:
        return device_id in self._whitelist

    def validate_mqtt_client(self, device_id: UUID, access_token: str) -> bool:
        return self._whitelist.get(device_id) == access_token

    def _load(self, path: str) -> None:
        logger.info(f"Loading MQTT whitelist from {path}")
        try:
            with open(path) as f:
                for line_number, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Split by ":" and check for exactly two parts
                    try:
                        device_id_str, access_token = line.split(":")
                    except ValueError:
                        logger.warning(
                            f"Malformed line {line_number}: {line}."
                            " Expected format 'deviceId:accessToken'"
                        )
                        continue

                    # Validate UUID
                    try:
                        device_id = UUID(device_id_str)
                    except ValueError:
                        logger.warning(
                            f"Invalid UUID format at line {line_number}: {device_id_str}"
                        )
                        continue

                    # Store the valid device_id and access_token
                    self._whitelist[device_id] = access_token

            logger.info(f"Loaded {len(self._whitelist)} accounts from {path}")

        except FileNotFoundError:
            logger.warning(f"MQTT whitelist file not found at {path}, skipping loading")
        except Exception as e:
            logger.error(f"Failed to load MQTT whitelist from {path}: {e}")
