from datetime import datetime
from typing import List

from .dependencies import CheckTeamLogic
from src.core.exceptions import (
    EvaluationNotFoundError,
    ForbiddenError,
    TaskNotCompletedError,
)
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.evaluations import Evaluation
from src.models.users import User, UserRole
from src.models.tasks import Task, TaskStatus


class EvaluationService:
    async def rate_task(
        self,
        task_id: int,
        rating: int,
        current_user: User,
        uow: IUnitOfWork,
        comment: str | None = None,
    ) -> Evaluation:
        """
        Оценить выполненныую задачу от 1 до 5 или обновить оценку.
        Только для admin и manager
        """
        async with uow:
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError("Only admins and managers can rate tasks")

            task = await uow.tasks_repo.get(task_id)
            CheckTeamLogic.check_task_team(current_user, task)

            if task.executor_id == current_user.id:
                raise ForbiddenError("You can't rate tasks assigned to you")

            if task.author_id != current_user.id:
                raise ForbiddenError("You can only rate tasks created by you")

            if task.status != TaskStatus.DONE:
                raise TaskNotCompletedError(
                    f"Task {task_id} is not completed. "
                    f"Current status {task.status}"
                )

            evaluation = await uow.evaluations_repo.get_by_task(task_id)
            if evaluation:
                evaluation.rating = rating
                evaluation.comment = comment
                result = await uow.evaluations_repo.update(evaluation)
            else:
                evaluation = Evaluation(
                    task_id=task_id,
                    rating=rating,
                    comment=comment,
                    rater_id=current_user.id,
                )
                result = await uow.evaluations_repo.add(evaluation)

        return result

    async def get_evaluations(
        self,
        current_user: User,
        uow: IUnitOfWork,
        user_id: int | None = None,
    ) -> List[Evaluation]:
        """
        Получить все оценки пользователя.
        Admin и manager получают оценки любого пользователя либо всей команды
        Employee получают только свои оценки внутри команды
        User получает свои оценки вне зависисомти от команды
        """
        async with uow:
            if current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
                if current_user.team_id is None:
                    raise ForbiddenError("You are not in the team")

                if user_id:
                    user = await uow.users_repo.get(user_id)
                    team_id = CheckTeamLogic.check_user_team(
                        current_user, user
                    )
                    evaluations = (
                        await uow.evaluations_repo.get_user_evaluations(
                            user_id, team_id
                        )
                    )
                else:
                    evaluations = await uow.evaluations_repo.get_by_team(
                        current_user.team_id
                    )
            elif current_user.role == UserRole.EMPLOYEE:
                evaluations = await uow.evaluations_repo.get_user_evaluations(
                    current_user.id, current_user.team_id
                )
            else:
                evaluations = await uow.evaluations_repo.get_user_evaluations(
                    current_user.id
                )

        return evaluations

    async def get_evaluations_with_tasks(
        self, uow: IUnitOfWork, current_user: User, user_id: int | None = None
    ) -> List[tuple[Evaluation, Task]]:
        """
        Получить все оценки пользователя вместе с данными о задачах.
        Admin и manager получают оценки любого пользователя
        Employee получает только свои оценки
        """
        async with uow:
            if current_user.team_id is None:
                raise ForbiddenError("You are not in the team")

            if user_id:
                if current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
                    user = await uow.users_repo.get(user_id)
                    team_id = CheckTeamLogic.check_user_team(
                        current_user, user
                    )
                    evaluations = (
                        await uow.evaluations_repo.get_evaluations_with_tasks(
                            user_id, team_id
                        )
                    )
                    return evaluations

            evaluations = (
                await uow.evaluations_repo.get_evaluations_with_tasks(
                    current_user.id, current_user.team_id
                )
            )

        return evaluations

    async def get_rating_stats(
        self,
        uow: IUnitOfWork,
        current_user: User,
        user_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict | None:
        """
        Получение статистики по оценкам за заданный период времени.
        Admin и manager получают статистику любого пользователя
        Employee получают только свою статистику внутри команды
        User получает свою статистику вне зависимости от команды
        """
        async with uow:
            if current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
                if user_id:
                    user = await uow.users_repo.get(user_id)
                    team_id = CheckTeamLogic.check_user_team(
                        current_user, user
                    )
                    stats = await uow.evaluations_repo.get_statistics(
                        user_id, team_id, start_date, end_date
                    )
                else:
                    stats = await uow.evaluations_repo.get_statistics(
                        current_user.id,
                        current_user.team_id,
                        start_date,
                        end_date,
                    )
            elif current_user.role == UserRole.EMPLOYEE:
                stats = await uow.evaluations_repo.get_statistics(
                    current_user.id, current_user.team_id, start_date, end_date
                )
            else:
                stats = await uow.evaluations_repo.get_statistics(
                    current_user.id, start_date, end_date
                )

        return stats

    async def delete_evaluation(
        self,
        task_id: int,
        uow: IUnitOfWork,
        current_user: User,
    ) -> None:
        """
        Удаление существующей оценки.
        Только для admin и manager
        """
        async with uow:
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can delete evaluations"
                )

            task = await uow.tasks_repo.get(task_id)
            CheckTeamLogic.check_task_team(current_user, task)

            evaluation = await uow.evaluations_repo.get_by_task(task_id)
            if not evaluation:
                raise EvaluationNotFoundError(
                    f"Evaluation for task {task_id} not found"
                )

            await uow.evaluations_repo.delete(evaluation.id)
