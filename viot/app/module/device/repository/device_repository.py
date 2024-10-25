from uuid import UUID

from sqlalchemy import delete, exists, select, update

from app.database.repository import PageableRepository
from app.module.device.constants import DeviceStatus

from ..model.device import Device


class DeviceRepository(PageableRepository[Device, UUID]):
    async def find_by_device_id_and_team_id(self, device_id: UUID, team_id: UUID) -> Device | None:
        stmt = select(Device).where(Device.id == device_id, Device.team_id == team_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def delete_by_device_id_and_team_id(self, device_id: UUID, team_id: UUID) -> None:
        stmt = delete(Device).where(Device.id == device_id, Device.team_id == team_id)
        await self.session.execute(stmt)

    async def exists_by_id_and_team_id(self, device_id: UUID, team_id: UUID) -> bool:
        stmt = select(exists().where(Device.id == device_id, Device.team_id == team_id))
        return (await self.session.execute(stmt)).scalar() or False

    async def update_device_status(self, status: DeviceStatus) -> None:
        stmt = update(Device).values(status=status)
        await self.session.execute(stmt)
