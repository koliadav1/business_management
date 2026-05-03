from typing import List

from sqlalchemy import select

from src.models.tasks import Comment
from src.core.interfaces.repositories.comments_repository import (
    ICommentsRepository,
)
from .base_repository import SQLRepository


class CommentsRepository(ICommentsRepository, SQLRepository):
    def __init__(self, session):
        super().__init__(session, Comment)

    async def get_by_task(self, task_id: int) -> List[Comment] | None:
        """Получить комментарии по ID задачи"""
        result = await self._session.execute(
            select(Comment).where(Comment.task_id == task_id)
        )
        return result.scalars().all()

    async def get_by_author(self, user_id: int) -> List[Comment] | None:
        """Получить все комментарии пользователя"""
        result = await self._session.execute(
            select(Comment).where(Comment.author_id == user_id)
        )
        return result.scalars().all()
