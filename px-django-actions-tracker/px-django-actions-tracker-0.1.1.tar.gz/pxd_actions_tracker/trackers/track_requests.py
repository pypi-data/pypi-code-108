from typing import Callable, Dict, Optional, Sequence, Tuple
import traceback
import logging
from uuid import UUID
from requests import Response, PreparedRequest, ConnectionError

from ..cases import log
from ..utils import clean_data
from ..domains import ERROR, INFO


__all__ = (
    'MESSAGE_FORMAT',
    'track',

    'should_track_non_200',
    'should_track_all',
    'resolve_log_detail',
)


logger = logging.getLogger(__name__)


def MESSAGE_FORMAT(**detail):
    return f'[REQUESTS]: "{detail.get("request", {}).get("url", "")}"'


def resolve_request_data(request: PreparedRequest) -> Dict:
    return {
        'method': request.method, 'url': request.url,
        'body': clean_data(request.body),
        'headers': clean_data(dict(request.headers)),
    }


def resolve_response_data(response: Response) -> Dict:
    return {
        'status_code': response.status_code,
        'content': clean_data(response.content),
    }


def resolve_exception_data(
    error: Optional[Exception],
    response: Optional[Response]
) -> Optional[Dict]:
    if error is not None:
        return {'message': str(error), 'traceback': traceback.format_exc()}

    return None


def should_track_non_200(
    request: Optional[PreparedRequest] = None,
    response: Optional[Response] = None,
    error: Optional[Exception] = None,
    args: Sequence = (),
    kwargs: Dict = {},
) -> Tuple[bool, str]:
    should = (
        error is not None
        or
        response is None
        or
        response.status_code // 100 in (4, 5)
    )

    return should, ERROR


def should_track_all(
    request: Optional[PreparedRequest] = None,
    response: Optional[Response] = None,
    error: Optional[Exception] = None,
    args: Sequence = (),
    kwargs: Dict = {},
) -> Tuple[bool, str]:
    e, _ = should_track_non_200(response=response, error=error)

    return True, ERROR if e else INFO


def resolve_log_detail(
    request: Optional[PreparedRequest] = None,
    response: Optional[Response] = None,
    error: Optional[Exception] = None,
    args: Sequence = (),
    kwargs: Dict = {},
) -> Dict:
    request = request if request else response.request if response is not None else None
    request_data = {} if request is None else resolve_request_data(request)
    response_data = None if response is None else resolve_response_data(response)
    error_data = resolve_exception_data(error, response)

    return {
        'request': request_data, 'response': response_data,
        'error': error_data,
    }


def track(
    domain: str,
    resolver: Callable,
    args: Sequence = (),
    kwargs: Dict = {},
    message_format: Callable = MESSAGE_FORMAT,
    should_track: Callable = should_track_non_200,
    detail_resolver: Callable = resolve_log_detail,
) -> Tuple[Optional[Response], Optional[UUID]]:
    error = None
    response: Optional[Response] = None
    request: Optional[PreparedRequest] = None

    try:
        response = resolver()

        if response is not None:
            request = response.request
    except ConnectionError as e:
        response = e.response
        request = e.request
        error = e
    except Exception as e:
        error = e

    kw = dict(
        request=request, response=response, error=error,
        args=args, kwargs=kwargs,
    )
    should, domain_postfix = should_track(**kw)

    if not should:
        return response, None

    id = None
    try:
        detail = detail_resolver(**kw)
        id = log(
            (domain | domain_postfix) if domain_postfix else domain,
            message_format(**detail), detail=detail,
        )
    except Exception as e:
        logger.exception(e)

    if error is not None:
        raise error

    return response, id
