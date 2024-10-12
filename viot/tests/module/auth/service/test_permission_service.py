from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.module.auth.exception.permission_exception import ResourceAccessDeniedException
from app.module.auth.service.permission_service import PermissionService


@pytest.fixture
def mock_user_team_role_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_permission_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def permission_service(
    mock_permission_repository: AsyncMock, mock_user_team_role_repository: AsyncMock
) -> PermissionService:
    return PermissionService(mock_permission_repository, mock_user_team_role_repository)


async def test_get_all_permissions(
    permission_service: PermissionService,
    mock_permission_repository: AsyncMock,
    mock_permission: Mock,
) -> None:
    # given
    mock_permission_repository.find_all.return_value = [mock_permission, mock_permission]
    # when
    result = await permission_service.get_all_permissions()

    # then
    assert len(result) == 2
    assert result[0].id == mock_permission.id
    assert result[0].title == mock_permission.title
    assert result[0].description == mock_permission.description


async def test_validate_user_access_team_resource(
    permission_service: PermissionService,
    mock_user_team_role_repository: AsyncMock,
) -> None:
    # given
    mock_user_team_role_repository.is_user_has_permission_in_team.return_value = True

    # when
    await permission_service.validate_user_access_team_resource(
        user_id=uuid4(),
        team_id=uuid4(),
        permission_scope="team:resource:read",
    )


async def test_validate_user_access_team_resource_when_user_does_not_have_permission(
    permission_service: PermissionService,
    mock_user_team_role_repository: AsyncMock,
) -> None:
    # given
    mock_user_team_role_repository.is_user_has_permission_in_team.return_value = False

    # when
    with pytest.raises(ResourceAccessDeniedException):
        await permission_service.validate_user_access_team_resource(
            user_id=uuid4(),
            team_id=uuid4(),
            permission_scope="team:resource:read",
        )
