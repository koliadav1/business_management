from abc import abstractmethod
from datetime import datetime
from typing import List

from src.models.users import User
from src.models.meetings import Meeting
from .base_repository import IRepository


class IMeetingsRepository(IRepository[Meeting]):
    @abstractmethod
    async def get_meeting_with_members(
        self, meeting_id: int
    ) -> Meeting | None:
        """Получить встречу по ее ID со всеми участниками"""
        pass

    @abstractmethod
    async def get_user_meetings(
        self,
        user_id: int,
        include_cancelled: bool = False,
        include_inprogress: bool = True,
    ) -> List[Meeting]:
        """Получить все встречи пользователя"""
        pass

    @abstractmethod
    async def get_team_meetings(
        self,
        team_id: int,
        include_cancelled: bool = False,
        include_finished: bool = True,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> List[Meeting]:
        """Получить встречи команды"""
        pass

    @abstractmethod
    async def check_overlapping(
        self,
        user_ids: List[int],
        start_time: datetime,
        duration_m: int,
        exclude_meeting_id: int | None = None,
    ) -> List[int]:
        """
        Проверка на пересечение встречи с другими.
        exclude_meeting_id для исключения встречи при ее переносе
        """
        pass

    @abstractmethod
    async def cancel_meeting(self, meeting: Meeting) -> Meeting | None:
        """Отменить задачу"""
        pass

    @abstractmethod
    async def get_upcoming_meetings(
        self, user_id: int, minutes_ahead: int = 60
    ) -> List[Meeting]:
        """Получить ближайшие встречи пользователя"""
        pass

    @abstractmethod
    async def get_meeting_members(self, meeting_id: int) -> List[User]:
        """Получить всех участников встречи"""
        pass

    @abstractmethod
    async def remove_member_from_meeting(
        self, meeting: Meeting, member: User
    ) -> Meeting:
        """Удалить участника из встречи"""
        pass

    @abstractmethod
    async def add_members_to_meeting(
        self, meeting: Meeting, user_ids: List[int]
    ) -> Meeting:
        """Добавить участников к встрече"""
        pass

    @abstractmethod
    async def is_member(self, meeting_id: int, user_id: int) -> bool:
        """Является ли пользователь участником встречи"""
        pass
