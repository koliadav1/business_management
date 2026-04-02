from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии бд
    """
    async with session_maker() as session:
        yield session
