from datetime import datetime, timedelta
from typing import List

from sqlalchemy import exists, func, select
from sqlalchemy.orm import selectinload

from src.models.users import User
from src.models.meetings import Meeting
from .base_repository import SQLRepository
from src.core.interfaces.repositories.meetings_repository import (
    IMeetingsRepository,
)


class MeetingsRepository(SQLRepository[Meeting], IMeetingsRepository):
    def __init__(self, session):
        super().__init__(session, Meeting)

    async def get_meeting_with_members(
        self, meeting_id: int
    ) -> Meeting | None:
        """Получить встречу по ее ID со всеми участниками"""
        result = await self._session.execute(
            select(Meeting)
            .where(Meeting.id == meeting_id)
            .options(
                selectinload(Meeting.initiator),
                selectinload(Meeting.members),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_meetings(
        self,
        user_id: int,
        include_cancelled: bool = False,
        include_finished: bool = True,
    ) -> List[Meeting]:
        """Получить все встречи пользователя"""
        query = select(Meeting).join(Meeting.members).where(User.id == user_id)

        if not include_cancelled:
            query = query.where(Meeting.is_active)

        if not include_finished:
            query = query.where(Meeting.start_time > func.now())

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_team_meetings(
        self,
        team_id: int,
        include_cancelled: bool = False,
        include_finished: bool = True,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> List[Meeting]:
        """Получить встречи команды"""
        query = select(Meeting).where(Meeting.team_id == team_id)

        if not include_cancelled:
            query = query.where(Meeting.is_active)

        if not include_finished:
            query = query.where(Meeting.start_time > func.now())

        if start_date:
            query = query.where(Meeting.start_time >= start_date)

        if end_date:
            query = query.where(Meeting.start_time <= end_date)

        result = await self._session.execute(query)
        return result.scalars().all()

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
        end_time = start_time + timedelta(minutes=duration_m)

        query = (
            select(User.id)
            .where(User.id.in_(user_ids))
            .where(
                User.meetings.any(
                    Meeting.is_active,
                    Meeting.start_time < end_time,
                    Meeting.start_time
                    + (Meeting.duration_m * func.text("interval '1 minute'"))
                    > start_time,
                    Meeting.id != exclude_meeting_id,
                )
            )
        )

        result = await self._session.execute(query)
        return [row for row in result.scalars()]

    async def cancel_meeting(self, meeting: Meeting) -> Meeting | None:
        """Отменить задачу"""
        meeting.is_active = False
        await self._session.flush()

        return meeting

    async def get_upcoming_meetings(
        self, user_id: int, minutes_ahead: int = 60
    ) -> List[Meeting]:
        """Получить ближайшие встречи пользователя"""
        now = datetime.now()
        future_time = now + timedelta(minutes=minutes_ahead)

        query = (
            select(Meeting)
            .join(Meeting.members)
            .where(
                User.id == user_id,
                Meeting.is_active,
                Meeting.start_time >= now,
                Meeting.start_time <= future_time,
            )
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_meeting_members(self, meeting_id: int) -> List[User]:
        """Получить всех участников встречи"""
        query = (
            select(User).join(User.meetings).where(Meeting.id == meeting_id)
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def remove_member_from_meeting(
        self, meeting: Meeting, member: User
    ) -> Meeting:
        """Удалить участника из встречи"""
        meeting.members.remove(member)
        await self._session.flush()
        return meeting

    async def add_members_to_meeting(
        self, meeting: Meeting, user_ids: List[int]
    ) -> Meeting:
        """Добавить участников к встрече"""
        result = await self._session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        new_members = result.scalars().all()

        for user in new_members:
            if user not in meeting.members:
                meeting.members.append(user)

        await self._session.flush()
        return meeting

    async def is_member(self, meeting_id: int, user_id: int) -> bool:
        """Является ли пользователь участником встречи"""
        result = await self._session.execute(
            select(
                exists().where(
                    Meeting.id == meeting_id,
                    Meeting.members.any(User.id == user_id),
                )
            )
        )
        return result.scalar() or False
