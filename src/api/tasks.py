from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.tasks import TaskStatus
from src.core.exceptions import (
    ForbiddenError,
    InvalidTransitionError,
    TaskNotFoundError,
    TaskNotInTeamError,
    UserNotFoundError,
    UserNotInTeamError,
)
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
    description="Только для администраторов",
)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Создание новой задачи.
    Только для admin
    """
    try:
        task = await service.create_task(
            uow=uow,
            description=task_data.description,
            deadline=task_data.deadline,
            executor_id=task_data.executor_id,
            current_user=current_user,
        )
        return task
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get(
    "/",
    response_model=List[TaskRead],
    summary="Получить список задач",
    description="Возвращает задачи в зависимости от роли",
)
async def get_tasks(
    user_id: int | None = Query(
        None, description="ID пользователя (только для admin)"
    ),
    status: TaskStatus | None = Query(
        None, description="Фильтр по статусу задачи"
    ),
    deadline_from: datetime | None = Query(
        None, description="Начальная дата для фильтрации по дедлайну"
    ),
    deadline_to: datetime | None = Query(
        None, description="Конечная дата для фильтрации по дедлайну"
    ),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Получение списка задач.
    Admin может видеть задачи любого пользователя
    Обычный пользователь видит только свои заачи
    """
    try:
        tasks = await service.get_tasks(
            uow=uow,
            current_user=current_user,
            status=status,
            user_id=user_id,
            deadline_from=deadline_from,
            deadline_to=deadline_to,
        )
        return tasks
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/overdue",
    response_model=List[TaskRead],
    summary="Получить просроченные задачи",
    description="Возвращает просроченные задачи пользователя и всех (admin)",
)
async def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Получение просроченных задач.
    Admin получает все просроченные задачи
    Обычный пользователь получает свои просроченные задачи
    """
    tasks = await service.get_overdue_tasks(current_user=current_user, uow=uow)
    return tasks


@router.get(
    "/{task_id}",
    summary="Получить задачу по ID",
    description="Доступ для admin и исполнителя задачи",
)
async def get_task(
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """Получение информации о задаче"""
    try:
        task = await service.get_task(
            uow=uow, task_id=task_id, current_user=current_user
        )
        return task
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaskNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Обновить задачу",
    description="Обновление описания и дедлайна задачи для admin",
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
    Только для admin
    """
    try:
        task = await service.update_task(
            uow=uow,
            task_id=task_id,
            current_user=current_user,
            description=task_data.description,
            deadline=task_data.deadline,
        )
        return task
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch(
    "/{task_id}/executor",
    response_model=TaskRead,
    summary="Переназначить исполнителя задачи",
    description="Только для admin",
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
    Только для admin
    """
    try:
        task = await service.assign_executor(
            uow=uow,
            task_id=task_id,
            executor_id=data.executor_id,
            current_user=current_user,
        )
        return task
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
    Admin может установить любой статус
    """
    try:
        task = await service.change_status(
            uow=uow,
            task_id=task_id,
            new_status=data.status,
            current_user=current_user,
        )
        return task
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Удаление задачи",
    description="Только для admin",
)
async def delete_task(
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    """
    Удаление задачи.
    Только для admin
    """
    try:
        await service.delete_task(
            uow=uow, task_id=task_id, current_user=current_user
        )
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaskNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))
