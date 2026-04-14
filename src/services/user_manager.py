from typing import Union

from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
)

from src.schemas.users import UserCreate
from src.models.users import User
from src.core.config import settings
from src.utils.password_validation import password_validate


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        password_validate(password, user.email)
