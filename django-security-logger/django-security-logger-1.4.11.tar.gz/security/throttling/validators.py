from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import resolve, Resolver404

from ipware.ip import get_client_ip

from security.backends.reader import get_count_input_requests
from security.enums import InputRequestSlug

from .exception import ThrottlingException


class ThrottlingValidator:

    def __init__(self, timeframe, throttle_at, description):
        self.timeframe = timeframe
        self.throttle_at = throttle_at
        self.description = description

    def validate(self, request):
        if not getattr(settings, 'TURN_OFF_THROTTLING', False) and not self._validate(request):
            raise ThrottlingException(self.description)

    def _validate(self, request):
        raise NotImplementedError

    def __repr__(self):
        return '<{} (timeframe={}, throttle_at={}, description={})>'.format(
            self.__class__.__name__, self.timeframe, self.throttle_at, self.description
        )


class PerRequestThrottlingValidator(ThrottlingValidator):

    def __init__(self, timeframe, throttle_at, description=_('Slow down')):
        super().__init__(timeframe, throttle_at, description)

    def _validate(self, request):
        try:
            view_slug = resolve(request.path_info, getattr(request, 'urlconf', None)).view_name
        except Resolver404:
            view_slug = None

        current_logger = getattr(request, 'input_request_logger', None)
        return get_count_input_requests(
            from_time=timezone.now() - timedelta(seconds=self.timeframe),
            ip=get_client_ip(request)[0],
            path=request.path,
            method=request.method.upper(),
            view_slug=view_slug,
            exclude_log_id=current_logger.id if current_logger else None
        ) < self.throttle_at


class LoginThrottlingValidator(ThrottlingValidator):

    slug = None

    def _validate(self, request):
        current_logger = getattr(request, 'input_request_logger', None)
        return get_count_input_requests(
            from_time=timezone.now() - timedelta(seconds=self.timeframe),
            ip=get_client_ip(request)[0],
            path=request.path,
            slug=self.slug,
            exclude_log_id=current_logger.id if current_logger else None
        ) < self.throttle_at


class UnsuccessfulLoginThrottlingValidator(LoginThrottlingValidator):

    slug = InputRequestSlug.UNSUCCESSFUL_LOGIN_REQUEST

    def __init__(self, timeframe, throttle_at, description=_('Too many login attempts')):
        super().__init__(timeframe, throttle_at, description)


class SuccessfulLoginThrottlingValidator(LoginThrottlingValidator):

    slug = InputRequestSlug.SUCCESSFUL_LOGIN_REQUEST

    def __init__(self, timeframe, throttle_at, description=_('You have logged in too many times')):
        super().__init__(timeframe, throttle_at, description)


class UnSuccessfulTwoFactorCodeVerificationThrottlingValidator(LoginThrottlingValidator):

    slug = InputRequestSlug.UNSUCCESSFUL_2FA_CODE_VERIFICATION_REQUEST

    def __init__(self, timeframe, throttle_at, description=_('Too many login attempts')):
        super().__init__(timeframe, throttle_at, description)


class SuccessfulTwoFactorCodeVerificationThrottlingValidator(LoginThrottlingValidator):

    slug = InputRequestSlug.SUCCESSFUL_2FA_CODE_VERIFICATION_REQUEST

    def __init__(self, timeframe, throttle_at, description=_('You have logged in too many times')):
        super().__init__(timeframe, throttle_at, description)
