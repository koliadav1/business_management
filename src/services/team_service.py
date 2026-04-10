from typing import List

from src.core.exceptions import (
    ForbiddenError,
    InvalidrRoleError,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    UserAlreadyInTeamError,
    UserNotFoundError,
    UserNotInTeamErorr,
)
from src.models.teams import Team
from src.models.users import User, UserRole
from src.core.interfaces.unit_of_work import IUnitOfWork


class TeamService:
    async def create_team(
        self,
        uow: IUnitOfWork,
        name: str,
        description: str | None,
        current_user: User,
    ) -> Team:
        """
        Создание команды.
        Только для роли admin
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admins can create a team")

            existing_team = await uow.teams_repo.get_by_name(name)
            if existing_team:
                raise TeamAlreadyExistsError(
                    f"Team with name {name} already exists"
                )

            team = Team(name=name, description=description)
            created_team = await uow.teams_repo.add(team)

            await uow.teams_repo.add_member(
                created_team, current_user, UserRole.ADMIN
            )
        return created_team

    async def get_team(self, uow: IUnitOfWork, team_id: int) -> Team:
        """
        Получить информацию о команде
        """
        async with uow:
            team = await uow.teams_repo.get(team_id)
            if not team:
                raise TeamNotFoundError(
                    f"Team with id {team_id} does not exist"
                )
        return team

    async def get_team_with_members(
        self, uow: IUnitOfWork, team_id: int, current_user: User
    ) -> Team:
        """
        Получение информации о команде и ее участниках.
        Только для участников команды
        """
        async with uow:
            team = await uow.teams_repo.get_team_with_members(team_id)
            if not team:
                raise TeamNotFoundError(
                    f"Team with id {team_id} does not exist"
                )

            if not await self._can_view_team_members(
                uow, team_id, current_user
            ):
                raise ForbiddenError("You can't view team members")

        return team

    async def get_my_team(
        self, uow: IUnitOfWork, current_user: User
    ) -> Team | None:
        """Получить команду текущего пользователя"""
        async with uow:
            return await uow.teams_repo.get_user_team(current_user.id)

    async def get_team_members(
        self,
        uow: IUnitOfWork,
        team_id: int,
        current_user: User,
        role: UserRole | None = None,
    ) -> List[User]:
        """
        Получить участников команды.
        Только для участников команды
        """
        async with uow:
            team = await uow.teams_repo.get(team_id)
            if not team:
                raise TeamNotFoundError(f"Team with id {team_id} not found")

            if not await self._can_view_team_members(
                uow, team_id, current_user
            ):
                raise ForbiddenError("You can't view team members")

            members = await uow.teams_repo.get_team_members(team_id, role)
        return members

    async def add_member(
        self,
        uow: IUnitOfWork,
        team_id: int,
        user_id: int,
        current_user: User,
        role: UserRole = UserRole.EMPLOYEE,
    ) -> User:
        """
        Добавить пользователя в команду.
        Только для admin и manager команды.
        """
        async with uow:
            if not await self._can_manage_team(uow, team_id, current_user):
                raise ForbiddenError(
                    "Only team admins and managers can add members"
                )

            team = await uow.teams_repo.get(team_id)
            if not team:
                raise TeamNotFoundError(f"Team with id {team_id} not found")

            user = await uow.users_repo.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found")

            if user.role == UserRole.ADMIN:
                raise ForbiddenError("Can't add admin to a team")

            if user.team_id is not None:
                raise UserAlreadyInTeamError(
                    f"User with id {user_id} is already in a team"
                )

            await uow.teams_repo.add_member(team, user, role)

        return user

    async def remove_member(
        self, uow: IUnitOfWork, team_id: int, user_id: int, current_user: User
    ) -> None:
        """
        Удаление пользователя из команды.
        Только для admin и manager команды
        """
        async with uow:
            if not await self._can_manage_team(uow, team_id, current_user):
                raise ForbiddenError(
                    "Only team admins and managers can remove members"
                )

            team = await uow.teams_repo.get(team_id)
            if not team:
                raise TeamNotFoundError(f"Team with id {team_id} not found")

            user = await uow.users_repo.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found")

            if user.team_id != team_id:
                raise UserNotInTeamErorr(
                    f"User {user_id} not in team {team_id}"
                )

            if user.role == UserRole.ADMIN:
                raise ForbiddenError("Can't remove admin from team")

            await uow.teams_repo.remove_member(team, user)

    async def update_member_role(
        self,
        uow: IUnitOfWork,
        team_id: int,
        user_id: int,
        new_role: UserRole,
        current_user: User,
    ) -> User:
        """
        Изменить роль участника команды.
        Только для admin и manager команды
        """
        async with uow:
            if not await self._can_manage_team(uow, team_id, current_user):
                raise ForbiddenError(
                    "Only team admins and managers can change roles"
                )

            if new_role not in [UserRole.MANAGER, UserRole.EMPLOYEE]:
                raise InvalidrRoleError(
                    f"Invalid role: {new_role}. Must be MANAGER or EMPLOYEE"
                )

            team = await uow.teams_repo.get(team_id)
            if not team:
                raise TeamNotFoundError(f"Team with id {team_id} not found")

            user = await uow.users_repo.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found")

            if user.team_id != team_id:
                raise UserNotInTeamErorr(
                    f"User {user_id} not in team {team_id}"
                )

            await uow.teams_repo.update_member_role(team, user, new_role)

        return user

    async def delete_team(
        self, uow: IUnitOfWork, team_id: int, current_user: User
    ) -> None:
        """
        Удаление команды.
        Только для admin команды
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admins can delete teams")

            team = await uow.teams_repo.get(team_id)
            if not team:
                raise TeamNotFoundError(f"Team with id {team_id} not found")

            await uow.teams_repo.delete(team_id)

    async def get_all_teams(self, uow: IUnitOfWork) -> List[Team]:
        """Получить список всех команд"""
        async with uow:
            return await uow.teams_repo.get_all()

    async def _can_view_team_members(
        self, uow: IUnitOfWork, team_id: int, current_user: User
    ):
        if await uow.teams_repo.is_member(team_id, current_user.id):
            return True

        return False

    async def _can_manage_team(
        self, uow: IUnitOfWork, team_id: int, current_user: User
    ):
        if await uow.teams_repo.is_member(
            team_id, current_user.id, UserRole.MANAGER
        ):
            return True

        if await uow.teams_repo.is_member(
            team_id, current_user.id, UserRole.ADMIN
        ):
            return True

        return False
