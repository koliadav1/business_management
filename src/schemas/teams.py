from typing import List, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from src.models.users import UserRole
from .dependencies import UtcDateTime

if TYPE_CHECKING:
    from .users import UserRead


class TeamCreate(BaseModel):
    name: str = Field(..., max_length=64, description="Название команды")
    description: str | None = Field(
        None, max_length=1024, description="Описание команды"
    )


class TeamUpdate(BaseModel):
    name: str | None = Field(
        None, max_length=64, description="Название команды"
    )
    description: str | None = Field(
        None, max_length=1024, description="Описание команды"
    )


class TeamRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class TeamWithMembersRead(TeamRead):
    members: List["UserRead"] = []

    model_config = ConfigDict(from_attributes=True)


class AddMember(BaseModel):
    user_id: int = Field(..., description="ID пользователя для добавления")
    role: UserRole = Field(
        UserRole.EMPLOYEE, description="Роль в команде (manager, employee)"
    )


class UpdateRole(BaseModel):
    role: UserRole = Field(..., description="Новая роль (manager, employee)")
