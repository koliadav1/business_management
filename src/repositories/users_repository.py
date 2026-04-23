from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces.repositories.users_repository import IUsersRepository
from src.models.users import User, UserRole


class UsersRepository(IUsersRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: int) -> User | None:
        """Получение пользователя по ID"""
        return await self._session.get(User, user_id)

    async def exists(self, user_id: int) -> bool:
        """Проверка существования пользователя"""
        query = select(exists().where(User.id == user_id))
        result = await self._session.execute(query)
        return result.scalar()

    async def update_user_role(self, user: User, new_role: UserRole) -> None:
        """Изменить роль пользователя"""
        user.role = new_role
        await self._session.flush()
