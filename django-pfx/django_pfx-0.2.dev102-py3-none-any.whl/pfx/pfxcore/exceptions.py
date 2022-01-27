from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from .shortcuts import f


class APIError(Exception):
    def __init__(self, message, status=400, **kwargs):
        self.status = status
        self.data = dict(message=message, **kwargs)

    @property
    def response(self):
        return JsonResponse(self.data, status=self.status)


class ModelNotFoundAPIError(APIError):
    def __init__(self, model, **kwargs):
        super().__init__(
            f(_("{model} not found."), model=model._meta.verbose_name),
            status=404, **kwargs)


class AuthenticationError(APIError):
    def __init__(self, **kwargs):
        super().__init__(
            f(_("Authentication Error")),
            status=401, **kwargs)


class UnauthorizedError(APIError):
    def __init__(self, **kwargs):
        super().__init__(
            f(_("Unauthorized")),
            status=401, **kwargs)


class ForbiddenError(APIError):
    def __init__(self, **kwargs):
        super().__init__(
            f(_("Forbidden")),
            status=403, **kwargs)
