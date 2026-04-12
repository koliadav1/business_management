from pydantic import ConfigDict, BaseModel, Field

from src.models.tasks import TaskStatus
from .dependencies import UtcDateTime


class TaskCreate(BaseModel):
    description: str = Field(
        ..., max_length=1024, description="Описание задачи"
    )
    deadline: UtcDateTime = Field(..., description="Дедлайн задачи")
    executor_id: int = Field(..., description="ID исполнителя задачи")


class TaskUpdate(BaseModel):
    description: str | None = Field(
        None, max_length=1024, description="Описание задачи"
    )
    deadline: UtcDateTime | None = Field(None, description="Дедлайн задачи")


class TaskAssignExecutor(BaseModel):
    executor_id: int = Field(..., description="ID нового исполнителя задачи")


class TaskChangeStatus(BaseModel):
    status: TaskStatus = Field(..., description="Новый статус задачи")


class TaskRead(BaseModel):
    id: int
    description: str
    deadline: UtcDateTime
    status: TaskStatus
    executor_id: int
    author_id: int
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)
