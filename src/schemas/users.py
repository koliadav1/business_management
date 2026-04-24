from typing import Annotated

from fastapi_users import schemas
from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from src.models.users import UserRole


def validate_phone_number(value: str | None) -> str | None:
    if value is not None and not value.replace("+", "").isdigit():
        raise ValueError(
            "Phone number must contain only digits and optional '+'"
        )
    return value


PhoneStr = Annotated[str, AfterValidator(validate_phone_number)]


class BaseUser(BaseModel):
    name: str | None = Field(
        None, max_length=30, description="Имя пользователя"
    )
    surname: str | None = Field(
        None, max_length=30, description="Фамилия пользователя"
    )
    phone_number: PhoneStr | None = Field(
        None, max_length=20, description="Номер телефона пользователя"
    )


class UserRead(schemas.BaseUser[int]):
    id: int
    team_id: int | None
    email: EmailStr
    role: UserRole
    name: str | None
    surname: str | None
    phone_number: PhoneStr | None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseUser, schemas.BaseUserCreate):
    email: EmailStr
    password: str


class UserUpdate(BaseUser, schemas.BaseUserUpdate):
    pass
