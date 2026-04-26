from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get(self, id: int) -> T | None:
        """Получить сущность по ID"""
        pass

    @abstractmethod
    async def get_all_paginated(
        self, skip: int, limit: int
    ) -> tuple[List[T], int]:
        """Получить все сущности"""
        pass

    @abstractmethod
    async def add(self, entity: T) -> T:
        """Добавить сущность"""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Обновить сущность"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> None:
        """Удалить сущность по ID"""
        pass
