class BaseError(Exception):
    code: str
    message: str

    def __init__(self, code: str = None, message: str = None, *args: object) -> None:
        self.code = code
        self.message = message

        super().__init__(*args)
