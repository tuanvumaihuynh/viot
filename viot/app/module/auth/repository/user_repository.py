from datetime import datetime
from uuid import UUID

import msgspec
from sqlalchemy import delete, exists, func, select, update

from app.database.repository import CrudRepository, Page, Pageable
from app.module.team.model.user_team import UserTeam

from ..model.user import User


class TeamMember(msgspec.Struct, frozen=True):
    user: User
    role: str
    joined_at: datetime


class UserRepository(CrudRepository[User, UUID]):
    async def find_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return (await self.session.execute(stmt)).scalar()

    async def find_id_by_email(self, email: str) -> UUID | None:
        stmt = select(User.id).where(User.email == email)
        return (await self.session.execute(stmt)).scalar()

    async def find_paging_member_by_team_id(
        self, team_id: UUID, pageable: Pageable
    ) -> Page[TeamMember]:
        stmt = (
            select(User, UserTeam.role, UserTeam.joined_at)
            .join(UserTeam)
            .where(UserTeam.team_id == team_id)
        )
        query = pageable.apply(stmt, self._model)
        count_query = select(func.count()).select_from(
            pageable.apply(stmt, self._model).order_by(None).limit(None).subquery()
        )

        items = (await self.session.execute(query)).fetchall()
        total_items = (await self.session.execute(count_query)).scalar_one()

        return Page(
            items=[
                TeamMember(user=user, role=role, joined_at=joined_at)
                for user, role, joined_at in items
            ],
            total_items=total_items,
            page=pageable.page,
            page_size=pageable.page_size,
        )

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(exists().where(User.email == email))
        result = await self.session.execute(stmt)
        return result.scalar() or False

    async def update_password(self, user_id: UUID, hashed_password: bytes) -> None:
        stmt = update(User).where(User.id == user_id).values(password=hashed_password)
        await self.session.execute(stmt)

    async def update_email_verified_at(self, user_id: UUID, email_verified_at: datetime) -> None:
        stmt = update(User).where(User.id == user_id).values(email_verified_at=email_verified_at)
        await self.session.execute(stmt)

    async def delete_by_id(self, id: UUID) -> None:
        stmt = delete(User).where(User.id == id)
        await self.session.execute(stmt)
