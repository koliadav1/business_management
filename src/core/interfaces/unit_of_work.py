from abc import ABC, abstractmethod

from src.core.interfaces.repositories import (
    ITeamsRepository,
    IUsersRepository,
    ITasksRepository,
    IMeetingsRepository,
    IEvaluationsRepository,
)


class IUnitOfWork(ABC):
    tasks_repo: ITasksRepository
    users_repo: IUsersRepository
    teams_repo: ITeamsRepository
    evaluations_repo: IEvaluationsRepository
    meetings_repo: IMeetingsRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass
