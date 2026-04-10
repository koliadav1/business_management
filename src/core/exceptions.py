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


class UserNotInTeamErorr(Exception):
    pass


class InvalidrRoleError(Exception):
    pass
