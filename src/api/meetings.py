from typing import List

from fastapi import APIRouter, Depends, Path, Query

from src.schemas.base import DateFilter
from src.services.meeting_service import MeetingService
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.users import User
from src.schemas.meetings import (
    AddMembersToMeeting,
    MeetingCreate,
    MeetingDetailRead,
    MeetingRead,
    MeetingUpdate,
    RemoveMemberFromMeeting,
)
from src.utils.dependencies import get_current_user, get_uow

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post(
    "/",
    response_model=MeetingDetailRead,
    status_code=201,
    summary="Создание встречи",
    description="Только для admin и manager",
)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """
    Создание новой встречи.
    Только для admin и manager
    """
    meeting = await service.create_meeting(
        description=meeting_data.description,
        start_time=meeting_data.start_time,
        duration_m=meeting_data.duration_m,
        member_ids=meeting_data.member_ids,
        current_user=current_user,
        uow=uow,
    )
    return meeting


@router.get(
    "/",
    response_model=List[MeetingRead],
    summary="Получить список встреч пользователя",
    description="Возвращает список встреч текущего пользователя "
    "или указанного (для admin)",
)
async def get_user_meetings(
    user_id: int | None = Query(
        None, description="ID пользователя (только для admin)"
    ),
    include_cancelled: bool = Query(
        False, description="Включить отмененные встречи"
    ),
    include_finished: bool = Query(
        True, description="Включить прошедшие и текущие встречи"
    ),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """
    Получение списка встреч пользователя.
    Admin получает встречи любого пользователя по ID
    Остальные члены команды получают свои встречи
    """
    meetings = await service.get_user_meetings(
        current_user=current_user,
        uow=uow,
        user_id=user_id,
        include_cancelled=include_cancelled,
        include_finished=include_finished,
    )
    return meetings


@router.get(
    "/team",
    response_model=List[MeetingRead],
    summary="Получить встречи команды",
    description="Возвращает все встречи внутри команды пользователя",
)
async def get_team_meetings(
    include_cancelled: bool = Query(
        False, description="Включить отмененные встречи"
    ),
    include_finished: bool = Query(
        True, description="Включить прошедшие и текущие встречи"
    ),
    date_filters: DateFilter = Depends(),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """Получение всех встреч внутри команды"""
    meetings = await service.get_team_meetings(
        current_user=current_user,
        uow=uow,
        include_cancelled=include_cancelled,
        include_finished=include_finished,
        start_date=date_filters.start_date,
        end_date=date_filters.end_date,
    )
    return meetings


@router.get(
    "/upcoming",
    response_model=List[MeetingRead],
    summary="Получить ближайшие встречи",
    description="Возвращает ближайшие встречи пользователя",
)
async def get_upcoming_meetings(
    minutes_ahead: int | None = Query(
        60,
        ge=1,
        le=1440,
        description="Максимальное время до встреч в минутах "
        "(не более 1440 минут или 24 часов)",
    ),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """Получение ближайших встреч пользователя"""
    meetings = await service.get_upcoming_meetings(
        current_user=current_user, uow=uow, minutes_ahead=minutes_ahead
    )
    return meetings


@router.get(
    "/{meeeting_id}",
    response_model=MeetingDetailRead,
    summary="Получение встречи и ее участников",
    description="Возвращает подробную информацию о встрече",
)
async def get_meeting(
    meeting_id: int = Path(gt=0, description="ID встречи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """
    Получение информации о встречи.
    Участники встречи и admin получают встречу со списком ее участников
    Остальные получают только информацию о встрече
    """
    meeting = await service.get_meeting(
        meeting_id=meeting_id, current_user=current_user, uow=uow
    )
    return meeting


@router.patch(
    "/{meeting_id}",
    response_model=MeetingRead,
    summary="Обновить встречу",
    description="Обновить информацию о встрече "
    "(только для admin и создателя встречи)",
)
async def update_meeting(
    meeting_data: MeetingUpdate,
    meeting_id: int = Path(gt=0, description="ID встречи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """
    Обновление встречи.
    Только для admin и инициатора встречи
    """
    meeting = await service.update_meeting(
        meeting_id=meeting_id,
        description=meeting_data.description,
        start_time=meeting_data.start_time,
        duration_m=meeting_data.duration_m,
        current_user=current_user,
        uow=uow,
    )
    return meeting


@router.patch(
    "/{meeting_id}/cancel",
    response_model=MeetingRead,
    summary="Отменить встречу",
    description="Отмена встречи (только для admin и организатора встречи)",
)
async def cancel_meeting(
    meeting_id: int = Path(gt=0, description="ID встречи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """
    Отмена встречи.
    Только для admin или инициатора встречи
    """
    meeting = await service.cancel_meeting(
        meeting_id=meeting_id, current_user=current_user, uow=uow
    )
    return meeting


@router.post(
    "/{meeting_id}/members",
    response_model=MeetingDetailRead,
    summary="Добавить участников к встрече",
    description="Добавление новых участников к существующей встрече "
    "(только для admin и организатора встречи)",
)
async def add_members_to_meeting(
    data: AddMembersToMeeting,
    meeting_id: int = Path(gt=0, description="ID встречи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """
    Добавление участников к встрече.
    Только для admin и инициатора встречи
    """
    meeting = await service.add_members_to_meeting(
        meeting_id=meeting_id,
        member_ids=data.member_ids,
        current_user=current_user,
        uow=uow,
    )
    return meeting


@router.delete(
    "/{meeting_id}/members",
    status_code=204,
    summary="Удлаить участника из встречи",
    description="Удалить пользователя из участников встречи "
    "(только для admin и организатора встречи)",
)
async def remove_member_from_meeting(
    data: RemoveMemberFromMeeting,
    meeting_id: int = Path(gt=0, description="ID встречи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: MeetingService = Depends(),
):
    """
    Удаление участника из встречи.
    Только для admin и инициатора встречи
    """
    await service.remove_member_from_meeting(
        meeting_id=meeting_id,
        member_id=data.member_id,
        current_user=current_user,
        uow=uow,
    )
