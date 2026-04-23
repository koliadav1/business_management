from typing import List
from fastapi import APIRouter, Depends, Path, Query

from src.schemas.base import DateFilter
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.tasks import TaskStatus
from src.services.task_service import TaskService
from src.models.users import User
from src.schemas.tasks import (
    TaskAssignExecutor,
    TaskChangeStatus,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from src.utils.dependencies import get_current_user, get_uow

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/",
    response_model=TaskRead,
    status_code=201,
    summary="Создание задачи",
    description="Только для администраторов и менеджеров команды",
)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Создание новой задачи.
    Только для admin и manager
    """
    task = await service.create_task(
        uow=uow,
        description=task_data.description,
        deadline=task_data.deadline,
        executor_id=task_data.executor_id,
        current_user=current_user,
    )
    return task


@router.get(
    "/",
    response_model=List[TaskRead],
    summary="Получить список задач",
    description="Возвращает задачи в зависимости от роли",
)
async def get_user_tasks(
    user_id: int | None = Query(
        None, description="ID пользователя (только для admin)"
    ),
    status: TaskStatus | None = Query(
        None, description="Фильтр по статусу задачи"
    ),
    date_filters: DateFilter = Depends(),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Получение списка задач.
    Admin и manager могут видеть задачи любого пользователя
    Обычный пользователь видит только свои заачи
    """
    tasks = await service.get_user_tasks(
        uow=uow,
        current_user=current_user,
        status=status,
        user_id=user_id,
        deadline_from=date_filters.start_date,
        deadline_to=date_filters.end_date,
    )
    return tasks


@router.get(
    "/team",
    response_model=List[TaskRead],
    summary="Получить список задач команды",
    description="Только для администраторов и менеджеров команды",
)
async def get_team_tasks(
    status: TaskStatus | None = Query(
        None, description="Фильтр по статусу задачи"
    ),
    date_filters: DateFilter = Depends(),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Получение списка задач команды.
    Только для admin и manager
    """
    tasks = await service.get_team_tasks(
        uow=uow,
        current_user=current_user,
        status=status,
        deadline_from=date_filters.start_date,
        deadline_to=date_filters.end_date,
    )
    return tasks


@router.get(
    "/overdue",
    response_model=List[TaskRead],
    summary="Получить просроченные задачи",
    description="Возвращает просроченные задачи в зависимости от роли",
)
async def get_user_overdue_tasks(
    user_id: int | None = Query(
        None, description="ID пользователя (только для admin)"
    ),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Получение просроченных задач.
    Admin и manager могут видеть задачи любого пользователя
    Обычный пользователь получает свои просроченные задачи
    """
    tasks = await service.get_user_overdue_tasks(
        current_user=current_user, uow=uow, user_id=user_id
    )
    return tasks


@router.get(
    "/team/overdue",
    response_model=List[TaskRead],
    summary="Получить просроченные задачи команды",
    description="Только для администраторов и менеджеров команды",
)
async def get_team_overdue_tasks(
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Получение списка просроченных задач команды.
    Только для admin и manager
    """
    tasks = await service.get_team_overdue_tasks(
        current_user=current_user, uow=uow
    )
    return tasks


@router.get(
    "/{task_id}",
    summary="Получить задачу по ID",
    description="Доступ для admin, manager и исполнителя задачи",
)
async def get_task(
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """Получение информации о задаче"""
    task = await service.get_task(
        uow=uow, task_id=task_id, current_user=current_user
    )
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Обновить задачу",
    description="Обновление описания и дедлайна для admin или автора задачи",
)
async def update_task(
    task_data: TaskUpdate,
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Обновление задачи.
    Только для admin и автора задачи
    """
    task = await service.update_task(
        uow=uow,
        task_id=task_id,
        current_user=current_user,
        description=task_data.description,
        deadline=task_data.deadline,
    )
    return task


@router.patch(
    "/{task_id}/executor",
    response_model=TaskRead,
    summary="Переназначить исполнителя задачи",
    description="Только для admin и автора задачи",
)
async def assign_executor(
    data: TaskAssignExecutor,
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Назначение исполнителя задачи.
    Только для admin и автора задачи
    """
    task = await service.assign_executor(
        uow=uow,
        task_id=task_id,
        executor_id=data.executor_id,
        current_user=current_user,
    )
    return task


@router.patch(
    "/{task_id}/status",
    response_model=TaskRead,
    summary="Изменение статуса задачи",
    description="Изменение статуса задачи с проверкой прав и переходов",
)
async def change_status(
    data: TaskChangeStatus,
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Изменение статуса задачи.

    Статусы:
    new -> in_progress/cancelled
    in_progress -> done/cancelled
    done -> in_progress
    cancelled -> нельзя изменить

    Исполнитель задачи может изменять статус на done или на in_progress
    Admin и автор задачи могут установить любой статус
    """
    task = await service.change_status(
        uow=uow,
        task_id=task_id,
        new_status=data.status,
        current_user=current_user,
    )
    return task


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Удаление задачи",
    description="Только для admin и автора задачи",
)
async def delete_task(
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Удаление задачи.
    Только для admin и автора задачи
    """
    await service.delete_task(
        uow=uow, task_id=task_id, current_user=current_user
    )
