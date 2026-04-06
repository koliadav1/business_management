from datetime import datetime
from typing import List

from sqlalchemy import and_, select

from .base_repository import SQLRepository
from src.core.interfaces.repositories.tasks_repository import ITasksRepository
from src.models.tasks import TaskStatus, Task


class TasksRepository(SQLRepository[Task], ITasksRepository):
    def __init__(self, session):
        super().__init__(session, Task)

    async def get_by_executor(self, executor_id: int) -> List[Task]:
        """Получить все задачи для конкретного исполнителя"""
        result = await self._session.execute(
            select(Task).where(Task.executor_id == executor_id)
        )
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

    async def get_overdue(self, user_id: int) -> List[Task]:
        """Получить просроченные задачи конкретного пользователя"""
        query = select(Task).where(
            and_(
                Task.executor_id == user_id,
                Task.deadline < datetime.now(),
                Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            )
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_all_overdue(self) -> List[Task]:
        """Получить все просроченные задачи"""
        query = select(Task).where(
            and_(
                Task.deadline < datetime.now(),
                Task.status.not_in([TaskStatus.DONE, TaskStatus.CANCELLED]),
            )
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def update_status(
        self, task_id: int, new_status: TaskStatus
    ) -> Task | None:
        """Изменить статус задачи"""
        task = await self.get(task_id)
        if task:
            task.status = new_status
            await self._session.flush()
            await self._session.refresh(task)
        return task
