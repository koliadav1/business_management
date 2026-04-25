from sqlalchemy.ext.asyncio import async_sessionmaker

from . import (
    MeetingsRepository,
    EvaluationsRepository,
    TeamsRepository,
    TasksRepository,
    UsersRepository,
    CommentsRepository,
)
from src.core.interfaces.unit_of_work import IUnitOfWork


class SQLAlchUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory()

        self.tasks_repo = TasksRepository(self._session)
        self.users_repo = UsersRepository(self._session)
        self.teams_repo = TeamsRepository(self._session)
        self.evaluations_repo = EvaluationsRepository(self._session)
        self.meetings_repo = MeetingsRepository(self._session)
        self.comments_repo = CommentsRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.close()
            self._session = None
