from typing import List, TypeVar
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces.repositories.base_repository import IRepository

T = TypeVar("T")


class SQLRepository(IRepository[T]):
    """Базовый репозиторий с общими CRUD опреациями"""

    def __init__(self, session: AsyncSession, model: type[T]):
        self._session = session
        self._model = model

    async def get(self, id: int) -> T | None:
        """Получить сущность по ID"""
        return await self._session.get(self._model, id)

    async def get_all(self) -> List[T]:
        """Получить все сущности"""
        result = await self._session.execute(select(self._model))
        return result.scalars().all()

    async def add(self, entity: T) -> T:
        """Добавить сущность"""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """Обновить сущность"""
        self._session.merge(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, id: int) -> None:
        """Удалить сущность по ID"""
        await self._session.execute(
            delete(self._model).where(self._model.id == id)
        )
        await self._session.flush()
