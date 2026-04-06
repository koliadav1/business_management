from typing import List

from src.core.interfaces.repositories.tasks_repository import ITasksRepository
from src.models.tasks import TaskStatus, Task


class TasksRepository(ITasksRepository):
    async def get_by_executor(self, executor_id: int) -> List[Task]:
        """Получить все задачи для конкретного исполнителя"""
        pass

    async def get_by_author(self, author_id: int) -> List[Task]:
        """Получить все задачи по их создателю"""
        pass

    async def get_by_status(self, status: TaskStatus) -> List[Task]:
        """Получить все задачи по их статусу"""
        pass

    async def get_overdue(self, user_id: int) -> List[Task]:
        """Получить просроченные задачи конкретного пользователя"""
        pass

    async def get_all_overdue(self) -> List[Task]:
        """Получить все просроченные задачи"""
        pass

    async def update_status(
        self, task_id: int, new_status: TaskStatus
    ) -> Task | None:
        """Изменить статус задачи"""
        pass
