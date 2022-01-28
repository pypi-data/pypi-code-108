import requests

from django.conf import settings

from dnoticias_services.utils.request import get_headers
from .base import BaseEditionsRequest


class GetUserConsumables(BaseEditionsRequest):
    def __call__(self, email, api_key=None, timeout=None):
        self.set_api_url(settings.EDITIONS_USER_CONSUMABLES_API_URL, (email, ))
        return self.get({}, api_key, timeout)


get_user_consumables = GetUserConsumables()

__all__ = ("get_user_consumables", )