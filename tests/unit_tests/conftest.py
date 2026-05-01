from datetime import datetime, timezone

import pytest_asyncio

from src.models.evaluations import Evaluation
from src.models.tasks import Task, TaskStatus
from src.models.users import User, UserRole
from src.services.evaluation_service import EvaluationService
from src.services.task_service import TaskService
from src.services.team_service import TeamService


@pytest_asyncio.fixture()
def mock_uow(mocker):
    mock_session = mocker.AsyncMock(name="MockSession")

    uow = mocker.AsyncMock(name="MockUoW")

    uow.session = mock_session

    uow.tasks_repo = mocker.AsyncMock(name="TasksRepo")
    uow.users_repo = mocker.AsyncMock(name="UsersRepo")
    uow.teams_repo = mocker.AsyncMock(name="TeamsRepo")
    uow.evaluations_repo = mocker.AsyncMock(name="EvaluationsRepo")
    uow.meetings_repo = mocker.AsyncMock(name="MeetingsRepo")
    uow.comments_repo = mocker.AsyncMock(name="CommentsRepo")

    uow.__aenter__.return_value = uow

    return uow


@pytest_asyncio.fixture
def team_service():
    return TeamService()


@pytest_asyncio.fixture
def task_service():
    return TaskService()


@pytest_asyncio.fixture
def evaluation_service():
    return EvaluationService()


@pytest_asyncio.fixture
def admin_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 1
    user.team_id = 10
    user.role = UserRole.ADMIN
    user.email = "admin@example.com"

    return user


@pytest_asyncio.fixture
def regular_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 2
    user.team_id = None
    user.role = UserRole.USER
    user.email = "user@example.com"

    return user


@pytest_asyncio.fixture
def employee_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 3
    user.team_id = 10
    user.role = UserRole.EMPLOYEE
    user.email = "employee@example.com"

    return user


@pytest_asyncio.fixture
def another_employee_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 4
    user.team_id = 10
    user.role = UserRole.EMPLOYEE
    user.email = "employee1@example.com"

    return user


@pytest_asyncio.fixture
def manager_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 5
    user.team_id = 10
    user.role = UserRole.MANAGER
    user.email = "manager@example.com"

    return user


@pytest_asyncio.fixture
def another_manager_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 6
    user.team_id = 10
    user.role = UserRole.MANAGER
    user.email = "manager1@example.com"

    return user


@pytest_asyncio.fixture
def mock_task(manager_user, employee_user, mocker):
    task = mocker.MagicMock(spec=Task)
    task.id = 100
    task.description = "Test"
    task.deadline = datetime.now(timezone.utc)
    task.executor_id = employee_user.id
    task.author_id = manager_user.id
    task.team_id = manager_user.team_id
    task.status = TaskStatus.NEW
    task.completed_at = None
    task.comments = None
    task.evaluation = None

    return task


@pytest_asyncio.fixture
def mock_task_done(manager_user, employee_user, mocker):
    task = mocker.MagicMock(spec=Task)
    task.id = 100
    task.description = "Test"
    task.deadline = datetime.now(timezone.utc)
    task.executor_id = employee_user.id
    task.author_id = manager_user.id
    task.team_id = manager_user.team_id
    task.status = TaskStatus.DONE
    task.completed_at = None
    task.comments = None
    task.evaluation = None

    return task


@pytest_asyncio.fixture
def mock_evaluation(mock_task_done, manager_user, mocker):
    evaluation = mocker.MagicMock(spec=Evaluation)
    evaluation.id = 1000
    evaluation.comment = "Test comm"
    evaluation.task_id = mock_task_done.id
    evaluation.rating = 5
    evaluation.rater_id = manager_user.id

    return evaluation
