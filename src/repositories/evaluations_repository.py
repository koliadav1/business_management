from datetime import datetime
from typing import List

from sqlalchemy import and_, case, func, select

from src.models.tasks import Task, TaskStatus
from src.repositories.base_repository import SQLRepository
from src.core.interfaces.repositories.evaluations_repository import (
    IEvaluationsRepository,
)
from src.models.evaluations import Evaluation


class EvaluationsRepository(SQLRepository[Evaluation], IEvaluationsRepository):
    def __init__(self, session):
        super().__init__(session, Evaluation)

    async def get_by_task(self, task_id: int) -> Evaluation | None:
        """Получить оценку по ID задачи"""
        result = await self._session.execute(
            select(Evaluation).where(Evaluation.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_user_evaluations(self, user_id: int) -> List[Evaluation]:
        """Получить все оценки пользователя"""
        result = await self._session.execute(
            select(Evaluation)
            .join(Task, Evaluation.task_id == Task.id)
            .where(Task.executor_id == user_id)
            .order_by(Evaluation.created_at.desc())
        )
        return result.scalars().all()

    async def get_avg_rating(
        self, user_id: int, start_date: datetime, end_date: datetime
    ) -> float:
        """Получить средний рейтинг выполненных задач за заданный период"""
        result = await self._session.execute(
            select(func.avg(Evaluation.rating))
            .join(Task, Evaluation.task_id == Task.id)
            .where(
                and_(
                    Task.executor_id == user_id,
                    Task.status == TaskStatus.DONE,
                    Task.completed_at.is_not(None),
                    Task.completed_at.between(start_date, end_date),
                )
            )
        )
        avg = result.scalar_one_or_none()
        return avg or 0.0

    async def get_statistics(self, user_id: int) -> dict:
        """Получить сводку по оценкам пользователя"""
        result = self._session.execute(
            select(
                func.count(Evaluation.id).label("total"),
                func.avg(Evaluation.rating).label("avg"),
                func.sum(case((Evaluation.rating == 5, 1), else_=0)).label(
                    "rating_5"
                ),
                func.sum(case((Evaluation.rating == 4, 1), else_=0)).label(
                    "rating_4"
                ),
                func.sum(case((Evaluation.rating == 3, 1), else_=0)).label(
                    "rating_3"
                ),
                func.sum(case((Evaluation.rating == 2, 1), else_=0)).label(
                    "rating_2"
                ),
                func.sum(case((Evaluation.rating == 1, 1), else_=0)).label(
                    "rating_1"
                ),
            )
            .join(Task, Evaluation.task_id == Task.id)
            .where(Task.executor_id == user_id)
        )
        row = result.scalar()

        return {
            "total": row.total or 0,
            "average": float(row.avg) or 0.0,
            "distribution": {
                5: row.rating_5 or 0,
                4: row.rating_4 or 0,
                3: row.rating_3 or 0,
                2: row.rating_2 or 0,
                1: row.rating_1 or 0,
            },
        }
