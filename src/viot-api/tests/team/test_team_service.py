from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.team import schemas


async def test_create_team(db: AsyncSession):
    from app.modules.team.service import create

    name = "Test Team"
    description = "A team for testing"

    request = schemas.TeamCreateRequest(name=name, description=description)
    user_id = uuid4()

    created_team = await create(db=db, request=request, user_id=user_id)

    assert created_team.name == name
    assert created_team.description == description
    assert created_team.default is True


async def test_update_team(db: AsyncSession):
    from app.modules.team.service import create, update

    name = "Test Team"
    description = "A team for testing"

    request = schemas.TeamCreateRequest(name=name, description=description)

    created_team = await create(db=db, request=request, user_id=uuid4())

    update_request = schemas.TeamUpdateRequest(
        name="Updated Team", description="Updated description"
    )
    updated_team = await update(db=db, id=created_team.id, request=update_request)
