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
    async def get_team_with_members(self, team_id: int) -> Team | None:
        """Получить команду и ее членов"""
        pass

    @abstractmethod
    async def get_team_members(
        self, team_id: int, user_role: UserRole | None = None
    ) -> List[User]:
        """Получить всех членов команды с фильтрацией по ролям"""
        pass

    @abstractmethod
    async def get_user_team(self, user_id: int) -> Team | None:
        """Получить команду пользователя"""
        pass

    @abstractmethod
    async def add_member(
        self,
        team_id: int,
        user_id: int,
        user_role: UserRole = UserRole.EMPLOYEE,
    ) -> bool:
        """Добавить пользователя в команду"""
        pass

    @abstractmethod
    async def remove_member(self, team_id: int, user_id: int) -> bool:
        """Убрать пользователя из команды"""
        pass

    @abstractmethod
    async def update_member_role(
        self, team_id: int, user_id: int, new_role: UserRole
    ) -> bool:
        """Изменить роль члена команды"""
        pass

    @abstractmethod
    async def is_member(
        self, team_id: int, user_id: int, user_role: UserRole | None = None
    ) -> bool:
        """
        Является ли пользователь членом команды
        с дополнительной проверкой по роли
        """
        pass
