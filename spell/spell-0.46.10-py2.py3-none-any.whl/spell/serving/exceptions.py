from starlette.exceptions import HTTPException


class InvalidPredictor(TypeError):
    pass


class BadAPIResponse(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=500, detail=detail)


class InvalidServerConfiguration(RuntimeError):
    pass
