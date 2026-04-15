from abc import abstractmethod
from datetime import datetime
from typing import List

from src.models.evaluations import Evaluation
from src.core.interfaces.repositories.base_repository import IRepository


class IEvaluationsRepository(IRepository[Evaluation]):
    @abstractmethod
    async def get_by_task(self, task_id: int) -> Evaluation | None:
        """Получить оценку по ID задачи"""
        pass

    @abstractmethod
    async def get_user_evaluations(self, user_id: int) -> List[Evaluation]:
        """Получить все оценки пользователя"""
        pass

    @abstractmethod
    async def get_avg_rating(
        self, user_id: int, start_date: datetime, end_date: datetime
    ) -> float:
        """Получить средний рейтинг выполненных задач за заданный период"""
        pass

    @abstractmethod
    async def get_statistics(self, user_id: int) -> dict:
        """Получить сводку по оценкам пользователя"""
        pass
