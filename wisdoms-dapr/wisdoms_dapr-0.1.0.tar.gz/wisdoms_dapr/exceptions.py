"""
Service Common Exceptions
"""

import typing

from fastapi.exceptions import HTTPException


class BaseServiceException(Exception):
    """Base Service Exception --- all service exception base class"""

    detail: typing.Any = 'base service exception'

    def __init__(self, detail: str = ''):

        if detail:
            self.detail = detail

    def __str__(self):
        return f'Service Exception: {self.detail}'
        

# ************ Service Error Exceptions ************
class ServiceErrorException(BaseServiceException):
    """Service Error Exception"""

    detail = 'service error exception'

class InvalidConfigError(ServiceErrorException):
    """Invalid Config"""

    detail = "invalid config"
    

# ************ Service Exception ************
class ServiceException(HTTPException, BaseServiceException):
    """Service Exception"""

    status_code: int = 400

    def __init__(self, status_code: typing.Optional[int] = None, detail: typing.Any = None, headers: typing.Optional[dict[str, typing.Any]] = None) -> None:
        if detail:
            self.detail = detail

        if status_code and status_code > 0:
            self.status_code = status_code

        super().__init__(self.status_code, detail=self.detail, headers=headers)

class ValidationException(ServiceException):
    """Validation Exception"""

    detail = 'validation failed'


class ParameterException(ServiceException):
    """Parameter Exception"""

    detail = 'invalid parameter'


class DBException(ServiceException):
    """DB Exception"""

    msg = "database error"
    status = 500
