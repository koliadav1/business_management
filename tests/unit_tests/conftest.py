import pytest_asyncio

from src.models.users import User, UserRole
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
def admin_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 1
    user.team_id = 10
    user.role = UserRole.ADMIN

    return user


@pytest_asyncio.fixture
def regular_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 2
    user.team_id = None
    user.role = UserRole.USER

    return user


@pytest_asyncio.fixture
def employee_user(mocker):
    user = mocker.MagicMock(spec=User)

    user.id = 3
    user.team_id = 10
    user.role = UserRole.EMPLOYEE

    return user
