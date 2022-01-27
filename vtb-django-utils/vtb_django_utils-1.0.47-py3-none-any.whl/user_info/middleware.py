from datetime import datetime

from django.contrib.auth import get_user_model

from vtb_django_utils.utils.consts import DATETIME_SHORT_FORMAT
from vtb_django_utils.utils.db import get_model_field_names
from .info import set_user_info


class UserInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.fields = get_model_field_names(get_user_model(), exclude=('password', 'last_login'))

    def __call__(self, request):
        self._user_info_set(request)
        response = self.get_response(request)
        return response

    @staticmethod
    def _format_value(value):
        if isinstance(value, datetime):
            return value.strftime(DATETIME_SHORT_FORMAT)
        return value

    def _user_info_set(self, request):
        set_user_info(
            {field_name: self._format_value(getattr(request.user, field_name))
             for field_name in self.fields
             if hasattr(request.user, field_name)}
        )
