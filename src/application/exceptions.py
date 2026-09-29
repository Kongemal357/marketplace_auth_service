class EmailAlreadyTakenError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass
