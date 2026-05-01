import pytest

from src.core.exceptions import (
    CommentNotFoundError,
    ForbiddenError,
    TaskNotFoundError,
)
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.tasks import Comment, Task
from src.models.users import User
from src.services.comment_service import CommentService


class TestCommentService:

    @pytest.mark.asyncio
    async def test_add_comment_success(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
        mocker,
    ):
        mock_uow.tasks_repo.get.return_value = mock_task

        expected_comment = mocker.MagicMock(spec=Comment)
        expected_comment.id = 1001
        mock_uow.comments_repo.add.return_value = expected_comment

        result = await comment_service.add_comment(
            mock_task.id, "asd", admin_user, mock_uow
        )

        assert result == expected_comment
        mock_uow.comments_repo.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_comment_task_not_found(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        mock_uow.tasks_repo.get.return_value = None
        with pytest.raises(TaskNotFoundError):
            await comment_service.add_comment(
                999, "asda", admin_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_add_comment_forbidden(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_task: Task,
    ):
        mock_uow.tasks_repo.get.retun_value = mock_task
        mock_task.executor_id = 99
        with pytest.raises(
            ForbiddenError, match="You don't have access to this task"
        ):
            await comment_service.add_comment(
                mock_task.id, "asd", employee_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_get_task_comments_success(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
        mocker,
    ):
        expected_comments = [mocker.MagicMock(spec=Comment) for _ in range(5)]

        mock_uow.tasks_repo.get.return_value = mock_task
        mock_uow.comments_repo.get_by_task.return_value = expected_comments

        result = await comment_service.get_task_comments(
            mock_task.id, admin_user, mock_uow
        )

        assert result == expected_comments
        mock_uow.comments_repo.get_by_task.assert_called_once_with(
            mock_task.id
        )

    @pytest.mark.asyncio
    async def test_get_task_comments_not_found(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        mock_uow.tasks_repo.get.return_value = None
        with pytest.raises(TaskNotFoundError):
            await comment_service.get_task_comments(999, admin_user, mock_uow)

    @pytest.mark.asyncio
    async def test_get_task_comments_forbidden(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_task: Task,
    ):
        mock_uow.tasks_repo.get.retun_value = mock_task
        mock_task.executor_id = 99
        with pytest.raises(
            ForbiddenError, match="You don't have access to this task"
        ):
            await comment_service.get_task_comments(
                mock_task.id, employee_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_update_comment_success(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_comment: Comment,
    ):
        mock_comment.author_id = 99
        mock_uow.comments_repo.get.return_value = mock_comment
        mock_uow.comments_repo.update.return_value = mock_comment

        result = await comment_service.update_comment(
            mock_comment.id, "erqr", admin_user, mock_uow
        )

        assert result == mock_comment
        mock_uow.comments_repo.update.assert_called_once_with(mock_comment)

    @pytest.mark.asyncio
    async def test_update_comment_not_found(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        mock_uow.comments_repo.get.return_value = None
        with pytest.raises(CommentNotFoundError):
            await comment_service.update_comment(
                99, "asd", admin_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_update_comment_forbidden(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_comment: Comment,
    ):
        mock_uow.comments_repo.get.return_value = mock_comment
        with pytest.raises(
            ForbiddenError, match="You can't edit this comment"
        ):
            await comment_service.update_comment(
                mock_comment.id, "asd", employee_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_delete_comment_success(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_comment: Comment,
    ):
        mock_uow.comments_repo.get.return_value = mock_comment

        await comment_service.delete_comment(
            mock_comment.id, admin_user, mock_uow
        )

        mock_uow.comments_repo.delete.assert_called_once_with(mock_comment.id)

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        mock_uow.comments_repo.get.return_value = None
        with pytest.raises(CommentNotFoundError):
            await comment_service.delete_comment(99, admin_user, mock_uow)

    @pytest.mark.asyncio
    async def test_delete_comment_forbidden(
        self,
        comment_service: CommentService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_comment: Comment,
    ):
        mock_uow.comments_repo.get.return_value = mock_comment
        with pytest.raises(
            ForbiddenError, match="You can't edit this comment"
        ):
            await comment_service.delete_comment(
                mock_comment.id, employee_user, mock_uow
            )
