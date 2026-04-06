from datetime import datetime
from typing import List

from src.core.exceptions import (
    ForbiddenError,
    InvalidTransitionError,
    TaskNotFoundError,
    UserNotFoundError,
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
        Только для роли admin
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admins can create tasks")

            if not await uow.users_repo.exists(executor_id):
                raise UserNotFoundError(
                    f"Executor with {executor_id} id not found"
                )

            task = Task(
                description=description,
                deadline=deadline,
                executor_id=executor_id,
                author_id=current_user.id,
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
        Только для роли admin
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admins can assign executor")

            task = await uow.tasks_repo.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task with {task_id} id not found")

            if not await uow.users_repo.exists(executor_id):
                raise UserNotFoundError(
                    f"Executor with {executor_id} id not found"
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
        Только для роли admin
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admins can update tasks")

            task = await uow.tasks_repo.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task with {task_id} id not found")

            if description:
                task.description = description

            if deadline:
                if deadline < datetime.now():
                    raise ValueError("Deadline can't be in the past")
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
        Только для роли admin
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                raise ForbiddenError("Only admins can delete tasks")

            task = await uow.tasks_repo.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task with {task_id} id not found")

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
        Admin - установка любого статуса
        Executor - только статусы DONE и IN_PROGRESS
        """
        async with uow:
            task = await uow.tasks_repo.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task with {task_id} id not found")

            if not self._can_change_status(task, new_status, current_user):
                raise ForbiddenError(
                    f"User {current_user.role.value} can't change status from "
                    f"{task.status.value} to {new_status.value}"
                )

            if not self._is_valid_transition(task.status, new_status):
                raise InvalidTransitionError(
                    f"Can't change status from "
                    f"{task.status.value} to {new_status.valuse}"
                )

            task.status = new_status
            updated_task = await uow.tasks_repo.update(task)

        return updated_task

    async def get_task(
        self,
        task_id: int,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Task:
        """
        Получить задачу по ID.
        Только для admin и исполнителя задачи
        """
        async with uow:
            task = await uow.tasks_repo.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task with {task_id} id not found")

            if (
                current_user.role == UserRole.ADMIN
                or current_user.id == task.executor_id
            ):
                return task
            else:
                raise ForbiddenError("You don't have access to this task")

    async def get_user_tasks(
        self,
        uow: IUnitOfWork,
        current_user: User,
        status: TaskStatus | None = None,
        user_id: int | None = None,
    ) -> List[Task]:
        """
        Получить задачи пользователя
        Admin видит задачи любого пользователя
        Обычный пользователь видит только свои задачи
        """
        async with uow:
            if current_user.role == UserRole.ADMIN and user_id:
                tasks = await uow.tasks_repo.get_by_executor(user_id)
            elif not user_id:
                tasks = await uow.tasks_repo.get_by_executor(current_user.id)
            elif user_id and current_user.role != UserRole.ADMIN:
                raise ForbiddenError("You can only see your tasks")
            if status:
                tasks = [task for task in tasks if task.status == status]

        return tasks

    async def get_overdue_tasks(
        self,
        current_user: User,
        uow: IUnitOfWork,
    ) -> List[Task]:
        """
        Получить все просроченные задачи.
        Admin видит задачи любого пользователя
        Обычный пользователь видит только свои задачи
        """
        async with uow:
            if current_user.role != UserRole.ADMIN:
                tasks = await uow.tasks_repo.get_overdue(current_user.user_id)
            else:
                tasks = await uow.tasks_repo.get_all_overdue()
        return tasks

    def _can_change_status(
        self, task: Task, new_status: TaskStatus, user: User
    ) -> bool:
        """Проверка прав на изменение статуса"""
        if user.role == UserRole.ADMIN:
            return True

        if user.id == task.executor_id:
            allowed_statuses = [TaskStatus.IN_PROGRESS, TaskStatus.DONE]
            return new_status in allowed_statuses

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
