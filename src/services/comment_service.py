from typing import List

from src.core.exceptions import (
    CommentNotFoundError,
    ForbiddenError,
    TaskNotFoundError,
)
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.users import User, UserRole
from src.models.tasks import Comment


class CommentService:
    async def add_comment(
        self, task_id: int, content: str, current_user: User, uow: IUnitOfWork
    ) -> Comment:
        """
        Добавить комменатрий к задаче.
        Только для admin, manager и исполнителя задачи
        """
        async with uow:
            task = await uow.tasks_repo.get(task_id)

            if not task:
                raise TaskNotFoundError(f"Task with ID {task_id} not found")

            if (
                current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]
                and current_user.id != task.executor_id
            ):
                raise ForbiddenError("You don't have access to this task")

            comment = Comment(
                content=content, task_id=task_id, author_id=current_user.id
            )

            created_comment = await uow.comments_repo.add(comment)

        return created_comment

    async def get_task_comments(
        self, task_id: int, current_user: User, uow: IUnitOfWork
    ) -> List[Comment]:
        """
        Получить комментарии к задаче.
        Только для admin, manager и исполнителя задачи
        """
        async with uow:
            task = await uow.tasks_repo.get(task_id)

            if not task:
                raise TaskNotFoundError(f"Task with ID {task_id} not found")

            if (
                current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]
                and current_user.id != task.executor_id
            ):
                raise ForbiddenError("You don't have access to this task")

            comments = await uow.comments_repo.get_by_task(task_id)

        return comments

    async def update_comment(
        self,
        comment_id: int,
        content: str,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Comment:
        """
        Изменить комментарий.
        Только для автора комменатрия и admin
        """
        async with uow:
            comment = await uow.comments_repo.get(comment_id)
            if not comment:
                raise CommentNotFoundError(
                    f"Comment with ID {comment_id} not found"
                )

            if (
                current_user.id != comment.author_id
                and current_user.role != UserRole.ADMIN
            ):
                raise ForbiddenError("You can't edit this comment")

            comment.content = content
            updated_comment = await uow.comments_repo.update(comment)

        return updated_comment

    async def delete_comment(
        self, comment_id: int, current_user: User, uow: IUnitOfWork
    ) -> None:
        """
        Удалить комментарий.
        Только для автора комментария и admin
        """
        async with uow:
            comment = await uow.comments_repo.get(comment_id)
            if not comment:
                raise CommentNotFoundError(
                    f"Comment with ID {comment_id} not found"
                )

            if (
                current_user.id != comment.author_id
                or current_user.role != UserRole.ADMIN
            ):
                raise ForbiddenError("You can't edit this comment")

            await uow.comments_repo.delete(comment_id)
