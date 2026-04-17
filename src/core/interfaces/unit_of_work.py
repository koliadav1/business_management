from abc import ABC, abstractmethod

from src.core.interfaces.repositories.evaluations_repository import (
    IEvaluationsRepository,
)
from src.core.interfaces.repositories.teams_repository import ITeamsRepository
from src.core.interfaces.repositories.users_repository import IUsersRepository
from src.core.interfaces.repositories.tasks_repository import ITasksRepository


class IUnitOfWork(ABC):
    tasks_repo: ITasksRepository
    users_repo: IUsersRepository
    teams_repo: ITeamsRepository
    evaluations_repo: IEvaluationsRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass
