from app.exceptions import ServerError


class UserNotFound(ServerError):
    def __init__(
        self, message: str = "invalid session", status_code: int = 404
    ) -> None:
        super().__init__(message=message, status_code=status_code)


class UserAlreadyExists(ServerError):
    def __init__(
        self, message: str = "user already exists", status_code: int = 403
    ) -> None:
        super().__init__(message=message, status_code=status_code)
