from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.schemas.users import UserRead
from src.core.exceptions import (
    ForbiddenError,
    InvalidRoleError,
    TeamAlreadyExistsError,
    TeamNotFoundError,
    UserAlreadyInTeamError,
    UserNotFoundError,
    UserNotInTeamErorr,
)
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
    try:
        team = await service.create_team(
            uow=uow,
            name=team_data.name,
            description=team_data.description,
            current_user=current_user,
        )
        return team
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TeamAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


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
    team = await service.get_my_team(uow=uow, current_user=current_user)
    if not team:
        raise HTTPException(status_code=204, detail="User has no team")
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
    try:
        team = await service.get_team(uow=uow, team_id=team_id)
        return team
    except TeamNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{team_id}/members",
    response_model=List[UserRead],
    summary="Получить состав команды",
    description="Доступ для членов команды",
)
async def get_team_members(
    team_id: int = Path(gt=0, description="ID команды"),
    role: UserRole | None = Query(None, description="Фильтр по роли"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Получение списка участников команды.
    Только для участников команды
    """
    try:
        members = await service.get_team_members(
            uow=uow, team_id=team_id, current_user=current_user, role=role
        )
        return members
    except TeamNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post(
    "/{team_id}/members",
    response_model=UserRead,
    status_code=201,
    summary="Добавить пользователя в команду",
    description="Только для администратора и менеджера команды",
)
async def add_member(
    request: AddMember,
    team_id: int = Path(gt=0, description="ID команды"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Добавление пользователя в команду.
    Только для manager и admin команды
    """
    try:
        user = await service.add_member(
            uow=uow,
            team_id=team_id,
            user_id=request.user_id,
            current_user=current_user,
            role=request.role,
        )
        return user
    except TeamNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserAlreadyInTeamError as e:
        raise HTTPException(status_code=409, detail=str(e))


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
    try:
        await service.remove_member(
            uow=uow,
            user_id=user_id,
            current_user=current_user,
        )
    except TeamNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotInTeamErorr as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/{team_id}/members/{user_id}/role",
    response_model=UserRead,
    summary="Изменить роль участника",
    description="Только для администратора и менеджера команды",
)
async def update_member_role(
    request: UpdateRole,
    team_id: int = Path(gt=0, description="ID команды"),
    user_id: int = Path(gt=0, description="ID пользователя"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Изменение роли участника команды.
    Только для admin и manager команды
    """
    try:
        user = await service.update_member_role(
            uow=uow,
            team_id=team_id,
            user_id=user_id,
            new_role=request.role,
            current_user=current_user,
        )
        return user
    except TeamNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotInTeamErorr as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidRoleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{team_id}",
    status_code=204,
    summary="Удалить команду",
    description="Только для администратора",
)
async def delete_team(
    team_id: int = Path(gt=0, description="ID команды"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TeamService = Depends(),
):
    """
    Удаление команды.
    Только для admin команды
    """
    try:
        await service.delete_team(
            uow=uow, team_id=team_id, current_user=current_user
        )

    except TeamNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
