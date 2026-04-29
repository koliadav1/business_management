from datetime import datetime, timezone
from typing import List

from src.models.evaluations import Evaluation

from .dependencies import CheckTeamLogic
from src.core.exceptions import (
    ForbiddenError,
    InvalidTransitionError,
)
from src.models.tasks import Task, TaskStatus
from src.models.users import User, UserRole
from src.core.interfaces.unit_of_work import IUnitOfWork


class TaskService:
    async def create_task(
        self,
        description: str,
        deadline: datetime,
        executor_id: int,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Task:
        """
        Создание задачи.
        Только для admin и manager
        """
        async with uow:
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can create tasks"
                )

            executor = await uow.users_repo.get(executor_id)
            team_id = CheckTeamLogic.check_user_team(current_user, executor)

            if (
                executor.role == UserRole.MANAGER
                and current_user.role == UserRole.Manager
            ):
                raise ForbiddenError(
                    "Managers can't assign other managers to tasks"
                )

            task = Task(
                description=description,
                deadline=deadline,
                executor_id=executor_id,
                author_id=current_user.id,
                team_id=team_id,
                status=TaskStatus.NEW,
            )

            created_task = await uow.tasks_repo.add(task)
        return created_task

    async def assign_executor(
        self,
        task_id: int,
        executor_id: int,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Task:
        """
        Переназначить исполнителя задачи.
        Только для admin и автора задачи
        """
        async with uow:
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can assign executors"
                )

            executor = await uow.users_repo.get(executor_id)
            CheckTeamLogic.check_user_team(current_user, executor)

            if (
                executor.role == UserRole.MANAGER
                and current_user.role == UserRole.Manager
            ):
                raise ForbiddenError(
                    "Managers can't assign other managers to tasks"
                )

            task = await uow.tasks_repo.get(task_id)
            CheckTeamLogic.check_task_team(current_user, task)

            if not self._can_manage_task(task, current_user):
                raise ForbiddenError(
                    "Only admins and task authors can manage task"
                )

            task.executor_id = executor_id
            updated_task = await uow.tasks_repo.update(task)

        return updated_task

    async def update_task(
        self,
        task_id: int,
        description: str | None,
        deadline: datetime | None,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Task:
        """
        Изменение описания и дедлайна задачи.
        Только для admin и автора задачи
        """
        async with uow:
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can update tasks"
                )

            task = await uow.tasks_repo.get(task_id)
            CheckTeamLogic.check_task_team(current_user, task)

            if not self._can_manage_task(task, current_user):
                raise ForbiddenError(
                    "Only admins and task authors can manage task"
                )

            if task.status in [TaskStatus.CANCELLED, TaskStatus.DONE]:
                raise ForbiddenError(
                    "You can't update cancelled or done tasks"
                )

            if description:
                task.description = description

            if deadline:
                task.deadline = deadline

            updated_task = await uow.tasks_repo.update(task)

        return updated_task

    async def delete_task(
        self,
        task_id: int,
        current_user: User,
        uow: IUnitOfWork,
    ) -> None:
        """
        Удаление задачи.
        Только для admin и автора задачи
        """
        async with uow:
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can update tasks"
                )

            task = await uow.tasks_repo.get(task_id)
            CheckTeamLogic.check_task_team(current_user, task)
            if not self._can_manage_task(task, current_user):
                raise ForbiddenError(
                    "Only admins and task authors can manage task"
                )

            await uow.tasks_repo.delete(task_id)

    async def change_status(
        self,
        task_id: int,
        new_status: TaskStatus,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Task:
        """
        Изменение статуса задачи.
        Admin и автор задачи - установка любого статуса
        Executor - только статусы DONE и IN_PROGRESS
        """
        async with uow:
            task = await uow.tasks_repo.get(task_id)
            CheckTeamLogic.check_task_team(current_user, task)
            if not self._can_change_status(task, new_status, current_user):
                raise ForbiddenError(
                    f"User {current_user.role.value} can't change status from "
                    f"{task.status.value} to {new_status.value}"
                )

            if not self._is_valid_transition(task.status, new_status):
                raise InvalidTransitionError(
                    f"Can't change status from "
                    f"{task.status.value} to {new_status.value}"
                )

            old_status = task.status
            task.status = new_status

            if new_status == TaskStatus.DONE and task.completed_at is None:
                task.completed_at = datetime.now(timezone.utc)

            if old_status == TaskStatus.DONE and new_status != TaskStatus.DONE:
                task.completed_at = None

            updated_task = await uow.tasks_repo.update(task)

        return updated_task

    async def get_task(
        self,
        task_id: int,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Task | None:
        """
        Получить задачу по ID.
        Только для admin, manager и исполнителя задачи
        """
        async with uow:
            task = await uow.tasks_repo.get_task_with_comments(task_id)
            CheckTeamLogic.check_task_team(current_user, task)

            if current_user.id == task.executor_id or current_user.role in [
                UserRole.ADMIN,
                UserRole.MANAGER,
            ]:
                return task
            else:
                ForbiddenError("You cant view this task")

    async def get_user_tasks(
        self,
        uow: IUnitOfWork,
        current_user: User,
        page: int,
        limit: int,
        status: TaskStatus | None = None,
        user_id: int | None = None,
        deadline_from: datetime | None = None,
        deadline_to: datetime | None = None,
    ) -> List[Task]:
        """
        Получить задачи пользователя
        Admin и manager видят задачи любого пользователя
        Обычный пользователь видит только свои задачи
        """
        async with uow:
            skip = (page - 1) * limit
            if current_user.team_id is None:
                raise ForbiddenError("You're not in a team")

            if user_id and user_id != current_user.id:
                if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                    raise ForbiddenError(
                        "Only admins and managers can view other user's tasks"
                    )

            target_id = user_id if user_id else current_user.id

            tasks, total = await uow.tasks_repo.get_by_executor(
                target_id,
                current_user.team_id,
                skip,
                limit,
                status,
                deadline_from,
                deadline_to,
            )

        return {
            "items": tasks,
            "total": total,
            "page": page,
            "page_size": limit,
        }

    async def get_team_tasks(
        self,
        uow: IUnitOfWork,
        current_user: User,
        page: int,
        limit: int,
        status: TaskStatus | None = None,
        deadline_from: datetime | None = None,
        deadline_to: datetime | None = None,
    ) -> List[Task]:
        """
        Получить все задачи команды.
        Только для admin и manager
        """
        async with uow:
            skip = (page - 1) * limit

            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can view team tasks"
                )
            tasks, total = await uow.tasks_repo.get_by_team(
                current_user.team_id,
                skip,
                limit,
                status,
                deadline_from,
                deadline_to,
            )
        return {
            "items": tasks,
            "total": total,
            "page": page,
            "page_size": limit,
        }

    async def get_user_overdue_tasks(
        self,
        current_user: User,
        uow: IUnitOfWork,
        page: int,
        limit: int,
        user_id: int | None = None,
    ) -> List[Task]:
        """
        Получить просроченные задачи пользователя.
        Admin и manager видят задачи любого пользователя
        Обычный пользователь видит только свои задачи
        """
        async with uow:
            skip = (page - 1) * limit

            if current_user.team_id is None:
                raise ForbiddenError("You're not in a team")

            if user_id and user_id != current_user.id:
                if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                    raise ForbiddenError(
                        "Only admins and managers can view other user's tasks"
                    )

            target_id = user_id if user_id else current_user.id

            tasks, total = await uow.tasks_repo.get_overdue_for_user(
                target_id, current_user.team_id, skip, limit
            )

        return {
            "items": tasks,
            "total": total,
            "page": page,
            "page_size": limit,
        }

    async def get_team_overdue_tasks(
        self,
        current_user: User,
        uow: IUnitOfWork,
        page: int,
        limit: int,
    ) -> List[Task]:
        """
        Получить просроченные задачи команды.
        Только для admin и manager
        """
        async with uow:
            skip = (page - 1) * limit

            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can view team tasks"
                )
            tasks, total = await uow.tasks_repo.get_overdue_for_team(
                current_user.team_id, skip, limit
            )
        return {
            "items": tasks,
            "total": total,
            "page": page,
            "page_size": limit,
        }

    async def get_done_tasks_with_evaluations(
        self,
        uow: IUnitOfWork,
        current_user: User,
        page: int,
        limit: int,
    ) -> List[tuple[Task, Evaluation]]:
        """
        Получить все сделанные задачи команды с соответствующими оценками.
        Только для admin и manager
        """
        async with uow:
            skip = (page - 1) * limit
            if current_user.team_id is None:
                raise ForbiddenError("You are not in the team")

            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers "
                    "can view other user's evaluations"
                )

            tasks, total = (
                await uow.evaluations_repo.get_done_tasks_with_evaluations(
                    current_user.team_id, skip, limit
                )
            )

        return {
            "items": tasks,
            "total": total,
            "page": page,
            "page_size": limit,
        }

    def _can_change_status(
        self, task: Task, new_status: TaskStatus, user: User
    ) -> bool:
        """Проверка прав на изменение статуса"""
        if self._can_manage_task(task, user):
            return True

        if user.id == task.executor_id:
            return new_status in [TaskStatus.IN_PROGRESS, TaskStatus.DONE]

        return False

    def _can_manage_task(self, task: Task, user: User) -> None:
        """Проверка прав на управление задачей"""
        if user.role == UserRole.ADMIN or user.id == task.author_id:
            return True
        else:
            return False

    def _is_valid_transition(
        self, current: TaskStatus, new: TaskStatus
    ) -> bool:
        transitions = {
            TaskStatus.NEW: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
            TaskStatus.IN_PROGRESS: {TaskStatus.DONE, TaskStatus.CANCELLED},
            TaskStatus.DONE: {TaskStatus.IN_PROGRESS},
            TaskStatus.CANCELLED: set(),
        }
        return new in transitions.get(current, set())
