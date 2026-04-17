class TaskNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class TeamNotFoundError(Exception):
    pass


class TeamAlreadyExistsError(Exception):
    pass


class UserAlreadyInTeamError(Exception):
    pass


class UserNotInTeamError(Exception):
    pass


class TaskNotInTeamError(Exception):
    pass


class InvalidRoleError(Exception):
    pass


class TaskNotCompletedError(Exception):
    pass


class EvaluationNotFoundError(Exception):
    pass
