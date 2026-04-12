from datetime import datetime, timezone
from typing import Annotated
from pydantic import AfterValidator


def validate_utc(v: datetime) -> datetime:
    if v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)


UtcDateTime = Annotated[datetime, AfterValidator(validate_utc)]
