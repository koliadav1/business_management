import os

os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_DB"] = "db_test"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "1"

from sqlalchemy import NullPool
from typing import AsyncGenerator
from passlib.context import CryptContext
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.models.teams import Team
from src.core.database import Base
from src.main import app
from src.models.users import User, UserRole
from src.repositories.unit_of_work import SQLAlchUnitOfWork
from src.utils.dependencies import get_db_session, get_uow
from src.core.config import settings


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        settings.DB_URL, echo=False, poolclass=NullPool
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as conn:
        session_factory = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:

            async def override_get_db_session():
                return session

            app.dependency_overrides[get_db_session] = override_get_db_session
            try:
                yield session
            finally:
                await session.rollback()
                await session.close()
                app.dependency_overrides.pop(override_get_db_session, None)

                async with test_engine.begin() as clean_conn:
                    for table in reversed(Base.metadata.sorted_tables):
                        await clean_conn.execute(table.delete())


@pytest_asyncio.fixture(scope="function")
async def uow(db_session: AsyncSession):
    class MockUOW(SQLAlchUnitOfWork):
        def __init__(self, session):
            self._session_factory = lambda: session
            super().__init__(self._session_factory)

    uow = MockUOW(db_session)

    async def override_get_uow():
        return uow

    app.dependency_overrides[get_uow] = override_get_uow

    try:
        yield uow
    finally:
        app.dependency_overrides.pop(get_uow, None)


@pytest_asyncio.fixture(scope="function")
async def client(db_session, uow):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": test_user.plain_password,
        },
    )
    tokens = response.json()
    return {
        "Authorization": f"Bearer {tokens["access_token"]}",
        "X-Refresh-Token": tokens["refresh_token"],
    }


@pytest_asyncio.fixture(scope="function")
async def admin_auth_headers(client, test_team_with_members):
    admin = test_team_with_members["admin"]
    response = await client.post(
        "/auth/login",
        data={
            "username": admin.email,
            "password": admin.plain_password,
        },
    )
    tokens = response.json()
    return {
        "Authorization": f"Bearer {tokens["access_token"]}",
        "X-Refresh-Token": tokens["refresh_token"],
    }


@pytest_asyncio.fixture(scope="function")
async def manager_auth_headers(client, test_team_with_members):
    manager = test_team_with_members["manager"]
    response = await client.post(
        "/auth/login",
        data={
            "username": manager.email,
            "password": manager.plain_password,
        },
    )
    tokens = response.json()
    return {
        "Authorization": f"Bearer {tokens["access_token"]}",
        "X-Refresh-Token": tokens["refresh_token"],
    }


@pytest_asyncio.fixture(scope="function")
async def employee_auth_headers(client, test_team_with_members):
    employee = test_team_with_members["employee"]
    response = await client.post(
        "/auth/login",
        data={
            "username": employee.email,
            "password": employee.plain_password,
        },
    )
    tokens = response.json()
    return {
        "Authorization": f"Bearer {tokens["access_token"]}",
        "X-Refresh-Token": tokens["refresh_token"],
    }


# Фикстуры с данными


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        email="user@test.com",
        hashed_password=pwd_context.hash("TestPass123"),
        role=UserRole.USER,
        name="Test",
        surname="asds",
    )

    db_session.add(user)
    await db_session.flush()

    user.plain_password = "TestPass123"

    yield user


@pytest_asyncio.fixture(scope="function")
async def test_team(
    db_session,
):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    user = User(
        email="admin@test.com",
        hashed_password=pwd_context.hash("admin123"),
        role=UserRole.USER,
        team_id=None,
    )

    db_session.add(user)
    await db_session.flush()

    user.plain_password = "admin123"

    team = Team(
        name="Test team",
        description="test",
        invite_code=Team.generate_invite_code(),
    )
    db_session.add(team)
    await db_session.flush()
    user.team_id = team.id
    user.role = UserRole.ADMIN
    await db_session.flush()

    yield {"admin": user, "team": team}


@pytest_asyncio.fixture(scope="function")
async def test_team_with_members(db_session, test_team):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    manager = User(
        email="manager@test.com",
        hashed_password=pwd_context.hash("manager123"),
        role=UserRole.MANAGER,
        team_id=test_team["team"].id,
    )
    employee = User(
        email="employee@test.com",
        hashed_password=pwd_context.hash("employee123"),
        role=UserRole.EMPLOYEE,
        team_id=test_team["team"].id,
    )
    another_employee = User(
        email="employee1@test.com",
        hashed_password=pwd_context.hash("employee123"),
        role=UserRole.EMPLOYEE,
        team_id=test_team["team"].id,
    )

    db_session.add_all([manager, employee, another_employee])
    await db_session.flush()

    manager.plain_password = "manager123"
    employee.plain_password = "employee123"
    another_employee.plain_password = "employee123"

    return {
        "team": test_team["team"],
        "admin": test_team["admin"],
        "manager": manager,
        "employee": employee,
        "another_employee": another_employee,
    }
