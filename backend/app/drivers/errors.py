from app.exceptions import ServerError


class DriverNotFound(ServerError):
    def __init__(
        self, message: str = "Driver not found", status_code: int = 404
    ) -> None:
        super().__init__(message=message, status_code=status_code)


class DriverAlreadyExists(ServerError):
    def __init__(
        self, message: str = "Driver already exists", status_code: int = 403
    ) -> None:
        super().__init__(message=message, status_code=status_code)
