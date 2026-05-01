from typing import Dict

from pydantic import ConfigDict, BaseModel, Field

from .tasks import TaskRead
from .dependencies import UtcDateTime


class EvaluationBase(BaseModel):
    rating: int = Field(ge=1, le=5, description="Оценка от 1 до 5")
    comment: str | None = Field(
        None, max_length=1024, description="Комментарий к оценке"
    )


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationUpdate(EvaluationBase):
    pass


class EvaluationRead(EvaluationBase):
    id: int
    task_id: int
    rater_id: int
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class EvaluationWithTaskRead(BaseModel):
    evaluation: EvaluationRead | None
    task: TaskRead


class StatsRead(BaseModel):
    average: float = Field(description="Средняя оценка по задачам")
    total: int = Field(description="Количество оцененных задач")
    distribution: Dict[int, int] = Field(description="Распределение оценок")
