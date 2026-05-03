from datetime import datetime, timedelta, timezone

import pytest

from src.core.exceptions import ForbiddenError, TaskNotCompletedError
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.evaluations import Evaluation
from src.models.tasks import Task
from src.models.users import User
from src.services.evaluation_service import EvaluationService


class TestEvaluationService:
    @pytest.mark.asyncio
    async def test_rate_task_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        manager_user: User,
        mock_task_done: Task,
        mocker,
    ):
        mock_uow.evaluations_repo.get_by_task.return_value = None
        mock_uow.tasks_repo.get.return_value = mock_task_done

        expected_evaluation = mocker.MagicMock(spec=Evaluation)
        mock_uow.evaluations_repo.add.return_value = expected_evaluation

        result = await evaluation_service.rate_task(
            mock_task_done.id, 5, manager_user, mock_uow, "test"
        )

        assert result == expected_evaluation
        mock_uow.evaluations_repo.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_rate_task_update_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        manager_user: User,
        mock_task_done: Task,
        mock_evaluation: Evaluation,
    ):
        mock_uow.tasks_repo.get.return_value = mock_task_done
        mock_uow.evaluations_repo.get_by_task.return_value = mock_evaluation
        mock_uow.evaluations_repo.update.return_value = mock_evaluation

        result = await evaluation_service.rate_task(
            mock_task_done.id, 4, manager_user, mock_uow, "test123"
        )

        assert result == mock_evaluation
        mock_uow.evaluations_repo.update.assert_called_once_with(
            mock_evaluation
        )
        mock_uow.evaluations_repo.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_task_forbidden(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_task_done: Task,
    ):
        with pytest.raises(
            ForbiddenError, match="Only admins and managers can rate tasks"
        ):
            await evaluation_service.rate_task(
                mock_task_done.id, 3, employee_user, mock_uow, "asd"
            )

    @pytest.mark.asyncio
    async def test_rate_task_not_completed(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        manager_user: User,
        mock_task: Task,
    ):
        mock_uow.tasks_repo.get.return_value = mock_task
        with pytest.raises(TaskNotCompletedError):
            await evaluation_service.rate_task(
                mock_task.id, 4, manager_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_get_evaluations_team_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        page, limit = 1, 10
        expected_evaluations = [
            mocker.MagicMock(spec=Evaluation) for _ in range(5)
        ]
        mock_uow.evaluations_repo.get_by_team.return_value = (
            expected_evaluations,
            5,
        )

        result = await evaluation_service.get_evaluations(
            admin_user, mock_uow, page, limit
        )

        assert result["items"] == expected_evaluations
        assert result["total"] == 5
        assert result["page"] == 1
        assert result["page_size"] == 10
        mock_uow.evaluations_repo.get_by_team.assert_called_once_with(
            admin_user.team_id, 0, limit
        )

    @pytest.mark.asyncio
    async def test_get_evaluations_for_user_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 10
        expected_evaluations = [
            mocker.MagicMock(spec=Evaluation) for _ in range(5)
        ]
        mock_uow.evaluations_repo.get_user_evaluations.return_value = (
            expected_evaluations,
            5,
        )

        result = await evaluation_service.get_evaluations(
            admin_user, mock_uow, page, limit, employee_user.id
        )

        assert result["items"] == expected_evaluations
        assert result["total"] == 5
        assert result["page"] == 1
        assert result["page_size"] == 10
        mock_uow.evaluations_repo.get_user_evaluations.assert_called_once_with(
            employee_user.id, 0, limit, admin_user.team_id
        )

    @pytest.mark.asyncio
    async def test_get_evaluations_as_employee_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 10
        expected_evaluations = [
            mocker.MagicMock(spec=Evaluation) for _ in range(5)
        ]
        mock_uow.evaluations_repo.get_user_evaluations.return_value = (
            expected_evaluations,
            5,
        )

        result = await evaluation_service.get_evaluations(
            employee_user, mock_uow, page, limit
        )

        assert result["items"] == expected_evaluations
        assert result["total"] == 5
        assert result["page"] == 1
        assert result["page_size"] == 10
        mock_uow.evaluations_repo.get_user_evaluations.assert_called_once_with(
            employee_user.id, 0, limit, employee_user.team_id
        )

    @pytest.mark.asyncio
    async def test_get_evaluations_with_tasks_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 10
        expected_items = [
            (mocker.MagicMock(spec=Evaluation), mocker.MagicMock(spec=Task))
            for _ in range(5)
        ]
        mock_uow.evaluations_repo.get_evaluations_with_tasks.return_value = (
            expected_items,
            5,
        )

        result = await evaluation_service.get_evaluations_with_tasks(
            mock_uow, admin_user, page, limit, employee_user.id
        )

        assert result["items"] == expected_items
        assert result["total"] == 5
        assert result["page"] == 1
        assert result["page_size"] == 10
        mock_uow.evaluations_repo.get_evaluations_with_tasks.assert_called_once_with(
            employee_user.id, admin_user.team_id, 0, limit
        )

    @pytest.mark.asyncio
    async def test_get_evaluations_with_tasks_as_self_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        page, limit = 1, 10
        expected_items = [
            (mocker.MagicMock(spec=Evaluation), mocker.MagicMock(spec=Task))
            for _ in range(5)
        ]
        mock_uow.evaluations_repo.get_evaluations_with_tasks.return_value = (
            expected_items,
            5,
        )

        result = await evaluation_service.get_evaluations_with_tasks(
            mock_uow, employee_user, page, limit
        )

        assert result["items"] == expected_items
        assert result["total"] == 5
        assert result["page"] == 1
        assert result["page_size"] == 10
        mock_uow.evaluations_repo.get_evaluations_with_tasks.assert_called_once_with(
            employee_user.id, employee_user.team_id, 0, limit
        )

    @pytest.mark.asyncio
    async def test_get_evaluations_with_tasks_forbidden(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        manager_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can view other user's evaluations",
        ):
            await evaluation_service.get_evaluations_with_tasks(
                mock_uow, employee_user, 1, 1, manager_user.id
            )

    @pytest.mark.asyncio
    async def test_get_rating_stats_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        manager_user: User,
    ):
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        expected_stats = {
            "total": 5,
            "average": 3.5,
            "distribution": {
                5: 1,
                4: 2,
                3: 3,
                2: 4,
                1: 5,
            },
        }

        mock_uow.users_repo.get.return_value = manager_user
        mock_uow.evaluations_repo.get_statistics.return_value = expected_stats

        result = await evaluation_service.get_rating_stats(
            mock_uow, admin_user, manager_user.id, start_date, end_date
        )

        assert result == expected_stats
        mock_uow.evaluations_repo.get_statistics.assert_called_once_with(
            manager_user.id, admin_user.team_id, start_date, end_date
        )

    @pytest.mark.asyncio
    async def test_get_rating_stats_as_self_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        manager_user: User,
    ):
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        expected_stats = {
            "total": 5,
            "average": 3.5,
            "distribution": {
                5: 1,
                4: 2,
                3: 3,
                2: 4,
                1: 5,
            },
        }

        mock_uow.evaluations_repo.get_statistics.return_value = expected_stats

        result = await evaluation_service.get_rating_stats(
            mock_uow, manager_user, start_date=start_date, end_date=end_date
        )

        assert result == expected_stats
        mock_uow.evaluations_repo.get_statistics.assert_called_once_with(
            manager_user.id, manager_user.team_id, start_date, end_date
        )

    @pytest.mark.asyncio
    async def test_get_rating_stats_no_results(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        manager_user: User,
    ):
        mock_uow.evaluations_repo.get_statistics.return_value = None

        result = await evaluation_service.get_rating_stats(
            mock_uow, manager_user
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_evaluation_success(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_evaluation: Evaluation,
        mock_task_done: Task,
    ):
        mock_uow.tasks_repo.get.return_value = mock_task_done
        mock_uow.evaluations_repo.get_by_task.return_value = mock_evaluation

        await evaluation_service.delete_evaluation(
            mock_task_done.id, mock_uow, admin_user
        )

        mock_uow.evaluations_repo.delete.assert_called_once_with(
            mock_evaluation.id
        )

    @pytest.mark.asyncio
    async def test_delete_evaluation_forbidden(
        self,
        evaluation_service: EvaluationService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_task_done: Task,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can delete evaluations",
        ):
            await evaluation_service.delete_evaluation(
                mock_task_done.id, mock_uow, employee_user
            )
