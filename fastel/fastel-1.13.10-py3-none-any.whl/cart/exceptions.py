from typing import Any

from fastapi.requests import Request
from fastapi.responses import JSONResponse


class CartException(Exception):
    def __init__(self, message: Any) -> None:
        super().__init__(message)
        print("[CartException]", message)


def cart_exception_handler(request: Request, exc: CartException) -> JSONResponse:
    print("[cart_exception_handler]", exc)
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "detail": ""},
    )
