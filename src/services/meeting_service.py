from datetime import datetime, timezone
from typing import List

from .dependencies import CheckTeamLogic
from src.core.exceptions import (
    ForbiddenError,
    MeetingAlreadyOverError,
    MeetingCancelledError,
    MeetingNotFoundError,
    OverlappingTimeError,
    UserNotInTeamError,
)
from src.models.meetings import Meeting
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.users import User, UserRole


class MeetingService:
    async def create_meeting(
        self,
        description: str,
        start_time: datetime,
        duration_m: int,
        member_ids: List[int],
        current_user: User,
        uow: IUnitOfWork,
    ) -> Meeting:
        """
        Создание встречи.
        Только для admin и manager.
        """
        async with uow:
            if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                raise ForbiddenError(
                    "Only admins and managers can create meetings"
                )

            if current_user.team_id is None:
                raise ForbiddenError(
                    "You must be in a team to create meetings"
                )

            meeting = Meeting(
                description=description,
                start_time=start_time,
                duration_m=duration_m,
                initiator_id=current_user.id,
                team_id=current_user.team_id,
            )

            if member_ids:
                invalid_users = await uow.teams_repo.is_members(
                    current_user.team_id, member_ids
                )
                if invalid_users:
                    raise UserNotInTeamError(
                        f"Users with IDs {invalid_users}"
                        " not found or not in your team"
                    )

                overlapping_users = await uow.meetings_repo.check_overlapping(
                    user_ids=member_ids,
                    start_time=start_time,
                    duration_m=duration_m,
                )
                if overlapping_users:
                    raise OverlappingTimeError(
                        f"Users with IDs {overlapping_users} "
                        "have overlapping meetings"
                    )

                created_meeting = await uow.meetings_repo.add(meeting)

                created_meeting = (
                    await uow.meetings_repo.add_members_to_meeting(
                        created_meeting.id, member_ids
                    )
                )
            else:
                created_meeting = await uow.meetings_repo.add(meeting)

        return created_meeting

    async def update_meeting(
        self,
        meeting_id: int,
        description: str | None,
        start_time: datetime | None,
        duration_m: int | None,
        current_user: User,
        uow: IUnitOfWork,
    ) -> Meeting:
        """
        Обновление встречи.
        Только для admin или инициатора встречи
        """
        async with uow:
            meeting = await uow.meetings_repo.get(meeting_id)

            if not meeting:
                raise MeetingNotFoundError(
                    f"Meeting with ID {meeting_id} not found"
                )

            self._check_can_manage_meeting(meeting, current_user)

            old_start_time = meeting.start_time
            old_duration = meeting.duration_m

            if description is not None:
                meeting.description = description

            if start_time is not None:
                meeting.start_time = start_time

            if duration_m is not None:
                meeting.duration_m = duration_m

            if start_time is not None or duration_m is not None:
                time = start_time or old_start_time
                duration = duration_m or old_duration

                member_ids = [member.id for member in meeting.members]

                overlapping_users = await uow.meetings_repo.check_overlapping(
                    member_ids, time, duration, meeting.id
                )
                if overlapping_users:
                    raise OverlappingTimeError(
                        f"Users with IDs {overlapping_users} "
                        "have overlapping meetings"
                    )

            updated_meeting = await uow.meetings_repo.update(meeting)

        return updated_meeting

    async def cancel_meeting(
        self, meeting_id: int, current_user: User, uow: IUnitOfWork
    ) -> Meeting:
        """
        Отмена встречи.
        Только для admin или инициатора встречи
        """
        async with uow:
            meeting = await uow.meetings_repo.get(meeting_id)

            if not meeting:
                raise MeetingNotFoundError(
                    f"Meeting with ID {meeting_id} not found"
                )

            self._check_can_manage_meeting(meeting, current_user)

            if meeting.start_time < datetime.now(timezone.utc):
                raise MeetingAlreadyOverError(
                    "Can't cancell meetings that are in progress or finished"
                )

            cancelled_meeting = await uow.meetings_repo.cancel_meeting(
                meeting_id
            )

        return cancelled_meeting

    async def get_meeting(
        self, meeting_id: int, current_user: User, uow: IUnitOfWork
    ) -> Meeting:
        """
        Получить встречу по ID.
        Только для членов команды
        """
        async with uow:
            meeting = await uow.meetings_repo.get(meeting_id)

            if not meeting:
                raise MeetingNotFoundError(
                    f"Meeting with ID {meeting_id} not found"
                )

            if current_user.team_id != meeting.team_id:
                raise ForbiddenError(
                    "You can only view meetings from your team"
                )

            is_member = await uow.meetings_repo.is_member(
                meeting_id, current_user.id
            )

            if is_member or current_user.role == UserRole.ADMIN:
                meeting = await uow.meetings_repo.get_meeting_with_members(
                    meeting_id
                )

        return meeting

    async def get_user_meetings(
        self,
        current_user: User,
        uow: IUnitOfWork,
        user_id: int | None = None,
        include_cancelled: bool | None = False,
        include_finished: bool | None = True,
    ) -> List[Meeting]:
        """
        Получить встречи пользователя.
        Admin получает встречи любого пользователя своей команды
        Employee и manager получают свои встречи
        """
        async with uow:
            if current_user.team_id is None:
                raise ForbiddenError("Only team members can access meetings")

            if current_user.role == UserRole.ADMIN:
                if user_id:
                    await CheckTeamLogic.check_user_team(
                        uow, current_user, user_id
                    )
                    meetings = await uow.meetings_repo.get_user_meetings(
                        user_id, include_cancelled, include_finished
                    )
                else:
                    meetings = await uow.meetings_repo.get_user_meetings(
                        current_user.id, include_cancelled, include_finished
                    )
            else:
                meetings = await uow.meetings_repo.get_user_meetings(
                    current_user.id, include_cancelled, include_finished
                )

        return meetings

    async def get_team_meetings(
        self,
        current_user: User,
        uow: IUnitOfWork,
        include_cancelled: bool | None = False,
        include_finished: bool | None = True,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> List[Meeting]:
        """Получить встречи команды"""
        async with uow:
            if current_user.team_id is None:
                raise ForbiddenError("Only team members can access meetings")

            meetings = await uow.meetings_repo.get_team_meetings(
                current_user.team_id,
                include_cancelled,
                include_finished,
                start_date,
                end_date,
            )

        return meetings

    async def get_upcoming_meetings(
        self,
        current_user: User,
        uow: IUnitOfWork,
        minutes_ahead: int | None = 60,
    ) -> List[Meeting]:
        """Получить ближайшие встречи пользователя"""
        async with uow:
            if current_user.team_id is None:
                raise ForbiddenError("Only team members can access meetings")

            meetings = await uow.meetings_repo.get_upcoming_meetings(
                current_user.id, minutes_ahead
            )

        return meetings

    async def add_members_to_meeting(
        self,
        meeting_id: int,
        member_ids: List[int],
        current_user: User,
        uow: IUnitOfWork,
    ) -> Meeting:
        """
        Добавить пользователей к встрече.
        Только для admin и инициатора встречи
        """
        async with uow:
            meeting = await uow.meetings_repo.get_meeting_with_members(
                meeting_id
            )

            if not meeting:
                raise MeetingNotFoundError(
                    f"Meeting with ID {meeting_id} not found"
                )

            self._check_can_manage_meeting(meeting, current_user)

            if meeting.start_time < datetime.now(timezone.utc):
                raise MeetingAlreadyOverError(
                    "Can't add members to meetings that "
                    "are in progress or finished"
                )

            existing_ids = {member.id for member in meeting.members}
            new_member_ids = list(set(member_ids) - existing_ids)

            if not new_member_ids:
                return meeting

            invalid_users = await uow.teams_repo.is_members(
                meeting.team_id, new_member_ids
            )
            if invalid_users:
                raise UserNotInTeamError(
                    f"Users with IDs {invalid_users}"
                    " not found or not in your team"
                )

            overlapping_users = await uow.meetings_repo.check_overlapping(
                user_ids=new_member_ids,
                start_time=meeting.start_time,
                duration_m=meeting.duration_m,
            )
            if overlapping_users:
                raise OverlappingTimeError(
                    f"Users with IDs {overlapping_users} "
                    "have overlapping meetings"
                )

            updated_meeting = await uow.meetings_repo.add_members_to_meeting(
                meeting.id, new_member_ids
            )

        return updated_meeting

    async def remove_member_from_meeting(
        self,
        meeting_id: int,
        member_id: int,
        current_user: User,
        uow: IUnitOfWork,
    ) -> None:
        """
        Удалить пользователя из встречи.
        Только для admin и инициатора встречи
        """
        async with uow:
            meeting = await uow.meetings_repo.get_meeting_with_members(
                meeting_id
            )

            if not meeting:
                raise MeetingNotFoundError(
                    f"Meeting with ID {meeting_id} not found"
                )

            self._check_can_manage_meeting(meeting, current_user)

            if meeting.start_time < datetime.now(timezone.utc):
                raise MeetingAlreadyOverError(
                    "Can't remove members from meetings that "
                    "are in progress or finished"
                )

            if member_id == meeting.initiator_id:
                raise ForbiddenError("Can't remove initiator of meeting")

            await uow.meetings_repo.remove_member_from_meeting(
                meeting_id, member_id
            )

    def _check_can_manage_meeting(
        self, meeting: Meeting, current_user: User
    ) -> None:
        """Проверка доступа к управлению встречей"""

        if (
            current_user.role != UserRole.ADMIN
            and current_user.id != meeting.initiator_id
        ):
            raise ForbiddenError(
                "Only meeting initiator or admin can manage meetings"
            )

        if meeting.team_id != current_user.team_id:
            raise ForbiddenError("You can only manage meetings from your team")

        if not meeting.is_active:
            raise MeetingCancelledError("You can't manage cancelled meetings")
