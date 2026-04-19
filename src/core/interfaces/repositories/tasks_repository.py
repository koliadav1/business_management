from abc import abstractmethod
from typing import List

from src.models.tasks import TaskStatus, Task
from .base_repository import IRepository


class ITasksRepository(IRepository[Task]):
    @abstractmethod
    async def get_by_executor(
        self, executor_id: int, team_id: int
    ) -> List[Task]:
        """Получить все задачи для конкретного исполнителя"""
        pass

    @abstractmethod
    async def get_by_author(self, author_id: int) -> List[Task]:
        """Получить все задачи по их создателю"""
        pass

    @abstractmethod
    async def get_by_status(self, status: TaskStatus) -> List[Task]:
        """Получить все задачи по их статусу"""
        pass

    @abstractmethod
    async def get_overdue_for_user(
        self, user_id: int, team_id: int
    ) -> List[Task]:
        """Получить просроченные задачи конкретного пользователя"""
        pass

    @abstractmethod
    async def get_overdue_for_team(self, team_id: int) -> List[Task]:
        """Получить все просроченные задачи"""
        pass

    @abstractmethod
    async def update_status(
        self, task_id: int, new_status: TaskStatus
    ) -> Task | None:
        """Изменить статус задачи"""
        pass

    @abstractmethod
    async def get_by_team(self, team_id: int) -> List[Task]:
        """Получить все задачи команды"""
        pass
