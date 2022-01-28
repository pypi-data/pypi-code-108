"""Helpers/overrides for django-allauth."""

from typing import Any, Optional

from django.conf import settings
from django.http import HttpRequest

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from oauth2_provider.models import AbstractApplication
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.scopes import BaseScopes
from oauth2_provider.views.mixins import (
    ClientProtectedResourceMixin as _ClientProtectedResourceMixin,
)
from oauthlib.common import Request as OauthlibRequest

from .apps import AppConfig


class OurSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Customised adapter that recognises other authentication mechanisms."""

    def validate_disconnect(self, account, accounts):
        """Validate whether or not the socialaccount account can be safely disconnected.

        Honours other authentication backends, i.e. ignores unusable passwords if LDAP is used.
        """
        if "django_auth_ldap.backend.LDAPBackend" in settings.AUTHENTICATION_BACKENDS:
            # Ignore upstream validation error as we do not need a usable password
            return None

        # Let upstream decide whether we can disconnect or not
        return super().validate_disconnect(account, accounts)


class OurAccountAdapter(DefaultAccountAdapter):
    """Customised adapter to allow to disable signup."""

    def is_open_for_signup(self, request):
        return get_site_preferences()["auth__signup_enabled"]


class CustomOAuth2Validator(OAuth2Validator):
    def get_additional_claims(self, request: OauthlibRequest) -> dict[str, Any]:
        # Pull together scopes from request and from access token
        scopes = request.scopes.copy()
        if request.access_token:
            scopes += request.access_token.scope.split(" ")

        claims = {}
        # Pull together claim data from all apps
        for app in AppConfig.__subclasses__():
            claims.update(app.get_additional_claims(scopes, request))

        return claims


class AppScopes(BaseScopes):
    """Scopes backend for django-oauth-toolkit gathering scopes from apps.

    Will call the respective method on all known AlekSIS app configs and
    join the results.
    """

    def get_all_scopes(self) -> dict[str, str]:
        scopes = {}
        for app in AppConfig.__subclasses__():
            scopes |= app.get_all_scopes()
        return scopes

    def get_available_scopes(
        self,
        application: Optional[AbstractApplication] = None,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs
    ) -> list[str]:
        scopes = []
        for app in AppConfig.__subclasses__():
            scopes += app.get_available_scopes()
        # Filter by allowed scopes of requesting application
        if application and application.allowed_scopes:
            scopes = list(filter(lambda scope: scope in application.allowed_scopes, scopes))
        return scopes

    def get_default_scopes(
        self,
        application: Optional[AbstractApplication] = None,
        request: Optional[HttpRequest] = None,
        *args,
        **kwargs
    ) -> list[str]:
        scopes = []
        for app in AppConfig.__subclasses__():
            scopes += app.get_default_scopes()
        # Filter by allowed scopes of requesting application
        if application and application.allowed_scopes:
            scopes = list(filter(lambda scope: scope in application.allowed_scopes, scopes))
        return scopes


class ClientProtectedResourceMixin(_ClientProtectedResourceMixin):
    """Mixin for protecting resources with client authentication as mentioned in rfc:`3.2.1`.

    This involves authenticating with any of: HTTP Basic Auth, Client Credentials and
    Access token in that order. Breaks off after first validation.

    This sub-class extends the functionality of Django OAuth Toolkit's mixin with support
    for AlekSIS's `allowed_scopes` feature. For applications that have configured allowed
    scopes, the required scopes for the view are checked to be a subset of the application's
    allowed scopes (best to be combined with ScopedResourceMixin).
    """

    def authenticate_client(self, request: HttpRequest) -> bool:
        """Return a boolean representing if client is authenticated with client credentials.

        If the view has configured required scopes, they are verified against the application's
        allowed scopes.
        """
        # Build an OAuth request so we can handle client information
        core = self.get_oauthlib_core()
        uri, http_method, body, headers = core._extract_params(request)
        oauth_request = OauthlibRequest(uri, http_method, body, headers)

        # Verify general authentication of the client
        if not core.server.request_validator.authenticate_client(oauth_request):
            # Client credentials were invalid
            return False

        # Verify scopes of configured application
        # The OAuth request was enriched with a reference to the Application when using the
        #  validator above.
        required_scopes = set(self.get_scopes() or [])
        allowed_scopes = set(AppScopes().get_available_scopes(oauth_request.client) or [])
        return required_scopes.issubset(allowed_scopes)
