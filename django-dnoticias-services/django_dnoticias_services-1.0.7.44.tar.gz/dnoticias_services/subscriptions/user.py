import requests

from django.conf import settings

from dnoticias_services.utils.request import get_headers
from dnoticias_services.subscriptions.base import BaseSubscriptionRequest


class BaseUserRequest(BaseSubscriptionRequest):
    def get_user_notifications_url(self):
        return settings.USER_NOTIFICATION_API_URL
    def get_user_components_url(self):
        return settings.USER_COMPONENTS_API_URL
    def get_user_subscriptions_url(self):
        return settings.USER_SUBSCRIPTIONS_API_URL


class GetUserNotifications(BaseUserRequest):
    """
    Gets all the non-opened notifications for a given user by email.
    """
    def __call__(self, email, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.get(
            self.get_user_notifications_url().format(email),
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response


class GetUserComponents(BaseUserRequest):
    """
    Gets all the components for a given user by email.
    """
    def __call__(self, email, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.get(
            self.get_user_components_url().format(email),
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response


class GetLastUserSubscription(BaseUserRequest):
    """
    Gets the last user subscription
    """
    def __call__(self, email, api_key=None):
        _api_key = api_key or self.api_key

        response = requests.get(
            self.get_user_subscriptions_url().format(email),
            headers=get_headers(_api_key),
        )

        response.raise_for_status()

        return response


class GetUserRoles(BaseUserRequest):
    """
    Gets all the roles for an user by his email
    """
    def __call__(self, email, api_key=None, timeout=None):
        self.set_api_url(settings.USER_ROLES_API_URL, (email, ))
        return self.get(api_key, timeout)


get_user_notifications = GetUserNotifications()
get_user_components = GetUserComponents()
get_last_user_subscription = GetLastUserSubscription()
get_user_roles = GetUserRoles()

__all__ = ("get_user_notifications", "get_user_components", "get_user_roles", )
