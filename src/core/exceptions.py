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
