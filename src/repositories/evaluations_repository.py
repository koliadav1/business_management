from datetime import datetime
from typing import List

from sqlalchemy import and_, case, func, select

from src.models.tasks import Task
from src.repositories.base_repository import SQLRepository
from src.core.interfaces.repositories.evaluations_repository import (
    IEvaluationsRepository,
)
from src.models.users import User
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

    async def get_user_evaluations(
        self, user_id: int, team_id: int | None = None
    ) -> List[Evaluation]:
        """Получить все оценки пользователя"""
        query = (
            select(Evaluation)
            .join(Task, Evaluation.task_id == Task.id)
            .where(Task.executor_id == user_id)
            .order_by(Evaluation.created_at.desc())
        )
        if team_id:
            query = query.where(Task.team_id == team_id)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_statistics(
        self,
        user_id: int,
        team_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict | None:
        """Получить сводку по оценкам пользователя"""
        query = (
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

        if team_id:
            query = query.where(Task.team_id == team_id)
        if start_date:
            query = query.where(Task.completed_at >= start_date)
        if end_date:
            query = query.where(Task.completed_at <= end_date)

        result = await self._session.execute(query)
        row = result.one_or_none()

        return {
            "total": row.total if row.total else 0,
            "average": float(row.avg) if row.avg else 0.0,
            "distribution": {
                5: row.rating_5 or 0,
                4: row.rating_4 or 0,
                3: row.rating_3 or 0,
                2: row.rating_2 or 0,
                1: row.rating_1 or 0,
            },
        }

    async def get_evaluations_with_tasks(
        self,
        user_id: int,
        team_id: int,
    ) -> List[tuple[Evaluation, Task]]:
        """Получить данные об оценках и задачах пользователя"""
        query = (
            select(
                Evaluation,
                Task,
            )
            .join(Task, Evaluation.task_id == Task.id)
            .where(and_(Task.executor_id == user_id, Task.team_id == team_id))
        )

        result = await self._session.execute(query)
        return result.all()

    async def get_by_team(self, team_id: int) -> List[dict]:
        """Получить оценки и задачи для всей команды"""
        result = await self._session.execute(
            select(
                Evaluation,
                Task,
                User.email,
            )
            .join(Task, Evaluation.task_id == Task.id)
            .join(User, Task.executor_id == User.id)
            .where(Task.team_id == team_id)
            .order_by(Evaluation.created_at.desc())
        )
        rows = result.all()

        return [
            {
                "evaluation": evaluation,
                "task": task,
                "executor": executor,
            }
            for evaluation, task, executor in rows
        ]
