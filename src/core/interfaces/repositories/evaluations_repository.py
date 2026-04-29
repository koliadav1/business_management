from abc import abstractmethod
from datetime import datetime
from typing import List

from src.models.tasks import Task
from src.models.evaluations import Evaluation
from src.core.interfaces.repositories.base_repository import IRepository


class IEvaluationsRepository(IRepository[Evaluation]):
    @abstractmethod
    async def get_by_task(self, task_id: int) -> Evaluation | None:
        """Получить оценку по ID задачи"""
        pass

    @abstractmethod
    async def get_user_evaluations(
        self, user_id: int, skip: int, limit: int, team_id: int | None = None
    ) -> tuple[List[Evaluation], int]:
        """Получить все оценки пользователя"""
        pass

    @abstractmethod
    async def get_statistics(
        self,
        user_id: int,
        team_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict | None:
        """Получить сводку по оценкам пользователя"""
        pass

    @abstractmethod
    async def get_evaluations_with_tasks(
        self, user_id: int, team_id: int, skip: int, limit: int
    ) -> tuple[tuple[Evaluation, Task], int]:
        """Получить данные об оценках и задачах пользователя"""
        pass

    @abstractmethod
    async def get_by_team(
        self, team_id: int, skip: int, limit: int
    ) -> tuple[List[Evaluation], int]:
        """Получить оценки всей команды"""
        pass

    @abstractmethod
    async def get_done_tasks_with_evaluations(
        self, team_id: int, skip: int, limit: int
    ) -> tuple[tuple[Task, Evaluation], int]:
        """Получить оценки сделанные задачи и оценки к ним, если они есть"""
        pass
