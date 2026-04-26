from src.core.exceptions import (
    ForbiddenError,
    TaskNotFoundError,
    TaskNotInTeamError,
    UserNotFoundError,
    UserNotInTeamError,
)
from src.models.users import User
from src.models.tasks import Task


class CheckTeamLogic:
    """
    Статические методы для сервисов,
    использующих проверки на принадлежность команде
    """

    @staticmethod
    def check_user_team(user1: User, user2: User) -> int:
        if user1.team_id is None:
            raise ForbiddenError(f"User {user1.id} is not in a team")

        if not user2:
            raise UserNotFoundError("User not found")

        if user1.team_id != user2.team_id:
            raise UserNotInTeamError(
                f"User {user2.id} is not in the same team as {user1.id}"
            )

        return user1.team_id

    @staticmethod
    def check_task_team(admin_user: User, task: Task) -> None:
        if admin_user.team_id is None:
            raise ForbiddenError("Admin is not in a team")

        if not task:
            raise TaskNotFoundError("Task not found")

        if admin_user.team_id != task.team_id:
            raise TaskNotInTeamError(
                "You can only manage tasks from your team"
            )

        return task
