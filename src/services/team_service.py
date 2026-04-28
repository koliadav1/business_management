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
            if current_user.team_id is not None:
                raise UserAlreadyInTeamError("You're already in team")

            existing_team = await uow.teams_repo.get_by_name(name)
            if existing_team:
                raise TeamAlreadyExistsError(
                    f"Team with name {name} already exists"
                )

            invite_code = None
            while True:
                invite_code = Team.generate_invite_code()
                existing = await uow.teams_repo.get_by_invite_code(invite_code)
                if not existing:
                    break

            team = Team(
                name=name, description=description, invite_code=invite_code
            )
            created_team = await uow.teams_repo.add(team)

            user = await uow._session.merge(current_user)
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

    async def get_team_members(
        self,
        uow: IUnitOfWork,
        current_user: User,
        role: UserRole | None = None,
    ) -> List[User]:
        """
        Получить всех участников команды с фильтром по роли.
        Только для участников команды
        """
        async with uow:
            if current_user.team_id is None:
                raise ForbiddenError("You're not in team")

            members = await uow.teams_repo.get_team_members(
                current_user.team_id, role
            )
        return members

    async def add_member(
        self,
        uow: IUnitOfWork,
        user_id: int,
        current_user: User,
        role: UserRole = UserRole.EMPLOYEE,
    ) -> User:
        """
        Добавить пользователя в команду.
        Только для admin команды.
        """
        async with uow:
            if current_user.role != UserRole or current_user.team_id is None:
                raise ForbiddenError("Only team admins can add members")

            team = await uow.teams_repo.get(current_user.team_id)
            if not team:
                raise TeamNotFoundError(
                    f"Team with id {current_user.team_id} not found"
                )

            user = await uow.users_repo.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found")

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
        Только для admin  команды
        """
        async with uow:
            if current_user.role != UserRole or current_user.team_id is None:
                raise ForbiddenError("Only team admins can remove members")

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
        user_id: int,
        new_role: UserRole,
        current_user: User,
    ) -> User:
        """
        Изменить роль участника команды.
        Только для admin команды
        """
        async with uow:
            if (
                current_user.role != UserRole.ADMIN
                or current_user.team_id is None
            ):
                raise ForbiddenError("Only team admins can change roles")

            if new_role not in [
                UserRole.MANAGER,
                UserRole.EMPLOYEE,
                UserRole.ADMIN,
            ]:
                raise InvalidRoleError(
                    f"Invalid role: {new_role}. "
                    "Must be MANAGER, EMPLOYEE or ADMIN"
                )

            user = await uow.users_repo.get(user_id)
            if not user:
                raise UserNotFoundError(f"User with id {user_id} not found")

            if user.team_id != current_user.team_id:
                raise UserNotInTeamError(
                    f"User {user_id} not in team {current_user.team_id}"
                )

            await uow.users_repo.update_user_role(user, new_role)

        return user

    async def delete_team(self, uow: IUnitOfWork, current_user: User) -> None:
        """
        Удаление команды.
        Только для admin команды
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admins can delete teams")
            await uow.teams_repo.delete(current_user.team_id)
            await uow.users_repo.update_user_role(current_user, UserRole.USER)

    async def get_all_teams(
        self, uow: IUnitOfWork, page: int, limit: int
    ) -> List[Team]:
        """Получить список всех команд"""
        async with uow:
            skip = (page - 1) * limit
            teams, total = await uow.teams_repo.get_all_paginated(skip, limit)
        return {
            "items": teams,
            "total": total,
            "page": page,
            "page_size": limit,
        }

    async def quit_team(self, uow: IUnitOfWork, current_user: User) -> None:
        """Покинуть команду"""
        async with uow:
            if current_user.role == UserRole.ADMIN:
                admins = await uow.teams_repo.get_team_members(
                    current_user.team_id, UserRole.ADMIN
                )
                if any(current_user != user for user in admins):
                    await uow.teams_repo.remove_member(current_user)
                else:
                    ForbiddenError(
                        "You must assign another admin to replace you"
                    )
            else:
                await uow.teams_repo.remove_member(current_user)

    async def join_by_team_code(
        self, uow: IUnitOfWork, current_user: User, inv_code: str
    ) -> Team:
        """Присоединится к команде по коду"""
        async with uow:
            if current_user.team_id is not None:
                raise UserAlreadyInTeamError("You're already in team")

            team = await uow.teams_repo.get_by_invite_code(inv_code)
            if not team:
                raise TeamNotFoundError(f"Team with code {inv_code} not found")

            user = await uow.session.merge(current_user)
            await uow.teams_repo.add_member(team, user, UserRole.EMPLOYEE)

        return team

    async def get_team_invite_code(
        self, uow: IUnitOfWork, current_user: User
    ) -> str:
        """
        Получить код команды для приглашения.
        Только для admin команды.
        """
        async with uow:
            if current_user.team_id is None:
                raise ForbiddenError("You're not in team")
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admin can get invite code")

            team = await uow.teams_repo.get(current_user.team_id)

            return team.invite_code
