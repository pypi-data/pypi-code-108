from typing import Callable, Dict, Optional, Sequence, Tuple
import traceback
import logging
from uuid import UUID
from functools import wraps
from px_domains import Domain

from django.http import HttpRequest, HttpResponse

from ..cases import log
from ..utils import clean_data, get_ip_address
from ..domains import ERROR, INFO, VIEW


__all__ = (
    'MESSAGE_FORMAT',

    'track',
    'track_middleware',
    'decorate',
    'create_middleware',

    'should_track_non_200',
    'should_track_all',
)


logger = logging.getLogger(__name__)


HEADER_PREFIX = 'HTTP_'
HEADER_PREFIX_LENGTH = len(HEADER_PREFIX)
MESSAGE_FORMAT = '[VISIT]: "{request[path]}"'.format


def resolve_request_data(request: HttpRequest) -> Dict:
    user = None if request.user.is_anonymous else request.user

    return {
        'ip': get_ip_address(request),
        'host': request.get_host(),
        'method': request.method,
        'path': request.path,
        'content_type': request.content_type,
        'user': (
            {'id': None, 'name': 'Anonymous'}
            if user is None else
            {'id': user.id, 'name': user.get_username()}
        ),
        'data': clean_data(
            request.data
            if hasattr(request, 'data') else
            request.POST
            if hasattr(request, 'POST') else
            None
        ),
        'query_params': clean_data(dict(request.GET.lists())),
        'headers': clean_data({
            key[HEADER_PREFIX_LENGTH:]: value
            for key, value in request.META.items()
            if key.startswith(HEADER_PREFIX)
        })
    }


def resolve_response_data(response: HttpResponse) -> Dict:
    rendered_content = None

    if response.streaming:
        rendered_content = None
    elif hasattr(response, 'rendered_content'):
        rendered_content = response.rendered_content
    else:
        rendered_content = response.content

    return {
        'content': clean_data(rendered_content),
        'status_code': response.status_code,
    }


def resolve_exception_data(
    error: Optional[Exception],
    response: Optional[HttpResponse]
) -> Optional[Dict]:
    if error is not None:
        return {'message': str(error), 'traceback': traceback.format_exc()}
    if response is not None and response.status_code // 100 == 5:
        return {
            'message': 'Error',
            'traceback': ''.join(traceback.format_list(response._init_stack))
        }

    return None


def should_track_non_200(
    request: HttpRequest,
    response: Optional[HttpResponse] = None,
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
    request: HttpRequest,
    response: Optional[HttpResponse] = None,
    error: Optional[Exception] = None,
    args: Sequence = (),
    kwargs: Dict = {},
) -> Tuple[bool, str]:
    e, _ = should_track_non_200(request, response=response, error=error)

    return True, ERROR if e else INFO


def resolve_log_detail(
    request: HttpRequest,
    response: Optional[HttpResponse] = None,
    error: Optional[Exception] = None,
    args: Sequence = (),
    kwargs: Dict = {},
) -> Dict:
    request_data = resolve_request_data(request)
    response_data = response and resolve_response_data(response) or None
    error_data = resolve_exception_data(error, response)

    return {
        'request': request_data, 'response': response_data,
        'error': error_data,
    }


def track(
    domain: str,
    request: HttpRequest,
    response: Optional[HttpResponse] = None,
    error: Optional[Exception] = None,
    args: Sequence = (),
    kwargs: Dict = {},
    message_format: Callable = MESSAGE_FORMAT,
    should_track: Callable = should_track_non_200,
    detail_resolver: Callable = resolve_log_detail,
) -> Optional[UUID]:
    kw = dict(response=response, error=error, args=args, kwargs=kwargs)
    should, domain_postfix = should_track(request, **kw)

    if not should:
        return None

    try:
        detail = detail_resolver(request, **kw)

        return log(
            (domain | domain_postfix) if domain_postfix else domain,
            message_format(**detail), detail=detail,
        )
    except Exception as e:
        logger.exception(e)

    return None


def track_middleware(
    domain: str,
    get_response: Callable,
    request: HttpRequest,
    tracker: Callable = track,
    args: Sequence = [],
    kwargs: dict = {},
) -> Tuple[HttpResponse, Optional[UUID]]:
    error = None
    response = None

    try:
        response = get_response(request, *args, **kwargs)
    except Exception as e:
        error = e

    try:
        log_id = tracker(
            domain,
            request,
            response=response,
            error=error,
            args=args,
            kwargs=kwargs,
        )
    except Exception as e:
        logger.exception(e)

    if error is not None:
        raise error

    return response, log_id


def decorate(domain: Domain = VIEW, tracker: Callable = track):
    def decorator(f: Callable):
        @wraps(f)
        def runner(request: HttpRequest, *args, **kwargs):
            response, _ = track_middleware(
                domain, f, request, tracker=tracker, args=args, kwargs=kwargs
            )

            return response

        return runner

    return decorator


def create_middleware(base_domain: Domain = VIEW, tracker: Callable = track):
    def middleware(get_response):
        def runner(request: HttpRequest, *args, **kwargs):
            domain = base_domain

            if request.resolver_match is not None:
                domain = domain | Domain(request.resolver_match.view_name)

            response, _ = track_middleware(
                domain, get_response, request, tracker=tracker,
                args=args, kwargs=kwargs
            )

            return response

        return runner

    return middleware
