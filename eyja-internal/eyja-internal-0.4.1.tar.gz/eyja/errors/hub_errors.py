from .base_error import BaseError


class LoadConfigError(BaseError):
    def __init__(self, message: str = None, *args: object) -> None:
        super().__init__('LOAD_CONFIG', message, *args)

class WrongConnectionError(BaseError):
    def __init__(self, message: str = None, *args: object) -> None:
        super().__init__('WRONG_CONNECTION', message, *args)
