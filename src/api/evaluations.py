from datetime import datetime
from fastapi import APIRouter, Depends, Path, Query

from src.schemas.base import PaginatedRead
from src.services.evaluation_service import EvaluationService
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.utils.dependencies import get_current_user, get_uow
from src.models.users import User
from src.schemas.evaluations import (
    EvaluationCreate,
    EvaluationRead,
    EvaluationWithTaskRead,
    StatsRead,
)

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post(
    "/rate/{task_id}",
    response_model=EvaluationRead,
    status_code=200,
    summary="Оценить задачу",
    description="Оценить или обновить оценку задачи. Только admin и manager",
)
async def rate_task(
    task_id: int,
    request: EvaluationCreate,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: EvaluationService = Depends(),
):
    """
    Оценка задачи от 1 до 5
    Только для admin и manager
    """
    evaluation = await service.rate_task(
        task_id=task_id,
        rating=request.rating,
        comment=request.comment,
        current_user=current_user,
        uow=uow,
    )
    return evaluation


@router.get(
    "/",
    response_model=PaginatedRead[EvaluationRead],
    summary="Получить оценки",
    description="Возвращает оценки в зависимости от роли",
)
async def get_evaluations(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: int | None = Query(
        None, description="ID пользователя, только для admin и manager"
    ),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: EvaluationService = Depends(),
):
    """
    Получение списка оценок.
    Admin и manager получают оценки любого пользователя или всей команды
    Employee получают только свои оценки внутри команды
    User получает свои оценки вне зависисомти от команды
    """
    result = await service.get_evaluations(
        current_user=current_user,
        uow=uow,
        page=page,
        limit=limit,
        user_id=user_id,
    )
    return PaginatedRead(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get(
    "/with-tasks",
    response_model=PaginatedRead[EvaluationWithTaskRead],
    summary="Получить оценки вместе с задачами",
    description="Возвращает оценки и связанные с ними задачи",
)
async def get_evaluations_with_tasks(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: int | None = Query(
        None, description="ID пользователя, только для admin и manager"
    ),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: EvaluationService = Depends(),
):
    """
    Получить все оценки пользователя вместе с данными о задачах.
    Admin и manager получают оценки любого пользователя
    Employee получает только свои оценки
    """
    result = await service.get_evaluations_with_tasks(
        uow=uow,
        current_user=current_user,
        page=page,
        limit=limit,
        user_id=user_id,
    )
    return PaginatedRead(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get(
    "/stats",
    response_model=StatsRead,
    summary="Получить статистику по оценкам за определенный период",
    description="Возвращает среднюю оценку, количество и распределение",
)
async def get_stats(
    user_id: int | None = Query(
        None, description="ID пользователя, только для admin и manager"
    ),
    start_date: datetime | None = Query(None, description="Начало периода"),
    end_date: datetime | None = Query(None, description="Конец периода"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: EvaluationService = Depends(),
):
    """
    Получение статистики по оценкам за заданный период.
    Admin и manager получают статистику любого пользователя
    Employee получают только свою статистику внутри команды
    User получает свою статистику вне зависимости от команды
    """
    stats = await service.get_rating_stats(
        uow=uow,
        current_user=current_user,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return stats


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Удалить оценку",
    description="Удаление оценки задачи. Только для admin и manager",
)
async def delete_evaluation(
    task_id: int = Path(gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: EvaluationService = Depends(),
):
    """
    Удаление оценки задачи.
    Только для admin и manager
    """
    await service.delete_evaluation(
        task_id=task_id, uow=uow, current_user=current_user
    )
