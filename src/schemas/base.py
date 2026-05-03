from typing import Generic, List, TypeVar

from fastapi import Query
from pydantic import BaseModel, model_validator

from src.core.exceptions import DateRangeValidationError
from .dependencies import UtcDateTime


class DateFilter(BaseModel):
    start_date: UtcDateTime | None = Query(
        None, description="Начальная дата для фильтрации"
    )
    end_date: UtcDateTime | None = Query(
        None, description="Конечная дата для фильтрации"
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> UtcDateTime | None:
        if (
            self.start_date
            and self.end_date
            and self.end_date < self.start_date
        ):
            raise DateRangeValidationError(
                "end_date must be greater than or equal to start_date"
            )
        return self


T = TypeVar("T")


class PaginatedRead(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
