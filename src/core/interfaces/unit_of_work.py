from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces.repositories import (
    ITeamsRepository,
    IUsersRepository,
    ITasksRepository,
    IMeetingsRepository,
    IEvaluationsRepository,
    ICommentsRepository,
)


class IUnitOfWork(ABC):
    session: AsyncSession
    tasks_repo: ITasksRepository
    users_repo: IUsersRepository
    teams_repo: ITeamsRepository
    evaluations_repo: IEvaluationsRepository
    meetings_repo: IMeetingsRepository
    comments_repo: ICommentsRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass
