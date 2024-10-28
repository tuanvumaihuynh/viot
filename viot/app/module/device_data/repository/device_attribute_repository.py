from collections.abc import Sequence
from typing import NamedTuple
from uuid import UUID

from sqlalchemy import delete, select

from app.database.repository import AsyncSqlalchemyRepository

from ..constants import DeviceAttributeScope
from ..model.device_attribute import DeviceAttribute


class KeyWithScope(NamedTuple):
    key: str
    scope: DeviceAttributeScope


class DeviceAttributeRepository(AsyncSqlalchemyRepository):
    async def find_all_key_with_scope_by_device_id(self, device_id: UUID) -> list[KeyWithScope]:
        stmt = select(DeviceAttribute.key, DeviceAttribute.scope).where(
            DeviceAttribute.device_id == device_id
        )
        results = (await self.session.execute(stmt)).fetchall()
        return [KeyWithScope(key=key, scope=scope) for key, scope in results]

    async def find_all_key_by_scope_and_device_id(
        self, device_id: UUID, scope: DeviceAttributeScope
    ) -> Sequence[str]:
        stmt = (
            select(DeviceAttribute.key)
            .where(DeviceAttribute.device_id == device_id)
            .where(DeviceAttribute.scope == scope)
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def find_all_by_device_id_keys_and_scope(
        self, device_id: UUID, keys: set[str], scope: DeviceAttributeScope
    ) -> Sequence[DeviceAttribute]:
        stmt = (
            select(DeviceAttribute)
            .where(DeviceAttribute.device_id == device_id)
            .where(DeviceAttribute.scope == scope)
            .where(DeviceAttribute.key.in_(keys))
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def delete_by_keys(self, device_id: UUID, keys: set[str]) -> None:
        stmt = (
            delete(DeviceAttribute)
            .where(DeviceAttribute.device_id == device_id)
            .where(DeviceAttribute.key.in_(keys))
        )
        await self.session.execute(stmt)
