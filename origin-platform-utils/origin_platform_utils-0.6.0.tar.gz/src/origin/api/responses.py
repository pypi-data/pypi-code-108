import rapidjson
from functools import cached_property
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, TypeVar, Generic, Tuple

from origin.serialize import json_serializer

from .cookies import Cookie


TResponseModel = TypeVar('TResponseModel')


@dataclass
class HttpResponse(Generic[TResponseModel], Exception):
    """
    TODO
    """

    # HTTP Status Code
    status: int

    # Response body
    body: Optional[Union[str, bytes]] = \
        field(default=None)

    # Response body JSON
    json: Optional[Dict[str, Any]] = \
        field(default=None)

    # Response model
    model: Optional[TResponseModel] = \
        field(default=None)

    # Response headers
    headers: Dict[str, str] = \
        field(default_factory=dict)

    # Response cookies
    cookies: Union[List[Cookie], Tuple[Cookie, ...]] = \
        field(default_factory=tuple)

    @cached_property
    def actual_headers(self) -> Dict[str, str]:
        """
        TODO
        """
        headers = {}
        headers.update(self.headers)

        return headers

    @cached_property
    def actual_body(self) -> Optional[Union[str, bytes]]:
        """
        TODO
        """
        if self.body is not None:
            return self.body
        elif self.json is not None:
            return rapidjson.dumps(self.json)
        elif self.model is not None:
            return json_serializer.serialize(self.model)
        else:
            return None

    @cached_property
    def actual_mimetype(self) -> Optional[Union[str, bytes]]:
        """
        TODO
        """
        if self.body is not None:
            return 'text/html'
        elif self.json is not None:
            return 'application/json'
        elif self.model is not None:
            return 'application/json'
        else:
            return 'text/html'


class HttpError(HttpResponse):
    """
    TODO
    """
    def __init__(self, msg: str, status: int, **kwargs):
        kwargs.setdefault('body', f'{status} {msg}')
        super(HttpError, self).__init__(status=status, **kwargs)


class MovedPermanently(HttpResponse):
    """
    HTTP 301 Moved Permanently.
    """
    def __init__(self, url, **kwargs):
        super(MovedPermanently, self).__init__(
            status=301, headers={'Location': url}, **kwargs)


class TemporaryRedirect(HttpResponse):
    """
    HTTP 307 Temporary Redirect.
    """
    def __init__(self, url, **kwargs):
        super(TemporaryRedirect, self).__init__(
            status=307, headers={'Location': url}, **kwargs)


class BadRequest(HttpError):
    """
    HTTP 400 Bad Request.

    Returned by the API in case the client invokes an endpoint but
    validation of input data (either query parameters or POST body) fails.

    This response should be accompanied by the validation errors.
    """
    def __init__(self, **kwargs):
        super(BadRequest, self).__init__(
            status=400, msg='Bad Request', **kwargs)


class Unauthorized(HttpError):
    """
    HTTP 401 Unauthorized.

    Returned by the API in case the client provides an invalid token,
    ie. a token that is expired, belongs to a user that doesn't exist etc.

    This is an indication that the client must acquire a new token.
    """
    def __init__(self, msg: str = 'Unauthorized', **kwargs):
        super(Unauthorized, self).__init__(
            status=401, msg=msg, **kwargs)


class Forbidden(HttpError):
    """
    HTTP 403 Forbidden.

    Returned by the API in case the client provides a token without
    the necessary scope(s).
    """
    def __init__(self, msg: str = 'Forbidden', **kwargs):
        super(Forbidden, self).__init__(
            status=403, msg=msg, **kwargs)


class InternalServerError(HttpError):
    """
    HTTP 500 Internal Server Error.
    """
    def __init__(self, msg: str = 'Internal Server Error', **kwargs):
        super(InternalServerError, self).__init__(
            status=500, msg=msg, **kwargs)
