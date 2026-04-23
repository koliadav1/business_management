from typing import List
from fastapi import APIRouter, Depends, Path, Query

from src.schemas.users import UserRead
from src.services.team_service import TeamService
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.users import User, UserRole
from src.schemas.teams import (
    AddMember,
    TeamCreate,
    TeamRead,
    UpdateRole,
)
from src.utils.dependencies import get_current_user, get_uow

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post(
    "/",
    response_model=TeamRead,
    status_code=201,
    summary="Создать команду",
    description="Только для admin. Администратор становится главой команды",
)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Создание новой команды.
    Только для admin
    """
    team = await service.create_team(
        uow=uow,
        name=team_data.name,
        description=team_data.description,
        current_user=current_user,
    )
    return team


@router.get(
    "/",
    response_model=List[TeamRead],
    summary="Получение списка команд",
)
async def get_all_teams(
    uow: IUnitOfWork = Depends(get_uow), service: TeamService = Depends()
):
    """Получение списка команд"""
    team = await service.get_all_teams(uow=uow)
    return team


@router.get(
    "/my-team",
    response_model=TeamRead,
    summary="Получить данные о моей команде",
    description="Возвращает данные о команде пользователя",
)
async def get_my_team(
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Получение данных о команде текущего пользователя
    """
    team = await service.get_team(uow=uow, team_id=current_user.team_id)
    return team


@router.get(
    "/{team_id}",
    response_model=TeamRead,
    summary="Получить информацию о команде",
)
async def get_team(
    team_id: int = Path(gt=0, description="ID команды"),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """Получение базовой информации о команде"""
    team = await service.get_team(uow=uow, team_id=team_id)
    return team


@router.get(
    "/members",
    response_model=List[UserRead],
    summary="Получить состав команды",
    description="Доступ для членов команды",
)
async def get_team_members(
    role: UserRole | None = Query(None, description="Фильтр по роли"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Получение списка участников команды.
    Только для участников команды
    """
    members = await service.get_team_members(
        uow=uow, current_user=current_user, role=role
    )
    return members


@router.post(
    "/members",
    response_model=UserRead,
    status_code=201,
    summary="Добавить пользователя в команду",
    description="Только для администратора и менеджера команды",
)
async def add_member(
    request: AddMember,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Добавление пользователя в команду.
    Только для manager и admin команды
    """
    user = await service.add_member(
        uow=uow,
        user_id=request.user_id,
        current_user=current_user,
        role=request.role,
    )
    return user


@router.delete(
    "/members/{user_id}",
    status_code=204,
    summary="Убрать участника из команды",
    description="Только для администратора и менеджера команды",
)
async def remove_member(
    user_id: int = Path(gt=0, description="ID пользователя"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Удаление пользователя из команды.
    Только для admin и manager команды
    """
    await service.remove_member(
        uow=uow,
        user_id=user_id,
        current_user=current_user,
    )


@router.patch(
    "/members/{user_id}/role",
    response_model=UserRead,
    summary="Изменить роль участника",
    description="Только для администратора и менеджера команды",
)
async def update_member_role(
    request: UpdateRole,
    user_id: int = Path(gt=0, description="ID пользователя"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Изменение роли участника команды.
    Только для admin и manager команды
    """
    user = await service.update_member_role(
        uow=uow,
        user_id=user_id,
        new_role=request.role,
        current_user=current_user,
    )
    return user


@router.delete(
    "/",
    status_code=204,
    summary="Удалить команду",
    description="Только для администратора",
)
async def delete_team(
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Удаление команды.
    Только для admin команды
    """
    await service.delete_team(uow=uow, current_user=current_user)


@router.delete(
    "/members/me",
    status_code=204,
    summary="Удалить себя из команды",
    description="Уйти из команды",
)
async def remove_self(
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """Удаление себя из команды"""
    await service.quit_team(
        uow=uow,
        current_user=current_user,
    )
