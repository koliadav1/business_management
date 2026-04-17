from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.core.exceptions import (
    EvaluationNotFoundError,
    ForbiddenError,
    TaskNotCompletedError,
    TaskNotFoundError,
    TaskNotInTeamError,
    UserNotFoundError,
    UserNotInTeamError,
)
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
    try:
        evaluation = await service.rate_task(
            task_id=task_id,
            rating=request.rating,
            comment=request.comment,
            current_user=current_user,
            uow=uow,
        )
        return evaluation
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotCompletedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaskNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get(
    "/",
    response_model=List[EvaluationRead],
    summary="Получить оценки",
    description="Возвращает оценки в зависимости от роли",
)
async def get_evaluation(
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
    try:
        evaluations = await service.get_evaluations(
            current_user=current_user,
            uow=uow,
            user_id=user_id,
        )
        return evaluations
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get(
    "/with-tasks",
    response_model=List[EvaluationWithTaskRead],
    summary="Получить оценки вместе с задачами",
    description="Возвращает оценки и связанные с ними задачи",
)
async def get_evaluations_with_tasks(
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
    try:
        evaluations = await service.get_evaluations_with_tasks(
            uow=uow, current_user=current_user, user_id=user_id
        )
        return [
            EvaluationWithTaskRead(
                evaluation=evaluation,
                task=task,
            )
            for evaluation, task in evaluations
        ]
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
    try:
        stats = await service.get_rating_stats(
            uow=uow,
            current_user=current_user,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        return stats
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))


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
    try:
        await service.delete_evaluation(
            task_id=task_id, uow=uow, current_user=current_user
        )
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaskNotInTeamError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except EvaluationNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
