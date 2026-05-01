from datetime import datetime, timedelta, timezone
import pytest

from src.core.exceptions import ForbiddenError, InvalidTransitionError
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.tasks import Task, TaskStatus
from src.models.users import User
from src.services.task_service import TaskService


class TestTaskService:

    @pytest.mark.asyncio
    async def test_create_task_succsess(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        employee_user: User,
        mocker,
    ):
        expected_task = mocker.MagicMock(spec=Task)
        expected_task.id = 200
        mock_uow.tasks_repo.add.return_value = expected_task

        mock_uow.users_repo.get.return_value = employee_user

        result = await task_service.create_task(
            "Test task",
            datetime.now(timezone.utc),
            employee_user.id,
            admin_user,
            mock_uow,
        )

        assert result == expected_task
        mock_uow.tasks_repo.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_wrong_role(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        manager_user: User,
        employee_user: User,
    ):
        mock_uow.users_repo.get.return_value = manager_user
        with pytest.raises(
            ForbiddenError, match="Only admins and managers can create tasks"
        ):
            await task_service.create_task(
                "asd",
                datetime.now(timezone.utc),
                manager_user.id,
                employee_user,
                mock_uow,
            )

    @pytest.mark.asyncio
    async def test_create_task_two_managers(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        manager_user: User,
        another_manager_user: User,
    ):
        mock_uow.users_repo.get.return_value = manager_user
        with pytest.raises(
            ForbiddenError,
            match="Managers can't assign other managers to tasks",
        ):
            await task_service.create_task(
                "asd",
                datetime.now(timezone.utc),
                manager_user.id,
                another_manager_user,
                mock_uow,
            )

    @pytest.mark.asyncio
    async def test_assign_executor_by_admin_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        manager_user: User,
        mock_task: Task,
    ):
        mock_uow.users_repo.get.return_value = manager_user
        mock_uow.tasks_repo.get.return_value = mock_task
        mock_uow.tasks_repo.update.return_value = mock_task

        result = await task_service.assign_executor(
            mock_task.id, manager_user.id, admin_user, mock_uow
        )

        assert result == mock_task
        assert mock_task.executor_id == manager_user.id
        mock_uow.tasks_repo.update.assert_called_once_with(mock_task)

    @pytest.mark.asyncio
    async def test_assign_executor_by_author_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        manager_user: User,
        another_employee_user: User,
        mock_task: Task,
    ):
        mock_uow.users_repo.get.return_value = another_employee_user
        mock_uow.tasks_repo.get.return_value = mock_task
        mock_uow.tasks_repo.update.return_value = mock_task

        result = await task_service.assign_executor(
            mock_task.id, another_employee_user.id, manager_user, mock_uow
        )

        assert result == mock_task
        assert mock_task.executor_id == another_employee_user.id
        mock_uow.tasks_repo.update.assert_called_once_with(mock_task)

    @pytest.mark.asyncio
    async def test_assign_executor_wrong_role(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        another_employee_user: User,
        mock_task: Task,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can assign executors",
        ):
            await task_service.assign_executor(
                mock_task.id, another_employee_user.id, employee_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_update_task_succcess(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
    ):
        description = "Test 123"
        deadline = datetime.now(timezone.utc)

        mock_uow.tasks_repo.get.return_value = mock_task
        mock_uow.tasks_repo.update.return_value = mock_task

        result = await task_service.update_task(
            mock_task.id, admin_user, mock_uow, description, deadline
        )

        assert result == mock_task
        assert result.deadline == deadline
        assert result.description == description

    @pytest.mark.asyncio
    async def test_update_task_cancelled(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
    ):
        mock_task.status = TaskStatus.CANCELLED
        mock_uow.tasks_repo.get.return_value = mock_task

        with pytest.raises(
            ForbiddenError, match="You can't update cancelled or done tasks"
        ):
            await task_service.update_task(mock_task.id, admin_user, mock_uow)

    @pytest.mark.asyncio
    async def test_delete_task_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
    ):
        mock_uow.tasks_repo.get.return_value = mock_task

        await task_service.delete_task(mock_task.id, admin_user, mock_uow)

        mock_uow.tasks_repo.delete.assert_called_once_with(mock_task.id)

    @pytest.mark.asyncio
    async def test_change_status__by_admin_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
    ):
        status = TaskStatus.IN_PROGRESS
        mock_uow.tasks_repo.get.return_value = mock_task
        mock_uow.tasks_repo.update.return_value = mock_task

        result = await task_service.change_status(
            mock_task.id, status, admin_user, mock_uow
        )

        assert result == mock_task
        assert mock_task.status == status

    @pytest.mark.asyncio
    async def test_change_status_by_executor_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_task: Task,
    ):
        status = TaskStatus.IN_PROGRESS
        mock_uow.tasks_repo.get.return_value = mock_task
        mock_uow.tasks_repo.update.return_value = mock_task

        result = await task_service.change_status(
            mock_task.id, status, employee_user, mock_uow
        )

        assert result == mock_task
        assert mock_task.status == status

    @pytest.mark.asyncio
    async def test_change_status_invalid_transition(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
    ):
        mock_task.status = TaskStatus.CANCELLED
        mock_uow.tasks_repo.get.return_value = mock_task

        with pytest.raises(InvalidTransitionError):
            await task_service.change_status(
                mock_task.id, TaskStatus.DONE, admin_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_change_status_by_executor_forbidden(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_task: Task,
    ):
        mock_uow.tasks_repo.get.return_value = mock_task

        with pytest.raises(ForbiddenError):
            await task_service.change_status(
                mock_task.id, TaskStatus.CANCELLED, employee_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_get_task_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_task: Task,
    ):
        mock_uow.tasks_repo.get_task_with_comments.return_value = mock_task

        result = await task_service.get_task(
            mock_task.id, admin_user, mock_uow
        )

        assert result == mock_task

    @pytest.mark.asyncio
    async def test_get_task_forbidden(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        regular_user: User,
        mock_task: Task,
    ):
        mock_uow.tasks_repo.get_task_with_comments.return_value = mock_task

        with pytest.raises(ForbiddenError):
            await task_service.get_task(mock_task.id, regular_user, mock_uow)

    @pytest.mark.asyncio
    async def test_get_user_tasks_as_self(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 20
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.tasks_repo.get_by_executor.return_value = (expected_tasks, 5)

        result = await task_service.get_user_tasks(
            mock_uow, employee_user, page, limit
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.tasks_repo.get_by_executor.assert_called_once_with(
            employee_user.id, employee_user.team_id, 0, limit, None, None, None
        )

    @pytest.mark.asyncio
    async def test_get_user_tasks_as_admin_for_other(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 20
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.tasks_repo.get_by_executor.return_value = (expected_tasks, 5)

        result = await task_service.get_user_tasks(
            mock_uow, admin_user, page, limit, user_id=employee_user.id
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.tasks_repo.get_by_executor.assert_called_once_with(
            employee_user.id, employee_user.team_id, 0, limit, None, None, None
        )

    @pytest.mark.asyncio
    async def test_get_user_tasks_forbidden(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        manager_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can view other user's tasks",
        ):
            await task_service.get_user_tasks(
                mock_uow, employee_user, 1, 1, user_id=manager_user.id
            )

    @pytest.mark.asyncio
    async def test_get_user_tasks_filters(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        page, limit = 1, 20
        deadline_from = datetime.now(timezone.utc)
        deadline_to = deadline_from + timedelta(days=30)
        status = TaskStatus.DONE
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.tasks_repo.get_by_executor.return_value = (expected_tasks, 5)

        result = await task_service.get_user_tasks(
            mock_uow,
            admin_user,
            page,
            limit,
            status=status,
            deadline_from=deadline_from,
            deadline_to=deadline_to,
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.tasks_repo.get_by_executor.assert_called_once_with(
            admin_user.id,
            admin_user.team_id,
            0,
            limit,
            status,
            deadline_from,
            deadline_to,
        )

    @pytest.mark.asyncio
    async def test_get_team_tasks_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        page, limit = 1, 20
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.tasks_repo.get_by_team.return_value = (expected_tasks, 5)

        result = await task_service.get_team_tasks(
            mock_uow, admin_user, page, limit
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.tasks_repo.get_by_team.assert_called_once_with(
            admin_user.team_id, 0, limit, None, None, None
        )

    @pytest.mark.asyncio
    async def test_get_team_tasks_forbidden(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        regular_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can view team tasks",
        ):
            await task_service.get_team_tasks(mock_uow, regular_user, 1, 1)

    @pytest.mark.asyncio
    async def test_get_user_overdue_tasks_as_self(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 20
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.tasks_repo.get_overdue_for_user.return_value = (
            expected_tasks,
            5,
        )

        result = await task_service.get_user_overdue_tasks(
            employee_user, mock_uow, page, limit
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.tasks_repo.get_overdue_for_user.assert_called_once_with(
            employee_user.id, employee_user.team_id, 0, limit
        )

    @pytest.mark.asyncio
    async def test_get_user_overdue_tasks_as_admin_for_other(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 20
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.tasks_repo.get_overdue_for_user.return_value = (
            expected_tasks,
            5,
        )

        result = await task_service.get_user_overdue_tasks(
            admin_user, mock_uow, page, limit, user_id=employee_user.id
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.tasks_repo.get_overdue_for_user.assert_called_once_with(
            employee_user.id, employee_user.team_id, 0, limit
        )

    @pytest.mark.asyncio
    async def test_get_user_overdue_tasks_forbidden(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        manager_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can view other user's tasks",
        ):
            await task_service.get_user_overdue_tasks(
                employee_user, mock_uow, 1, 1, user_id=manager_user.id
            )

    @pytest.mark.asyncio
    async def test_get_team_verdue_tasks_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        page, limit = 1, 20
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.tasks_repo.get_overdue_for_team.return_value = (
            expected_tasks,
            5,
        )

        result = await task_service.get_team_overdue_tasks(
            admin_user, mock_uow, page, limit
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.tasks_repo.get_overdue_for_team.assert_called_once_with(
            admin_user.team_id, 0, limit
        )

    @pytest.mark.asyncio
    async def test_get_team_overdue_tasks_forbidden(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        regular_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can view team tasks",
        ):
            await task_service.get_team_overdue_tasks(
                regular_user, mock_uow, 1, 1
            )

    @pytest.mark.asyncio
    async def test_get_done_tasks_with_evaluations_success(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        manager_user: User,
        mocker,
    ):
        page, limit = 1, 20
        expected_tasks = [mocker.MagicMock(spec=Task) for _ in range(5)]
        mock_uow.evaluations_repo.get_done_tasks_with_evaluations.return_value = (
            expected_tasks,
            5,
        )

        result = await task_service.get_done_tasks_with_evaluations(
            mock_uow, manager_user, page, limit
        )

        assert result["items"] == expected_tasks
        assert result["total"] == 5
        assert result["page"] == page
        assert result["page_size"] == limit
        mock_uow.evaluations_repo.get_done_tasks_with_evaluations.assert_called_once_with(
            manager_user.team_id, 0, limit
        )

    @pytest.mark.asyncio
    async def test_get_done_tasks_with_evaluations_forbidden(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        employee_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can view other user's evaluations",
        ):
            await task_service.get_done_tasks_with_evaluations(
                mock_uow, employee_user, 1, 1
            )

    @pytest.mark.asyncio
    async def test_get_done_tasks_with_evaluations_not_in_team(
        self,
        task_service: TaskService,
        mock_uow: IUnitOfWork,
        regular_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="You are not in the team",
        ):
            await task_service.get_done_tasks_with_evaluations(
                mock_uow, regular_user, 1, 1
            )
