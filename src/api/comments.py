from typing import List

from fastapi import APIRouter, Depends, Path

from src.services.comment_service import CommentService
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.models.users import User
from src.schemas.comments import CommentCreate, CommentRead, CommentUpdate
from src.utils.dependencies import get_current_user, get_uow

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/{task_id}",
    response_model=CommentRead,
    status_code=201,
    summary="Добавить комментарий к задаче",
    description="Только для исполнителя задачи, admin и manager",
)
async def add_comment(
    comment_data: CommentCreate,
    task_id: int = Path(..., gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: CommentService = Depends(),
):
    """
    Добавить комментарий к задаче.
    Только для исполнителя задачи, admin и manager
    """
    comment = await service.add_comment(
        task_id=task_id,
        content=comment_data.content,
        current_user=current_user,
        uow=uow,
    )
    return comment


@router.get(
    "/{task_id}",
    response_model=List[CommentRead],
    summary="Получить комментарии к задаче",
    description="Только для исполнителя задачи, admin и manager",
)
async def get_comments(
    task_id: int = Path(..., gt=0, description="ID задачи"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: CommentService = Depends(),
):
    """
    Получить комментарии к задаче.
    Только для исполнителя задачи, admin и manager
    """
    comments = await service.get_task_comments(
        task_id=task_id, current_user=current_user, uow=uow
    )
    return comments


@router.patch(
    "/{comment_id}",
    response_model=CommentRead,
    summary="Обновить комментарий",
    description="Только для автора комментария и admin",
)
async def update_comment(
    comment_data: CommentUpdate,
    comment_id: int = Path(..., gt=0, description="ID комментария"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: CommentService = Depends(),
):
    """
    Обновить комментарий.
    Только для автора комментария и admin
    """
    updated_comment = await service.update_comment(
        comment_id=comment_id,
        content=comment_data.content,
        current_user=current_user,
        uow=uow,
    )
    return updated_comment


@router.delete(
    "/{comment_id}",
    status_code=204,
    summary="Удалить комментарий",
    description="Только для автора комментария и admin",
)
async def delete_comment(
    comment_id: int = Path(..., gt=0, description="ID комментария"),
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_uow),
    service: CommentService = Depends(),
):

    await service.delete_comment(
        comment_id=comment_id, current_user=current_user, uow=uow
    )
