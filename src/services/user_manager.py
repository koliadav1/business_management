from fastapi_users import BaseUserManager, IntegerIDMixin

from src.models.users import Users
from src.core.config import settings


class UserManager(IntegerIDMixin, BaseUserManager[Users, int]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret = settings.SECRET
