from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppBaseException(Exception):
    status_code = 400


class ForbiddenError(AppBaseException):
    status_code = 403


class TaskNotInTeamError(ForbiddenError):
    pass


class NotFoundError(AppBaseException):
    status_code = 404


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


class CommentNotFoundError(NotFoundError):
    pass


class ConflictError(AppBaseException):
    status_code = 409


class UserNotInTeamError(ConflictError):
    pass


class AlreadyExistsError(ConflictError):
    pass


class UserAlreadyExistsError(AlreadyExistsError):
    pass


class TeamAlreadyExistsError(AlreadyExistsError):
    pass


class UserAlreadyInTeamError(ConflictError):
    pass


class OverlappingTimeError(ConflictError):
    pass


class MeetingCancelledError(ConflictError):
    pass


class MeetingAlreadyOverError(ConflictError):
    pass


class TaskNotCompletedError(ConflictError):
    pass


class UserNotMemberOfMeetingError(ConflictError):
    pass


class InvalidTransitionError(AppBaseException):
    status_code = 400


class InvalidRoleError(AppBaseException):
    status_code = 400


class DateRangeValidationError(AppBaseException):
    status_code = 422


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppBaseException)
    async def base_app_handler(request: Request, exc: AppBaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": [{"msg": str(exc), "type": exc.__class__.__name__}]
            },
        )
