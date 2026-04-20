from typing import List

from src.core.exceptions import (
    ForbiddenError,
    InvalidRoleError,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    UserAlreadyInTeamError,
    UserNotFoundError,
    UserNotInTeamError,
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
            if current_user.team_id is not None:
                raise UserAlreadyInTeamError("You're already in team")

            existing_team = await uow.teams_repo.get_by_name(name)
            if existing_team:
                raise TeamAlreadyExistsError(
                    f"Team with name {name} already exists"
                )

            team = Team(name=name, description=description)
            created_team = await uow.teams_repo.add(team)

            user = await uow.users_repo.get(current_user.id)
            await uow.teams_repo.add_member(created_team, user, UserRole.ADMIN)
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

            if current_user.team_id != team_id:
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
            if (
                current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]
                or current_user.team_id != team_id
            ):
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
        self, uow: IUnitOfWork, user_id: int, current_user: User
    ) -> None:
        """
        Удаление пользователя из команды.
        Только для admin и manager команды
        """
        async with uow:
            if current_user.team_id is None:
                raise ForbiddenError("You're not in team")
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only team admins and managers can remove members"
                )

            user = await uow.users_repo.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found")

            if user.team_id != current_user.team_id:
                raise UserNotInTeamError(
                    f"User {user_id} not in team {current_user.team_id}"
                )

            if user.role == UserRole.ADMIN:
                raise ForbiddenError("Can't remove admin from team")

            await uow.teams_repo.remove_member(user)

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
            if (
                current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]
                or current_user.team_id != team_id
            ):
                raise ForbiddenError(
                    "Only team admins and managers can change roles"
                )

            if new_role not in [UserRole.MANAGER, UserRole.EMPLOYEE]:
                raise InvalidRoleError(
                    f"Invalid role: {new_role}. Must be MANAGER or EMPLOYEE"
                )

            team = await uow.teams_repo.get(team_id)
            if not team:
                raise TeamNotFoundError(f"Team with id {team_id} not found")

            user = await uow.users_repo.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found")

            if user.team_id != team_id:
                raise UserNotInTeamError(
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
