from uuid import UUID

from sqlalchemy import exists, select

from app.database.repository import CrudRepository
from app.module.auth.model.role import Role


class RoleRepository(CrudRepository[Role, int]):
    async def is_role_name_exists_in_team(self, *, team_id: UUID, role_name: str) -> bool:
        stmt = select(exists().where(Role.name == role_name).where(Role.team_id == team_id))
        result = await self.session.execute(stmt)
        return bool(result.scalar())
