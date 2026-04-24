from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.services.user_manager import UserManager
from src.models.users import User
from src.schemas.users import UserRead, UserUpdate
from src.utils.dependencies import get_current_user, get_user_manager

router = APIRouter()


@router.patch("/users/me", response_model=UserRead)
async def update_me_secure(
    user_data: UserUpdate,
    user: User = Depends(get_current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    Переопределенный /me эндпоинт.
    Для изменения пароля или почты необходимо указать текущий пароль
    """
    update_data = user_data.model_dump(exclude_unset=True)

    if "password" in update_data or "email" in update_data:
        current_password = update_data.pop("current_password", None)

        if not current_password:
            raise HTTPException(
                status_code=400,
                detail="Current password needed to change your email/password",
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
