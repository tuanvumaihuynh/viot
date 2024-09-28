from unittest.mock import AsyncMock, Mock

import pytest

from app.module.auth.repository.password_reset_repository import PasswordResetRepository
from app.module.auth.repository.permission_repository import PermissionRepository
from app.module.auth.repository.refresh_token_repository import RefreshTokenRepository
from app.module.auth.repository.role_permission_repository import RolePermissionRepository
from app.module.auth.repository.role_repository import RoleRepository
from app.module.auth.repository.user_repository import UserRepository
from app.module.auth.repository.user_team_role_repository import UserTeamRoleRepository
from app.module.auth.service.auth_service import AuthService
from app.module.auth.service.password_reset_service import PasswordResetService
from app.module.auth.service.team_role_service import TeamRoleService
from app.module.auth.service.token_service import TokenService
from app.module.auth.service.user_service import UserService
from app.module.email.service import IEmailService
from app.module.team.repository.team_invitation_repository import (
    TeamInvitationRepository,
)
from app.module.team.repository.team_repository import TeamRepository
from app.module.team.service.team_invitation_service import TeamInvitationService
from app.module.team.service.team_service import TeamService


@pytest.fixture
def mock_email_service() -> Mock:
    return Mock(spec=IEmailService)


@pytest.fixture
def auth_service(
    mock_email_service: IEmailService,
    mock_user_repository: UserRepository,
    mock_refresh_token_repository: RefreshTokenRepository,
    mock_password_reset_repository: PasswordResetRepository,
) -> AuthService:
    return AuthService(
        email_service=mock_email_service,
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_token_repository,
        password_reset_repository=mock_password_reset_repository,
    )


@pytest.fixture
def password_reset_service(
    mock_email_service: IEmailService,
    mock_user_repository: UserRepository,
    mock_password_reset_repository: PasswordResetRepository,
) -> PasswordResetService:
    return PasswordResetService(
        email_service=mock_email_service,
        user_repository=mock_user_repository,
        password_reset_repository=mock_password_reset_repository,
    )


@pytest.fixture
def token_service(
    mock_user_repository: UserRepository, mock_refresh_token_repository: RefreshTokenRepository
) -> TokenService:
    return TokenService(
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_token_repository,
    )


@pytest.fixture
def user_service(mock_user_repository: UserRepository) -> UserService:
    return UserService(user_repository=mock_user_repository)


@pytest.fixture
def team_role_service(
    mock_role_repository: RoleRepository,
    mock_role_permission_repository: RolePermissionRepository,
    mock_permission_repository: PermissionRepository,
) -> TeamRoleService:
    return TeamRoleService(
        role_repository=mock_role_repository,
        role_permission_repository=mock_role_permission_repository,
        permission_repository=mock_permission_repository,
    )


@pytest.fixture
def team_service(
    mock_team_repository: TeamRepository,
    mock_permission_repository: PermissionRepository,
    mock_user_team_role_repository: UserTeamRoleRepository,
) -> TeamService:
    return TeamService(
        team_repository=mock_team_repository,
        team_role_service=AsyncMock(),
        permission_repository=mock_permission_repository,
        user_team_role_repository=mock_user_team_role_repository,
    )


@pytest.fixture
def team_invitation_service(
    mock_email_service: IEmailService,
    mock_team_invitation_repository: TeamInvitationRepository,
    mock_user_repository: UserRepository,
    mock_team_repository: TeamRepository,
    mock_user_team_role_repository: UserTeamRoleRepository,
    mock_role_repository: RoleRepository,
) -> TeamInvitationService:
    return TeamInvitationService(
        email_service=mock_email_service,
        team_invitation_repository=mock_team_invitation_repository,
        user_repository=mock_user_repository,
        team_repository=mock_team_repository,
        user_team_role_repository=mock_user_team_role_repository,
        role_repository=mock_role_repository,
    )
