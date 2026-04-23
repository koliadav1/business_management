from abc import ABC, abstractmethod

from src.models.users import User, UserRole


class IUsersRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> User | None:
        """Получение пользователя по ID"""
        pass

    @abstractmethod
    async def exists(self, user_id: int) -> bool:
        """Проверка существования пользоватея"""
        pass

    @abstractmethod
    async def update_user_role(self, user: User, new_role: UserRole) -> None:
        """Изменить роль пользователя"""
        pass
