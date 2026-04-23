from datetime import datetime
from typing import List

from sqlalchemy import select

from .base_repository import SQLRepository
from src.core.interfaces.repositories.tasks_repository import ITasksRepository
from src.models.tasks import TaskStatus, Task


class TasksRepository(SQLRepository[Task], ITasksRepository):
    def __init__(self, session):
        super().__init__(session, Task)

    async def get_by_executor(
        self,
        executor_id: int,
        team_id: int,
        status: TaskStatus | None = None,
        deadline_from: datetime | None = None,
        deadline_to: datetime | None = None,
    ) -> List[Task]:
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

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_author(self, author_id: int) -> List[Task]:
        """Получить все задачи по их создателю"""
        result = await self._session.execute(
            select(Task).where(Task.author_id == author_id)
        )
        return result.scalars().all()

    async def get_by_status(self, status: TaskStatus) -> List[Task]:
        """Получить все задачи по их статусу"""
        result = await self._session.execute(
            select(Task).where(Task.status == status)
        )
        return result.scalars().all()

    async def get_overdue_for_user(
        self, user_id: int, team_id: int
    ) -> List[Task]:
        """Получить просроченные задачи конкретного пользователя"""
        query = select(Task).where(
            Task.executor_id == user_id,
            Task.deadline < datetime.now(),
            Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            Task.team_id == team_id,
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_overdue_for_team(self, team_id: int) -> List[Task]:
        """Получить все просроченные задачи"""
        query = select(Task).where(
            Task.deadline < datetime.now(),
            Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            Task.team_id == team_id,
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_team(
        self,
        team_id: int,
        status: TaskStatus | None = None,
        deadline_from: datetime | None = None,
        deadline_to: datetime | None = None,
    ) -> List[Task]:
        query = select(Task).where(Task.team_id == team_id)

        if status:
            query = query.where(Task.status == status)
        if deadline_from:
            query = query.where(Task.deadline >= deadline_from)
        if deadline_to:
            query = query.where(Task.deadline <= deadline_to)

        result = await self._session.execute(query)
        return result.scalars().all()
