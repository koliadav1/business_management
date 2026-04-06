from abc import ABC, abstractmethod

from src.models.users import User


class IUsersRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> User | None:
        """Получение пользователя по ID"""
        pass

    @abstractmethod
    async def exists(self, user_id: int) -> bool:
        """Проверка существования пользоватея"""
        pass
