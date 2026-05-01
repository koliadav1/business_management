import pytest

from src.core.exceptions import (
    ForbiddenError,
    InvalidRoleError,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    UserAlreadyInTeamError,
    UserNotFoundError,
    UserNotInTeamError,
)
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.teams import Team
from src.models.users import User, UserRole
from src.services.team_service import TeamService


class TestTeamService:

    @pytest.mark.asyncio
    async def test_create_team_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        regular_user: User,
        mocker,
    ):
        data = {"name": "New team", "description": "Test"}
        mock_uow.teams_repo.get_by_name.return_value = None
        mock_uow.teams_repo.get_by_invite_code.return_value = None

        expected_team = mocker.MagicMock(spec=Team)
        expected_team.id = 1
        expected_team.name = data["name"]
        expected_team.description = data["description"]
        expected_team.invite_code = "ABCD1234"

        mock_uow.teams_repo.add.return_value = expected_team

        result = await team_service.create_team(
            mock_uow, data["name"], data["description"], regular_user
        )

        assert result == expected_team
        mock_uow.teams_repo.get_by_name.assert_called_once_with(data["name"])
        mock_uow.teams_repo.add.assert_called_once()
        mock_uow.teams_repo.add_member.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_team_already_in_team(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        with pytest.raises(UserAlreadyInTeamError):
            await team_service.create_team(
                mock_uow, "New team", None, admin_user
            )

    @pytest.mark.asyncio
    async def test_create_team_name_exists(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        regular_user: User,
        mocker,
    ):
        existing_team = mocker.MagicMock(spec=Team)
        mock_uow.teams_repo.get_by_name.return_value = existing_team

        with pytest.raises(TeamAlreadyExistsError):
            await team_service.create_team(
                mock_uow, "New team", None, regular_user
            )

    @pytest.mark.asyncio
    async def test_get_team_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        mocker,
    ):
        expected_team = mocker.MagicMock(spec=Team)
        expected_team.id = 1
        mock_uow.teams_repo.get.return_value = expected_team

        result = await team_service.get_team(mock_uow, 1)

        assert result == expected_team
        mock_uow.teams_repo.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_team_not_found(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        mocker,
    ):
        mock_uow.teams_repo.get.return_value = None

        with pytest.raises(TeamNotFoundError):
            await team_service.get_team(mock_uow, 9999)

    @pytest.mark.asyncio
    async def test_get_team_members_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        expected_members = [mocker.MagicMock(spec=User) for _ in range(3)]

        mock_uow.teams_repo.get_team_members.return_value = expected_members

        result = await team_service.get_team_members(mock_uow, employee_user)

        assert result == expected_members
        mock_uow.teams_repo.get_team_members.assert_called_once_with(
            employee_user.team_id, None
        )

    @pytest.mark.asyncio
    async def test_get_team_members_with_role(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        expected_members = [mocker.MagicMock(spec=User)]

        mock_uow.teams_repo.get_team_members.return_value = expected_members

        result = await team_service.get_team_members(
            mock_uow, employee_user, UserRole.ADMIN
        )

        assert result == expected_members
        mock_uow.teams_repo.get_team_members.assert_called_once_with(
            employee_user.team_id, UserRole.ADMIN
        )

    @pytest.mark.asyncio
    async def test_get_team_members_not_in_team(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        regular_user: User,
    ):
        with pytest.raises(ForbiddenError, match="You're not in team"):
            await team_service.get_team_members(mock_uow, regular_user)

    @pytest.mark.asyncio
    async def test_add_member_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        new_user = mocker.MagicMock(spec=User)
        new_user.id = 5
        new_user.team_id = None

        team = mocker.MagicMock(spec=Team)
        team.id = admin_user.team_id

        mock_uow.teams_repo.get.return_value = team
        mock_uow.users_repo.get.return_value = new_user
        mock_uow.teams_repo.add_member.return_value = None

        result = await team_service.add_member(mock_uow, 5, admin_user)

        assert result == new_user
        mock_uow.teams_repo.add_member.assert_called_once_with(
            team, new_user, UserRole.EMPLOYEE
        )

    @pytest.mark.asyncio
    async def test_add_member_not_admin(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        employee_user: User,
    ):
        with pytest.raises(
            ForbiddenError, match="Only team admins can add members"
        ):
            await team_service.add_member(mock_uow, 5, employee_user)

    @pytest.mark.asyncio
    async def test_add_member_user_not_found(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        team = mocker.MagicMock(scep=Team)
        mock_uow.teams_repo.get.return_value = team
        mock_uow.users_repo.get.return_value = None

        with pytest.raises(UserNotFoundError):
            await team_service.add_member(mock_uow, 999, admin_user)

    @pytest.mark.asyncio
    async def test_add_member_already_in_team(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        existing_user = mocker.MagicMock(spec=User)
        existing_user.id = 5
        existing_user.team_id = 20

        team = mocker.MagicMock(spec=Team)
        mock_uow.teams_repo.get.return_value = team
        mock_uow.users_repo.get.return_value = existing_user

        with pytest.raises(UserAlreadyInTeamError):
            await team_service.add_member(mock_uow, 5, admin_user)

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        user_to_remove = mocker.MagicMock(spec=User)
        user_to_remove.id = 5
        user_to_remove.team_id = admin_user.team_id
        user_to_remove.role = UserRole.EMPLOYEE

        mock_uow.users_repo.get.return_value = user_to_remove

        await team_service.remove_member(mock_uow, 5, admin_user)
        mock_uow.teams_repo.remove_member.assert_called_once_with(
            user_to_remove
        )

    @pytest.mark.asyncio
    async def test_remove_member_admin_remove_forbidden(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        user_to_remove = mocker.MagicMock(spec=User)
        user_to_remove.id = 5
        user_to_remove.team_id = admin_user.team_id
        user_to_remove.role = UserRole.ADMIN

        mock_uow.users_repo.get.return_value = user_to_remove

        with pytest.raises(
            ForbiddenError, match="Can't remove admin from team"
        ):
            await team_service.remove_member(mock_uow, 5, admin_user)

    @pytest.mark.asyncio
    async def test_remove_member_not_in_team(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        user_to_remove = mocker.MagicMock(spec=User)
        user_to_remove.id = 5
        user_to_remove.team_id = 999

        mock_uow.users_repo.get.return_value = user_to_remove

        with pytest.raises(UserNotInTeamError):
            await team_service.remove_member(mock_uow, 5, admin_user)

    @pytest.mark.asyncio
    async def test_update_member_role_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        user_to_update = mocker.MagicMock(spec=User)
        user_to_update.id = 5
        user_to_update.team_id = admin_user.team_id
        user_to_update.role = UserRole.EMPLOYEE

        mock_uow.users_repo.get.return_value = user_to_update

        result = await team_service.update_member_role(
            mock_uow, 5, UserRole.MANAGER, admin_user
        )

        assert result == user_to_update
        mock_uow.users_repo.update_user_role.assert_called_once_with(
            user_to_update, UserRole.MANAGER
        )

    @pytest.mark.asyncio
    async def test_update_member_role_invalid(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        with pytest.raises(InvalidRoleError):
            await team_service.update_member_role(
                mock_uow, 5, UserRole.USER, admin_user
            )

    @pytest.mark.asyncio
    async def test_delete_team_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        await team_service.delete_team(mock_uow, admin_user)
        mock_uow.teams_repo.delete.assert_called_once_with(admin_user.team_id)
        mock_uow.teams_repo.remove_all_members.assert_called_once_with(
            admin_user.team_id
        )

    @pytest.mark.asyncio
    async def test_delete_team_not_admin(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        employee_user: User,
    ):
        with pytest.raises(
            ForbiddenError, match="Only admins can delete teams"
        ):
            await team_service.delete_team(mock_uow, employee_user)

    @pytest.mark.asyncio
    async def test_get_all_teams_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        mocker,
    ):
        page, limit = 1, 20
        expected_teams = [mocker.MagicMock(spec=Team) for _ in range(5)]
        total = 5

        mock_uow.teams_repo.get_all_paginated.return_value = (
            expected_teams,
            total,
        )

        result = await team_service.get_all_teams(mock_uow, page, limit)

        assert result["items"] == expected_teams
        assert result["total"] == total
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.teams_repo.get_all_paginated.assert_called_once_with(0, limit)

    @pytest.mark.asyncio
    async def test_quit_team_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        employee_user: User,
    ):
        mock_uow.teams_repo.remove_member.return_value = None
        await team_service.quit_team(mock_uow, employee_user)
        mock_uow.teams_repo.remove_member.assert_called_once_with(
            employee_user
        )

    @pytest.mark.asyncio
    async def test_quit_team_as_admin(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Team admin can only delete team, but not leave",
        ):
            await team_service.quit_team(mock_uow, admin_user)

    @pytest.mark.asyncio
    async def test_join_by_code_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        regular_user: User,
        mocker,
    ):
        team = mocker.MagicMock(spec=Team)
        team.invite_code = "ADCD1234"

        mock_uow.teams_repo.get_by_invite_code.return_value = team

        result = await team_service.join_by_team_code(
            mock_uow, regular_user, "ADCD1234"
        )

        assert result == team
        mock_uow.teams_repo.add_member.assert_called_once_with(
            team, regular_user, UserRole.EMPLOYEE
        )

    @pytest.mark.asyncio
    async def test_join_by_code_already_in_team(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        employee_user: User,
    ):
        with pytest.raises(UserAlreadyInTeamError):
            await team_service.join_by_team_code(
                mock_uow, employee_user, "ADCD1234"
            )

    @pytest.mark.asyncio
    async def test_join_by_code_not_found(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        regular_user: User,
    ):
        mock_uow.teams_repo.get_by_invite_code.return_value = None

        with pytest.raises(TeamNotFoundError):
            await team_service.join_by_team_code(
                mock_uow, regular_user, "ADCD1234"
            )

    @pytest.mark.asyncio
    async def test_get_team_invite_code_success(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        team = mocker.MagicMock(spec=Team)
        team.invite_code = "ADCD1234"

        mock_uow.teams_repo.get.return_value = team

        result = await team_service.get_team_invite_code(mock_uow, admin_user)

        assert result == "ADCD1234"
        mock_uow.teams_repo.get.assert_called_once_with(admin_user.team_id)

    @pytest.mark.asyncio
    async def test_get_team_invite_code_not_admin(
        self,
        team_service: TeamService,
        mock_uow: IUnitOfWork,
        regular_user: User,
    ):
        with pytest.raises(
            ForbiddenError, match="Only admin can get invite code"
        ):
            await team_service.get_team_invite_code(mock_uow, regular_user)
