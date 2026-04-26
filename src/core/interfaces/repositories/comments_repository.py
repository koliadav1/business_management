from abc import abstractmethod
from typing import List

from src.models.tasks import Comment
from src.core.interfaces.repositories.base_repository import IRepository


class ICommentsRepository(IRepository[Comment]):
    @abstractmethod
    async def get_by_task(self, task_id: int) -> List[Comment] | None:
        """Получить комментарии по ID задачи"""
        pass

    @abstractmethod
    async def get_by_author(self, user_id: int) -> List[Comment] | None:
        """Получить все комментарии пользователя"""
        pass
