__all__ = ['StatusCode', 'STATUS_DESCRIPTIONS', 'STATUS_PASSED', 'STATUS_REJECTED']

from enum import IntEnum


class StatusCode(IntEnum):
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    MOVED_PERMANENTLY = 301
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502


STATUS_DESCRIPTIONS = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    204: 'No Content',
    301: 'Moved Permanently',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
}

STATUS_PASSED = [
    StatusCode.OK,
    StatusCode.CREATED,
    StatusCode.ACCEPTED,
    StatusCode.NO_CONTENT
]

STATUS_REJECTED = [
    StatusCode.MOVED_PERMANENTLY,  # django redirects to login page
    StatusCode.BAD_REQUEST,
    StatusCode.UNAUTHORIZED,
    StatusCode.FORBIDDEN,
    StatusCode.NOT_FOUND,
    StatusCode.METHOD_NOT_ALLOWED,
]
