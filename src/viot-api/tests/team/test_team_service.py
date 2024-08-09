import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestException, PermissionDeniedException
from app.modules.auth.models import ViotUser
from app.modules.auth.schemas import RegisterRequest
from app.modules.team import schemas


async def test_get_all_teams(db: AsyncSession, user: ViotUser):
    from app.modules.team.service import create, get_all

    name = "Test Team"
    description = "A team for testing"

    # Create team
    request = schemas.TeamCreateRequest(name=name, description=description)
    await create(db=db, request=request, user_id=user.id)

    # Get all teams
    teams = await get_all(db=db, user_id=user.id)

    assert len(teams) == 1
    assert teams[0].name == name
    assert teams[0].description == description
    assert teams[0].default is True


async def test_exist_by_id(db: AsyncSession, user: ViotUser):
    from app.modules.team.service import create, exist_by_id

    name = "Test Team"
    description = "A team for testing"

    # Create team
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team = await create(db=db, request=request, user_id=user.id)

    # Check if team exist
    assert await exist_by_id(db=db, id=created_team.id) is True


async def test_create_team(db: AsyncSession, user: ViotUser):
    from app.modules.team.service import create

    name = "Test Team"
    description = "A team for testing"

    # Create team
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team = await create(db=db, request=request, user_id=user.id)

    assert created_team.name == name
    assert created_team.description == description
    assert created_team.default is True


async def test_create_team_no_default(db: AsyncSession, user: ViotUser):
    from app.modules.team.service import create

    name = "Test Team"
    description = "A team for testing"

    # Create team 1 (default)
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team_1 = await create(db=db, request=request, user_id=user.id)

    # Create team 2 (not default)
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team_2 = await create(db=db, request=request, user_id=user.id)

    assert created_team_1.default is True
    assert created_team_2.default is False


async def test_update_team(db: AsyncSession, user: ViotUser):
    from app.modules.team.service import create, update

    name = "Test Team"
    description = "A team for testing"

    # Create team
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team = await create(db=db, request=request, user_id=user.id)

    # Update team
    new_name = "Updated Team"
    new_description = "Updated description"
    request = schemas.TeamUpdateRequest(
        name=new_name, description=new_description, team_id=created_team.id
    )
    updated_team = await update(db=db, request=request, team_id=created_team.id, user_id=user.id)

    assert updated_team.name == new_name
    assert updated_team.description == new_description
    assert updated_team.default is True


async def test_update_team_error_not_owner(db: AsyncSession, user: ViotUser):
    from app.modules.auth import service as auth_service
    from app.modules.team.service import create, update

    # Create team owner
    request = RegisterRequest(
        email="user2@gmail.com",
        first_name="Test",
        last_name="User",
        password="!Test123",
    )
    owner = await auth_service.create(db=db, request=request)

    name = "Test Team"
    description = "A team for testing"

    # Create team
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team = await create(db=db, request=request, user_id=owner.id)

    # Update team
    new_name = "Updated Team"
    new_description = "Updated description"
    request = schemas.TeamUpdateRequest(
        name=new_name, description=new_description, team_id=created_team.id
    )

    with pytest.raises(PermissionDeniedException) as excinfo:
        await update(db=db, request=request, team_id=created_team.id, user_id=user.id)

    assert str(excinfo.value) == "User is not owner of this team"


async def test_delete_default_team_error(db: AsyncSession, user: ViotUser):
    from app.modules.team.service import create, delete

    name = "Test Team"
    description = "A team for testing"

    # Create team
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team = await create(db=db, request=request, user_id=user.id)

    # Delete team
    with pytest.raises(BadRequestException) as excinfo:
        await delete(db=db, team_id=created_team.id, user_id=user.id)

    assert str(excinfo.value) == "Cannot delete default team"


async def test_delete_team_success(db: AsyncSession, user: ViotUser):
    from app.modules.team.service import create, delete, get_or_raise

    name = "Test Team"
    description = "A team for testing"

    # Create team 1
    request = schemas.TeamCreateRequest(name=name, description=description)
    await create(db=db, request=request, user_id=user.id)

    # Create team 2
    request = schemas.TeamCreateRequest(name="team a", description=description)
    created_team_2 = await create(db=db, request=request, user_id=user.id)

    # Delete team
    await delete(db=db, team_id=created_team_2.id, user_id=user.id)

    # Check if team is deleted
    with pytest.raises(BadRequestException) as excinfo:
        await get_or_raise(db=db, id=created_team_2.id)

    assert str(excinfo.value) == "Team not found"


async def test_delete_team_error_not_owner(db: AsyncSession, user: ViotUser):
    from app.modules.auth import service as auth_service
    from app.modules.team.service import create, delete

    # Create team owner
    request = RegisterRequest(
        email="user2@gmail.com",
        first_name="Test",
        last_name="User",
        password="!Test123",
    )
    owner = await auth_service.create(db=db, request=request)

    name = "Test Team"
    description = "A team for testing"

    # Create team
    request = schemas.TeamCreateRequest(name=name, description=description)
    created_team = await create(db=db, request=request, user_id=owner.id)

    # Delete team
    with pytest.raises(PermissionDeniedException) as excinfo:
        await delete(db=db, team_id=created_team.id, user_id=user.id)

    assert str(excinfo.value) == "User is not owner of this team"
