from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.core.database import session_maker
from src.services.user_manager import UserManager
from src.repositories.unit_of_work import SQLAlchUnitOfWork


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


async def get_sql_uow():
    return SQLAlchUnitOfWork(session_maker)
