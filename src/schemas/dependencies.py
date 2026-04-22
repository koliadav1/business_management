from datetime import datetime, timezone
from typing import Annotated
from pydantic import AfterValidator


def validate_utc(v: datetime) -> datetime:
    if v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)


UtcDateTime = Annotated[datetime, AfterValidator(validate_utc)]


def validate_future_time(value: UtcDateTime | None) -> UtcDateTime | None:
    if value is not None and value < datetime.now(timezone.utc):
        raise ValueError("Date and time can't be in the past")
    return value


FutureUtcDateTime = Annotated[
    UtcDateTime, AfterValidator(validate_future_time)
]
