from app.exceptions import ServerError


class VehicleNotFound(ServerError):
    def __init__(
        self, message: str = "Vehicle not found", status_code: int = 404
    ) -> None:
        super().__init__(message=message, status_code=status_code)


class VehicleAlreadyExists(ServerError):
    def __init__(
        self,
        message: str = "Vehicle with the same registration or license number already exists",
        status_code: int = 403,
    ) -> None:
        super().__init__(message=message, status_code=status_code)
