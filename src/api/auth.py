from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.router import ErrorCode

from src.models.users import User
from src.schemas.auth import LogoutResponse, RefreshTokenResponse
from src.services.user_manager import UserManager
from src.utils.dependencies import (
    get_user_manager,
    get_current_user,
    auth_backend,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    summary="Вход с помощью почты и пароля",
    description="Возвращает access_token и refresh_token в ответе",
)
async def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    Вход с помощью почты и пароля.
    Возвращает access_token и refresh_token в ответе
    """
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    strategy = auth_backend.get_strategy()
    response = await auth_backend.login(strategy, user)
    return response


@router.post(
    "/refresh",
    summary="Обновить access_token",
    response_model=RefreshTokenResponse,
)
async def refresh_access_token(
    request: Request, user_manager=Depends(get_user_manager)
):
    """Обновить access_token при помощи refresh_token"""
    refresh_token = (
        await auth_backend.transport.get_refresh_token_from_request(request)
    )

    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Refresh token required in X-Refresh-Token header",
        )
    response = await auth_backend.refresh(refresh_token, user_manager)
    return response


@router.post(
    "/logout", response_model=LogoutResponse, summary="Выход из системы"
)
async def logout(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
    user: User = Depends(get_current_user),
):
    """Выход из системы"""
    return LogoutResponse(message="Successfully logged out.")
