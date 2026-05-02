import os

os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_DB"] = "db_test"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "1"

from typing import AsyncGenerator

from fastapi_users.db import SQLAlchemyUserDatabase
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.database import Base
from src.main import app
from src.models.users import User
from src.repositories.unit_of_work import SQLAlchUnitOfWork
from src.schemas.users import UserCreate
from src.services.user_manager import UserManager
from src.utils.dependencies import get_db_session, get_uow
from src.core.config import settings


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(settings.DB_URL, echo=False, future=True)
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
    conn = await test_engine.connect()
    transaction = await conn.begin()
    session_factory = async_sessionmaker(
        bind=conn, expire_on_commit=False, class_=AsyncSession
    )
    async with session_factory() as session:

        async def override_get_db_session():
            try:
                yield session
            finally:
                pass

        app.dependency_overrides[get_db_session] = override_get_db_session
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
            await conn.close()

            app.dependency_overrides.pop(get_db_session, None)


@pytest_asyncio.fixture(scope="function")
async def uow(db_session: AsyncSession):

    class MockSessionMaker:
        async def __call__(self, *args, **kwds):
            return db_session

    mock_session_maker = MockSessionMaker()
    uow = SQLAlchUnitOfWork(mock_session_maker)

    async def override_get_uow():
        return uow

    app.dependency_overrides[get_uow] = override_get_uow

    try:
        yield uow
    finally:
        app.dependency_overrides.pop(get_uow, None)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
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
    return {"Authorization": f"Bearer {tokens["access_token"]}"}


# Фикстуры с данными


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    user_db = SQLAlchemyUserDatabase(db_session, User)

    async def get_user_manager():
        return UserManager(user_db)

    user_manager = await get_user_manager()

    user_data = UserCreate(
        email="test@example.com",
        password="TestPass123",
        name="test",
        surname="user",
        phone_number="123123",
    )

    user = await user_manager.create(user_data)

    user.plain_password = "TestPass123"

    yield user
