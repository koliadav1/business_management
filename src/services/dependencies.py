from src.core.exceptions import (
    ForbiddenError,
    TaskNotFoundError,
    TaskNotInTeamError,
    UserNotFoundError,
    UserNotInTeamError,
)
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.users import User
from src.models.tasks import Task


class CheckTeamLogic:
    """
    Статические методы для сервисов,
    использующих проверки на принадлежность команде
    """

    @staticmethod
    async def check_user_team(
        uow: IUnitOfWork, user_id1: User, user_id2: int
    ) -> int:
        if user_id1.team_id is None:
            raise ForbiddenError(f"User {user_id1} is not in a team")

        executor = await uow.users_repo.get(user_id2)
        if not executor:
            raise UserNotFoundError(f"User with id {user_id2} not found")

        if user_id1.team_id != executor.team_id:
            raise UserNotInTeamError(
                f"User {user_id2} is not in the same team as {user_id1}"
            )

        return user_id1.team_id

    @staticmethod
    async def check_task_team(
        uow: IUnitOfWork, admin_user: User, task_id: int
    ) -> Task:
        if admin_user.team_id is None:
            raise ForbiddenError("Admin is not in a team")

        task = await uow.tasks_repo.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with id {task_id} not found")

        if admin_user.team_id != task.team_id:
            raise TaskNotInTeamError(
                "You can only manage tasks from your team"
            )

        return task
