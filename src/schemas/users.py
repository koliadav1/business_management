from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr

from src.models.users import UserRole


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    pass
