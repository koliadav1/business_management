from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.core.database import session_maker
from src.services.user_manager import UserManager
from src.repositories.unit_of_work import SQLAlchUnitOfWork
from src.core.config import settings

bearer_transport = BearerTransport(tokenUrl="auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии бд
    """
    async with session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


async def get_uow():
    return SQLAlchUnitOfWork(session_maker)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager=get_user_manager, auth_backends=[auth_backend]
)

get_current_user = fastapi_users.current_user(active=True)
