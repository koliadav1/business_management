import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import UserAlreadyExistsError
from src.core.interfaces.unit_of_work import IUnitOfWork
from src.services.user_manager import UserManager
from src.models.users import User, UserRole
from src.schemas.users import UserRead, UserUpdate
from src.utils.dependencies import (
    get_current_user,
    get_db_session,
    get_user_manager,
    get_uow,
)

router = APIRouter(tags=["users"])


@router.patch("/users/me", response_model=UserRead)
async def update_me_secure(
    user_data: UserUpdate,
    user: User = Depends(get_current_user),
    user_manager: UserManager = Depends(get_user_manager),
    uow: IUnitOfWork = Depends(get_uow),
):
    """
    Переопределенный /me эндпоинт.
    Для изменения пароля или почты необходимо указать текущий пароль
    """
    async with uow:
        update_data = user_data.model_dump(exclude_unset=True)

        if "email" in update_data:
            current_password = update_data.pop("current_password", None)

            if not current_password:
                raise HTTPException(
                    status_code=400,
                    detail="Current password needed "
                    "to change your password",
                )

            verified_user = await user_manager.authenticate(
                OAuth2PasswordRequestForm(
                    username=user.email, password=current_password
                )
            )

            if not verified_user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid current password",
                )

            if "email" in update_data:
                new_email = update_data.get("email", None)

                exists = await uow.users_repo.get_by_email(new_email)
                if exists:
                    raise UserAlreadyExistsError("New email is already taken")

        if "current_password" in update_data:
            del update_data["current_password"]

        try:
            updated_user = await user_manager.update(
                user_update=UserUpdate(**update_data), user=user, safe=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Update failed: {str(e)}",
            )

        return updated_user


@router.delete("/users/me", status_code=204)
async def delete_me(
    password: str,
    user: User = Depends(get_current_user),
    user_manager: UserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Удаление аккаунта без возможности восстановления.
    Требуется подстверждение паролем
    """
    verified_user = await user_manager.authenticate(
        OAuth2PasswordRequestForm(username=user.email, password=password)
    )
    if not verified_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid current password",
        )

    user.is_active = False
    user.email = f"deleted_{user.id}@del.local"
    user.hashed_password = str(uuid.uuid4())
    user.team_id = None
    user.role = UserRole.USER

    user.name = None
    user.surname = None
    user.phone_number = None

    await session.commit()
