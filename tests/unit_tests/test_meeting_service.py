from datetime import datetime, timedelta, timezone

import pytest

from src.core.exceptions import (
    ForbiddenError,
    MeetingNotFoundError,
    OverlappingTimeError,
    UserNotInTeamError,
)
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.meetings import Meeting
from src.models.users import User
from src.services.meeting_service import MeetingService


class TestMeetingService:

    @pytest.mark.asyncio
    async def test_create_meeting_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        start_time = datetime.now(timezone.utc) + timedelta(days=1)

        expected_meeting = mocker.MagicMock(spec=Meeting)
        expected_meeting.id = 200
        mock_uow.meetings_repo.add.return_value = expected_meeting

        result = await meeting_service.create_meeting(
            "test", start_time, 60, admin_user, mock_uow
        )

        assert result == expected_meeting
        mock_uow.meetings_repo.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_meeting_with_members_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        start_time = datetime.now(timezone.utc) + timedelta(days=1)

        expected_meeting = mocker.MagicMock(spec=Meeting)
        expected_meeting.id = 200
        mock_uow.meetings_repo.add.return_value = expected_meeting
        mock_uow.meetings_repo.add_members_to_meeting.return_value = (
            expected_meeting
        )
        mock_uow.meetings_repo.check_overlapping.return_value = None

        mock_uow.teams_repo.is_members.return_value = None

        result = await meeting_service.create_meeting(
            "test", start_time, 60, admin_user, mock_uow, [admin_user]
        )

        assert result == expected_meeting
        mock_uow.meetings_repo.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_meeting_forbidden(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        employee_user: User,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only admins and managers can create meetings",
        ):
            await meeting_service.create_meeting(
                "asd", datetime.now(), 5, employee_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_create_meeting_with_invalid_members(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        with pytest.raises(
            UserNotInTeamError, match="not found or not in your team"
        ):
            await meeting_service.create_meeting(
                "123", datetime.now(), 60, admin_user, mock_uow, [700, 4324]
            )

    @pytest.mark.asyncio
    async def test_create_meeting_with_invalid_members(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        mock_uow.teams_repo.is_members.return_value = None
        mock_uow.meetings_repo.check_overlapping.return_value = [3]

        with pytest.raises(OverlappingTimeError):
            await meeting_service.create_meeting(
                "asd", datetime.now(), 5, admin_user, mock_uow, [3, 5]
            )

    @pytest.mark.asyncio
    async def test_update_meeting_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_future_meeting: Meeting,
    ):
        mock_uow.meetings_repo.get_meeting_with_members.return_value = (
            mock_future_meeting
        )
        mock_uow.meetings_repo.check_overlapping.return_value = None
        mock_uow.meetings_repo.update.return_value = mock_future_meeting

        result = await meeting_service.update_meeting(
            mock_future_meeting.id,
            admin_user,
            mock_uow,
            "new",
            start_time=datetime.now() + timedelta(days=30),
            duration_m=43243,
        )

        assert result == mock_future_meeting
        assert mock_future_meeting.description == "new"

    @pytest.mark.asyncio
    async def test_update_meeting_forbidden(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_future_meeting: Meeting,
    ):
        with pytest.raises(
            ForbiddenError,
            match="Only meeting initiator or admin can manage meetings",
        ):
            await meeting_service.update_meeting(
                mock_future_meeting,
                employee_user,
                mock_uow,
                "new",
            )

    @pytest.mark.asyncio
    async def test_cancell_meeting_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_future_meeting: Meeting,
    ):
        mock_uow.meetings_repo.get.return_value = mock_future_meeting
        mock_uow.meetings_repo.cancel_meeting.return_value = (
            mock_future_meeting
        )

        result = await meeting_service.cancel_meeting(
            mock_future_meeting.id, admin_user, mock_uow
        )

        assert result == mock_future_meeting
        mock_uow.meetings_repo.cancel_meeting.assert_called_once_with(
            mock_future_meeting
        )

    @pytest.mark.asyncio
    async def test_cancell_meeting_not_found(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
    ):
        mock_uow.meetings_repo.get.return_value = None
        with pytest.raises(MeetingNotFoundError):
            await meeting_service.cancel_meeting(999, admin_user, mock_uow)

    @pytest.mark.asyncio
    async def test_get_meeting_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_future_meeting: Meeting,
    ):
        mock_uow.meetings_repo.get_meeting_with_members.return_value = (
            mock_future_meeting
        )
        mock_uow.meetings_repo.is_member.return_value = False

        result = await meeting_service.get_meeting(
            mock_future_meeting.id, admin_user, mock_uow
        )

        assert result == mock_future_meeting
        mock_uow.meetings_repo.get_meeting_with_members.assert_called_once_with(
            mock_future_meeting.id
        )

    @pytest.mark.asyncio
    async def test_get_meeting_forbidden(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mock_future_meeting: Meeting,
    ):
        mock_uow.meetings_repo.is_member.return_value = False

        with pytest.raises(
            ForbiddenError,
            match="Only meeting members and admin can view meeting",
        ):
            await meeting_service.get_meeting(
                mock_future_meeting.id, employee_user, mock_uow
            )

    @pytest.mark.asyncio
    async def test_get_user_meetings_as_admin(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        employee_user: User,
        mocker,
    ):
        expected_meetings = [mocker.MagicMock(spec=Meeting) for _ in range(5)]
        mock_uow.users_repo.get.return_value = employee_user
        mock_uow.meetings_repo.get_user_meetings.return_value = (
            expected_meetings
        )

        result = await meeting_service.get_user_meetings(
            admin_user,
            mock_uow,
            employee_user.id,
            include_cancelled=True,
            include_finished=False,
        )

        assert result == expected_meetings
        mock_uow.meetings_repo.get_user_meetings.assert_called_once_with(
            employee_user.id, True, False
        )

    @pytest.mark.asyncio
    async def test_get_user_meetings_as_self(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        expected_meetings = [mocker.MagicMock(spec=Meeting) for _ in range(5)]
        mock_uow.users_repo.get.return_value = employee_user
        mock_uow.meetings_repo.get_user_meetings.return_value = (
            expected_meetings
        )

        result = await meeting_service.get_user_meetings(
            employee_user, mock_uow
        )

        assert result == expected_meetings
        mock_uow.meetings_repo.get_user_meetings.assert_called_once_with(
            employee_user.id, False, True
        )

    @pytest.mark.asyncio
    async def test_get_user_meetings_not_in_team(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        regular_user: User,
    ):
        with pytest.raises(
            ForbiddenError, match="Only team members can access meetings"
        ):
            await meeting_service.get_user_meetings(regular_user, mock_uow)

    @pytest.mark.asyncio
    async def test_get_team_meetings_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mocker,
    ):
        start_time = datetime.now(timezone.utc)
        end_date = start_time + timedelta(days=30)
        expected_meetings = [mocker.MagicMock(spec=Meeting) for _ in range(5)]
        mock_uow.meetings_repo.get_team_meetings.return_value = (
            expected_meetings
        )

        result = await meeting_service.get_team_meetings(
            admin_user, mock_uow, True, False, start_time, end_date
        )

        assert result == expected_meetings
        mock_uow.meetings_repo.get_team_meetings.assert_called_once_with(
            admin_user.team_id, True, False, start_time, end_date
        )

    @pytest.mark.asyncio
    async def test_get_upcoming_meetings_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        employee_user: User,
        mocker,
    ):
        expected_meetings = [mocker.MagicMock(spec=Meeting) for _ in range(5)]
        mock_uow.meetings_repo.get_upcoming_meetings.return_value = (
            expected_meetings
        )

        result = await meeting_service.get_upcoming_meetings(
            employee_user, mock_uow, 120
        )

        assert result == expected_meetings
        mock_uow.meetings_repo.get_upcoming_meetings.assert_called_once_with(
            employee_user.id, 120
        )

    @pytest.mark.asyncio
    async def test_add_members_to_meeting_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_future_meeting: Meeting,
        mocker,
    ):
        member_ids = [4, 5]
        mock_future_meeting.members = [admin_user]

        mock_uow.meetings_repo.get_meeting_with_members.return_value = (
            mock_future_meeting
        )
        mock_uow.teams_repo.is_members.return_value = None
        mock_uow.meetings_repo.check_overlapping.return_value = None

        upd_meeting = mocker.MagicMock(spec=Meeting)
        mock_uow.meetings_repo.add_members_to_meeting.return_value = (
            upd_meeting
        )

        result = await meeting_service.add_members_to_meeting(
            mock_future_meeting.id, member_ids, admin_user, mock_uow
        )

        assert result == upd_meeting

    @pytest.mark.asyncio
    async def test_add_members_to_meeting_existing(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_future_meeting: Meeting,
        mocker,
    ):
        member_ids = [4, 5]

        existing_user = mocker.MagicMock(spec=User)
        existing_user.id = 4

        mock_future_meeting.members = [admin_user, existing_user]

        mock_uow.meetings_repo.get_meeting_with_members.return_value = (
            mock_future_meeting
        )
        mock_uow.teams_repo.is_members.return_value = None
        mock_uow.meetings_repo.check_overlapping.return_value = None

        upd_meeting = mocker.MagicMock(spec=Meeting)
        mock_uow.meetings_repo.add_members_to_meeting.return_value = (
            upd_meeting
        )

        await meeting_service.add_members_to_meeting(
            mock_future_meeting.id, member_ids, admin_user, mock_uow
        )

        mock_uow.meetings_repo.add_members_to_meeting.assert_called_once_with(
            mock_future_meeting, [5]
        )

    async def test_remove_member_success(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_future_meeting: Meeting,
        mocker,
    ):
        member_to_remove = mocker.MagicMock(spec=User)
        member_to_remove.id = 5

        mock_future_meeting.members = [admin_user, member_to_remove]

        mock_uow.meetings_repo.get_meeting_with_members.return_value = (
            mock_future_meeting
        )
        mock_uow.users_repo.get.return_value = member_to_remove

        await meeting_service.remove_member_from_meeting(
            mock_future_meeting.id, member_to_remove.id, admin_user, mock_uow
        )

        mock_uow.meetings_repo.remove_member_from_meeting.assert_called_once_with(
            mock_future_meeting, member_to_remove
        )

    async def test_remove_member_initiator(
        self,
        meeting_service: MeetingService,
        mock_uow: IUnitOfWork,
        admin_user: User,
        mock_future_meeting: Meeting,
    ):
        mock_future_meeting.initiator_id = admin_user.id
        mock_uow.meetings_repo.get_meeting_with_members.return_value = (
            mock_future_meeting
        )

        with pytest.raises(
            ForbiddenError, match="Can't remove initiator of meeting"
        ):
            await meeting_service.remove_member_from_meeting(
                mock_future_meeting.id, admin_user.id, admin_user, mock_uow
            )
