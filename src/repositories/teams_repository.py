from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.users import User, UserRole
from src.core.interfaces.repositories.teams_repository import ITeamsRepository
from src.models.teams import Team
from .base_repository import SQLRepository


class TeamsRepository(SQLRepository[Team], ITeamsRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Team)

    async def get_by_name(self, name: str) -> Team | None:
        """Получить команду по названию"""
        result = await self._session.execute(
            select(Team).where(Team.name == name)
        )
        return result.scalar_one_or_none()

    async def get_team_members(
        self, team_id: int, user_role: UserRole | None = None
    ) -> List[User]:
        """Получить всех членов команды с фильтрацией по ролям"""
        query = select(User).where(User.team_id == team_id)

        if user_role:
            query = query.where(User.role == user_role)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_user_team(self, user_id: int) -> Team | None:
        """Получить команду пользователя"""
        query = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.team))
        )
        result = await self._session.execute(query)
        user = result.scalar_one_or_none()
        if user and user.team:
            return user.team
        return None

    async def add_member(
        self,
        team: Team,
        user: User,
        user_role: UserRole = UserRole.EMPLOYEE,
    ) -> None:
        """Добавить пользователя в команду"""
        user.team_id = team.id
        user.role = user_role
        await self._session.flush()

    async def remove_member(self, user: User) -> None:
        """Убрать пользователя из команды"""
        user.team_id = None

        if user.role != UserRole.ADMIN:
            user.role = UserRole.USER

        await self._session.flush()

    async def update_member_role(self, user: User, new_role: UserRole) -> None:
        """Изменить роль члена команды"""
        user.role = new_role
        await self._session.flush()

    async def is_members(
        self,
        team_id: int,
        user_ids: List[int],
        user_role: UserRole | None = None,
    ) -> List[int]:
        """
        Являются ли пользователи членами команды
        с дополнительной проверкой по роли
        """
        query = select(User).where(
            User.id.in_(user_ids), User.team_id == team_id
        )
        if user_role:
            query = query.where(User.role == user_role)

        result = await self._session.execute(query)
        valid_users = result.scalars().all()

        invalid_users = list(set(user_ids) - set(valid_users))
        return invalid_users
