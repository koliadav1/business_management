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
        self.session = self._session_factory()

        self.tasks_repo = TasksRepository(self.session)
        self.users_repo = UsersRepository(self.session)
        self.teams_repo = TeamsRepository(self.session)
        self.evaluations_repo = EvaluationsRepository(self.session)
        self.meetings_repo = MeetingsRepository(self.session)
        self.comments_repo = CommentsRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()
            self.session = None
