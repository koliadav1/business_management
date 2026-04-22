from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ForbiddenError(Exception):
    pass


class NotFoundError(Exception):
    pass


class TaskNotFoundError(NotFoundError):
    pass


class UserNotFoundError(NotFoundError):
    pass


class TeamNotFoundError(NotFoundError):
    pass


class EvaluationNotFoundError(NotFoundError):
    pass


class MeetingNotFoundError(NotFoundError):
    pass


class NotInTeamError(Exception):
    pass


class UserNotInTeamError(NotInTeamError):
    pass


class TaskNotInTeamError(NotInTeamError):
    pass


class InvalidTransitionError(Exception):
    pass


class TeamAlreadyExistsError(Exception):
    pass


class UserAlreadyInTeamError(Exception):
    pass


class InvalidRoleError(Exception):
    pass


class TaskNotCompletedError(Exception):
    pass


class OverlappingTimeError(Exception):
    pass


class MeetingCancelledError(Exception):
    pass


class MeetingAlreadyOverError(Exception):
    pass


class DateRangeValidationError(Exception):
    pass


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(DateRangeValidationError)
    async def date_range_handler(
        request: Request, exc: DateRangeValidationError
    ):
        return JSONResponse(status_code=422, content={"detail": str(exc)})
