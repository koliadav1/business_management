from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.users import UserRole
from .dependencies import UtcDateTime


class MeetingCreate(BaseModel):
    description: str = Field(
        ..., max_length=1024, description="Описание встречи"
    )
    start_time: UtcDateTime = Field(
        ..., description="Дата и время начала встречи"
    )
    duration_m: int = Field(
        ..., gt=0, description="Планируемая длительность встречи в минутах"
    )
    member_ids: List[int] | None = Field(
        None, description="ID участников встречи"
    )


class MeetingUpdate(BaseModel):
    description: str | None = Field(
        None, max_length=1024, description="Описание встречи"
    )
    start_time: UtcDateTime | None = Field(
        None, description="Дата и время начала встречи"
    )
    duration_m: int | None = Field(
        None, gt=0, description="Планируемая длительность встречи в минутах"
    )


class AddMembersToMeeting(BaseModel):
    member_ids: List[int] = Field(..., description="ID участников встречи")


class RemoveMemberFromMeeting(BaseModel):
    member_id: int = Field(
        ..., description="ID участника встречи для удаления"
    )


class MeetingMemberRead(BaseModel):
    id: int
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class MeetingRead(BaseModel):
    id: int
    description: str
    start_time: UtcDateTime
    duration_m: int
    end_time: UtcDateTime
    is_active: bool
    is_finished: bool
    initiator_id: int
    team_id: int
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class MeetingDetailRead(MeetingRead):
    members: List[MeetingMemberRead] = Field(description="Участники встречи")
