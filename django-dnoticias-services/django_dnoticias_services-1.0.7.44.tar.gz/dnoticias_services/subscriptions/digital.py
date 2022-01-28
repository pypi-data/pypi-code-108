import requests

from django.conf import settings

from dnoticias_services.utils.request import get_headers
from dnoticias_services.subscriptions.base import BaseSubscriptionRequest


class GetRolesSelect2View(BaseSubscriptionRequest):
    """
    Gets all the non-opened notifications for a given user by email.
    """
    def __call__(self, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.get(
            settings.ROLES_SELECT2_API_URL,
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response


class GetRolesView(BaseSubscriptionRequest):
    """
    Gets all the non-opened notifications for a given user by email.
    """
    def __call__(self, email, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.get(
            settings.ROLES_API_URL,
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response


get_roles = GetRolesView()
get_roles_select2 = GetRolesSelect2View()


__all__ = ("get_roles_select2", "get_roles", )
