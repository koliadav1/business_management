from abc import abstractmethod
from typing import List

from src.models.users import User, UserRole
from src.models.teams import Team
from .base_repository import IRepository


class ITeamsRepository(IRepository[Team]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Team | None:
        """Получить команду по названию"""
        pass

    @abstractmethod
    async def get_team_members(
        self, team_id: int, user_role: UserRole | None = None
    ) -> List[User]:
        """Получить всех членов команды с фильтрацией по ролям"""
        pass

    @abstractmethod
    async def add_member(
        self,
        team: Team,
        user: User,
        user_role: UserRole = UserRole.EMPLOYEE,
    ) -> None:
        """Добавить пользователя в команду"""
        pass

    @abstractmethod
    async def remove_member(self, user: User) -> None:
        """Убрать пользователя из команды"""
        pass

    @abstractmethod
    async def remove_all_members(self, team_id: int) -> None:
        """Убрать всех пользователей из команды"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_by_invite_code(self, code: str) -> Team | None:
        """Получить команду по коду приглашения"""
        pass
