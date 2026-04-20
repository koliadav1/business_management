class ForbiddenError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class TeamNotFoundError(Exception):
    pass


class EvaluationNotFoundError(Exception):
    pass


class MeetingNotFoundError(Exception):
    pass


class UserNotInTeamError(Exception):
    pass


class TaskNotInTeamError(Exception):
    pass


# TODO сгруппировать исключения выше и сделать код api чище благодаря наследованию исключений


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
