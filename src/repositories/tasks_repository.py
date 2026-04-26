from datetime import datetime
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from .base_repository import SQLRepository
from src.core.interfaces.repositories.tasks_repository import ITasksRepository
from src.models.tasks import Comment, TaskStatus, Task


class TasksRepository(SQLRepository[Task], ITasksRepository):
    def __init__(self, session):
        super().__init__(session, Task)

    async def get_by_executor(
        self,
        executor_id: int,
        team_id: int,
        skip: int,
        limit: int,
        status: TaskStatus | None = None,
        deadline_from: datetime | None = None,
        deadline_to: datetime | None = None,
    ) -> tuple[List[Task], int]:
        """Получить все задачи для конкретного исполнителя"""
        query = select(Task).where(
            Task.executor_id == executor_id, Task.team_id == team_id
        )

        if status:
            query = query.where(Task.status == status)
        if deadline_from:
            query = query.where(Task.deadline >= deadline_from)
        if deadline_to:
            query = query.where(Task.deadline <= deadline_to)

        paginated_query = query.offset(skip).limit(limit)

        result = await self._session.execute(paginated_query)
        tasks = result.scalars().all()

        count_query = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_query.scalar_one_or_none()

        return tasks, total or 0

    async def get_overdue_for_user(
        self, user_id: int, team_id: int, skip: int, limit: int
    ) -> tuple[List[Task], int]:
        """Получить просроченные задачи конкретного пользователя"""
        query = select(Task).where(
            Task.executor_id == user_id,
            Task.deadline < datetime.now(),
            Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            Task.team_id == team_id,
        )

        paginated_query = query.offset(skip).limit(limit)

        result = await self._session.execute(paginated_query)
        tasks = result.scalars().all()

        count_query = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_query.scalar_one_or_none()

        return tasks, total or 0

    async def get_overdue_for_team(
        self, team_id: int, skip: int, limit: int
    ) -> tuple[List[Task], int]:
        """Получить все просроченные задачи"""
        query = select(Task).where(
            Task.deadline < datetime.now(),
            Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            Task.team_id == team_id,
        )
        paginated_query = query.offset(skip).limit(limit)

        result = await self._session.execute(paginated_query)
        tasks = result.scalars().all()

        count_query = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_query.scalar_one_or_none()

        return tasks, total or 0

    async def get_by_team(
        self,
        team_id: int,
        skip: int,
        limit: int,
        status: TaskStatus | None = None,
        deadline_from: datetime | None = None,
        deadline_to: datetime | None = None,
    ) -> tuple[List[Task], int]:
        query = select(Task).where(Task.team_id == team_id)

        if status:
            query = query.where(Task.status == status)
        if deadline_from:
            query = query.where(Task.deadline >= deadline_from)
        if deadline_to:
            query = query.where(Task.deadline <= deadline_to)

        paginated_query = query.offset(skip).limit(limit)

        result = await self._session.execute(paginated_query)
        tasks = result.scalars().all()

        count_query = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_query.scalar_one_or_none()

        return tasks, total or 0

    async def get_task_with_comments(self, task_id: int) -> Task:
        """Получить задачу вместе с комментариями к ней"""
        result = await self._session.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(joinedload(Task.comments).joinedload(Comment.author))
        )
        return result.scalar_one_or_none()
