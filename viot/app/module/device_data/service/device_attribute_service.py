from uuid import UUID

from injector import inject

from ..constants import DeviceAttributeScope
from ..dto.device_attribute_dto import DeviceAttributeDto, ScopeKeysDto
from ..repository.device_attribute_repository import DeviceAttributeRepository


class DeviceAttributeService:
    @inject
    def __init__(
        self,
        device_attribute_repository: DeviceAttributeRepository,
    ) -> None:
        self._device_attribute_repository = device_attribute_repository

    async def get_all_keys_by_device_id(self, *, device_id: UUID) -> ScopeKeysDto:
        data = await self._device_attribute_repository.find_all_key_with_scope_by_device_id(
            device_id=device_id
        )
        return ScopeKeysDto.from_key_with_scopes(data)

    async def get_all_key_by_scope_and_device_id(
        self, *, device_id: UUID, scope: DeviceAttributeScope
    ) -> set[str]:
        data = await self._device_attribute_repository.find_all_key_by_scope_and_device_id(
            device_id=device_id, scope=scope
        )
        return set(data)

    async def get_all_by_device_id(
        self, *, device_id: UUID, keys: set[str], scope: DeviceAttributeScope
    ) -> list[DeviceAttributeDto]:
        data = await self._device_attribute_repository.find_all_by_device_id_keys_and_scope(
            device_id=device_id, keys=keys, scope=scope
        )
        return [DeviceAttributeDto.from_model(d) for d in data]
