from urllib.parse import urlparse

from django.template.defaultfilters import truncatechars
from django.urls.exceptions import Resolver404
from django.urls import resolve
from django.utils.timezone import now

from ipware.ip import get_client_ip

from security.enums import LoggerName
from security.config import settings
from security.backends.signals import (
    input_request_started, input_request_finished, input_request_error,
    output_request_started, output_request_finished, output_request_error,
)
from security.logging.common import SecurityLogger

from .utils import get_headers, clean_headers, clean_queries, clean_body


class InputRequestLogger(SecurityLogger):

    name = LoggerName.INPUT_REQUEST

    def __init__(self, hide_request_body=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hide_request_body = hide_request_body

    def log_request(self, request):
        user_pk = request.user.pk if hasattr(request, 'user') and request.user.is_authenticated else None
        path = truncatechars(request.path, 200)

        try:
            view_slug = resolve(request.path_info, getattr(request, 'urlconf', None)).view_name
        except Resolver404:
            view_slug = None

        self.data.update(dict(
            request_headers=clean_headers(get_headers(request)),
            request_body=(
                settings.SENSITIVE_DATA_REPLACEMENT
                if request.body and self.hide_request_body
                else clean_body(request.body, settings.LOG_REQUEST_BODY_LENGTH)
            ),
            user_id=user_pk,
            method=request.method.upper()[:7],
            host=request.get_host(),
            path=path,
            queries=clean_queries(request.GET.dict()),
            is_secure=request.is_secure(),
            ip=get_client_ip(request)[0],
            start=now(),
            view_slug=view_slug
        ))
        input_request_started.send(sender=InputRequestLogger, logger=self)

    def log_response(self, request, response):
        user_pk = request.user.pk if hasattr(request, 'user') and request.user.is_authenticated else None
        if (not response.streaming
                and (settings.LOG_RESPONSE_BODY_CONTENT_TYPES is None
                     or response.get('content-type', '').split(';')[0] in settings.LOG_RESPONSE_BODY_CONTENT_TYPES)):
            response_body = clean_body(response.content, settings.LOG_RESPONSE_BODY_LENGTH)
        else:
            response_body = None

        self.data.update(
            dict(
                stop=now(),
                response_code=response.status_code,
                response_headers=clean_headers(dict(response.items())),
                response_body=response_body,
                user_id=user_pk,
            )
        )
        input_request_finished.send(sender=InputRequestLogger, logger=self)

    def log_exception(self, ex_tb):
        self.data.update(dict(
            error_message=ex_tb
        ))
        input_request_error.send(sender=InputRequestLogger, logger=self)


class OutputRequestLogger(SecurityLogger):

    name = LoggerName.OUTPUT_REQUEST

    def log_request(self, request):
        from .utils import get_logged_params

        parsed_url = urlparse(request.url)
        self.data.update(dict(
            is_secure=parsed_url.scheme == 'https',
            host=parsed_url.netloc,
            path=parsed_url.path,
            method=request.method.upper()[:7],
            queries=clean_queries(get_logged_params(request.url)),
            start=now(),
            request_headers=clean_headers(dict(request.headers.items())),
            request_body=clean_body(request.body, settings.LOG_REQUEST_BODY_LENGTH),
        ))
        output_request_started.send(sender=OutputRequestLogger, logger=self)

    def log_response(self, response):
        self.data.update(dict(
            stop=now(),
            response_code=response.status_code,
            response_headers=clean_headers(dict(response.headers.items())),
            response_body=clean_body(response.content, settings.LOG_RESPONSE_BODY_LENGTH)
        ))
        output_request_finished.send(sender=OutputRequestLogger, logger=self)

    def log_exception(self, ex_tb):
        self.data.update(dict(
            error_message=ex_tb,
            stop=now(),
        ))
        output_request_error.send(sender=InputRequestLogger, logger=self)
