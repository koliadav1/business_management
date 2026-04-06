from abc import ABC, abstractmethod


class IUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass
