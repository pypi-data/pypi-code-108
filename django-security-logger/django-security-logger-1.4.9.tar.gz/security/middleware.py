import traceback

from django import http
from django.conf import settings as django_settings
from django.urls import is_valid_path, get_callable, get_resolver, set_urlconf, Resolver404

from ipware.ip import get_client_ip

from security.logging.requests.logger import InputRequestLogger
from security.throttling.exception import ThrottlingException

from .config import settings
from .utils import get_throttling_validators


def get_view_from_request_or_none(request):
    try:
        if hasattr(request, 'urlconf'):
            urlconf = request.urlconf
            set_urlconf(urlconf)
            resolver = get_resolver(urlconf)
        else:
            resolver = get_resolver()
        return resolver.resolve(request.path_info)[0]
    except Resolver404:
        return None


class LogMiddleware:

    response_redirect_class = http.HttpResponsePermanentRedirect

    def __init__(self, get_response=None):
        self.base_get_response = get_response
        super().__init__()

    def __call__(self, request):
        view = get_view_from_request_or_none(request)
        if (get_client_ip(request)[0] not in settings.LOG_REQUEST_IGNORE_IP
                and request.path not in settings.LOG_REQUEST_IGNORE_URL_PATHS
                and not getattr(view, 'log_exempt', False)):

            with InputRequestLogger(hide_request_body=getattr(view, 'hide_request_body', False)) as logger:
                request.input_request_logger = logger
                return self.get_response(request, logger)
        else:
            return self.get_response(request)

    def get_response(self, request, input_request_logger=None):
        response = self.process_request(request, input_request_logger)
        response = response or self.base_get_response(request)
        return self.process_response(request, response, input_request_logger)

    def process_request(self, request, input_request_logger=None):
        if input_request_logger:
            input_request_logger.log_request(request)

        # Return a redirect if necessary
        if self.should_redirect_with_slash(request):
            return self.response_redirect_class(self.get_full_path_with_slash(request))

    def get_full_path_with_slash(self, request):
        """
        Return the full path of the request with a trailing slash appended.

        Raise a RuntimeError if settings.DEBUG is True and request.method is
        POST, PUT, or PATCH.
        """
        new_path = request.get_full_path(force_append_slash=True)
        if django_settings.DEBUG and request.method in {'POST', 'PUT', 'PATCH'}:
            raise RuntimeError(
                "You called this URL via %(method)s, but the URL doesn't end "
                "in a slash and you have SECURITY_APPEND_SLASH set. Django can't "
                "redirect to the slash URL while maintaining %(method)s data. "
                "Change your form to point to %(url)s (note the trailing "
                "slash), or set SECURITY_APPEND_SLASH=False in your Django settings." % {
                    'method': request.method,
                    'url': request.get_host() + new_path,
                }
            )
        return new_path

    def should_redirect_with_slash(self, request):
        """
        Return True if settings.APPEND_SLASH is True and appending a slash to
        the request path turns an invalid path into a valid one.
        """
        if settings.APPEND_SLASH and not request.get_full_path().endswith('/'):
            urlconf = getattr(request, 'urlconf', None)
            return (
                not is_valid_path(request.path_info, urlconf) and
                is_valid_path('{}/'.format(request.path_info), urlconf)
            )
        return False

    def _render_throttling(self, request, exception):
        return get_callable(settings.THROTTLING_FAILURE_VIEW)(request, exception)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        throttling_validators = getattr(callback, 'throttling_validators', None)
        if throttling_validators is None:
            throttling_validators = get_throttling_validators('default_validators')

        try:
            for validator in throttling_validators:
                validator.validate(request)
        except ThrottlingException as exception:
            return self.process_exception(request, exception)

    def process_response(self, request, response, input_request_logger=None):
        if input_request_logger:
            input_request_logger.log_response(request, response)
        return response

    def process_exception(self, request, exception):
        input_request_logger = getattr(request, 'input_request_logger', None)
        if input_request_logger:
            input_request_logger.log_exception(traceback.format_exc())
            if isinstance(exception, ThrottlingException):
                return self._render_throttling(request, exception)
