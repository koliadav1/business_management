from src.core.interfaces.repositories.users_repository import IUsersRepository
from src.models.users import User


class UsersRepository(IUsersRepository):
    async def get(self, user_id: int) -> User | None:
        """Получение пользователя по ID"""
        pass

    async def exists(self, user_id: int) -> bool:
        """Проверка существования пользователя"""
        pass
