from typing import Any, Optional, Union

import falcon
from validr import Invalid

__all__ = (
    "BaseWebError",
    "RequestParamsInvalid",
    "ResponderReturnsInvalid",
)


class BaseWebError(Exception):
    """BaseWebError"""

    message: str
    error: str
    detail: Optional[Any]
    status: falcon.HTTPStatus
    headers: Optional[Union[list, dict]]

    def __init__(
        self,
        message: str,
        error: str = None,
        detail: Any = None,
        status: falcon.HTTPStatus = falcon.HTTP_400,
        headers: Union[list, dict] = None,
    ) -> None:
        self.message = message
        self.error = error or type(self).__name__
        self.detail = detail
        self.status = status
        self.headers = headers

    def __repr__(self):
        type_name = type(self).__name__
        error = ""
        if self.error != type_name:
            error = f"{self.error}: "
        return f"<{type_name} {error}{self.message}>"

    def __str__(self) -> str:
        return f"{self.error}: {self.message}"


class RequestParamsInvalid(BaseWebError):
    """RequestParamsInvalid"""

    def __init__(self, error: Invalid) -> None:
        value = error.value
        if value is not None:
            if not isinstance(value, (bool, int, float, str)):
                value = repr(value)
        detail = {
            "field": error.position,
            "value": value,
            "issue": error.message,
        }
        super().__init__(str(error), detail=detail)


class ResponderReturnsInvalid(Exception):
    """ResponderReturnsInvalid"""

    def __init__(self, error: Invalid) -> None:
        super().__init__(str(error))
