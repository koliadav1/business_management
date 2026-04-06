from typing import Union

from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
    InvalidPasswordException,
)

from src.schemas.users import UserCreate
from src.models.users import User
from src.core.config import settings


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Пароль должен быть не короче 8 символов"
            )
        if len(password) > 100:
            raise InvalidPasswordException(
                reason="Пароль должен быть не длинее 100 символов"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Пароль не должен содержать адрес почты"
            )
        if not any(ch.isdigit() for ch in password):
            raise InvalidPasswordException(
                reason="пароль должен содержать хотя бы одну цифру"
            )
