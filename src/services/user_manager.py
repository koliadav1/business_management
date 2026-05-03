from typing import Union

from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
    exceptions,
)
from sqlalchemy import select

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

    async def create(self, user_create: UserCreate, safe=False, request=None):
        if user_create.phone_number:
            user = await self.get_by_phone(user_create.phone_number)
            if user:
                raise exceptions.UserAlreadyExists(
                    "Phone number is already taken"
                )
        return await super().create(user_create, safe, request)

    async def get_by_phone(self, phone_number: str):
        query = select(User).where(User.phone_number == phone_number)
        result = await self.user_db.session.execute(query)
        user = result.scalar_one_or_none()
        return user
