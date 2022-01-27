"""
Расширения DRF Authentication's для аутентификации пользователей
"""
import logging
from typing import Dict, Any

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from vtb_http_interaction.http_utils import parse_authorization_header
from vtb_http_interaction.keycloak_gateway import KeycloakGateway

from vtb_django_utils.backends import prepare_user
from vtb_django_utils.keycloak_utils import keycloak_config

logger = logging.getLogger(__name__)


class KeycloakUser:
    """
    Пользователь Keycloak
    """
    id = None
    pk = None
    realm_access = None
    resource_access = None

    username = ''
    email = ''
    first_name = ''
    last_name = ''
    preferred_username = ''

    is_staff = False
    is_active = False
    is_superuser = False
    is_svc_admin = False

    def __str__(self):
        return 'KeycloakUser'

    @property
    def is_anonymous(self):
        """ anonymous flag """
        return False

    @property
    def is_authenticated(self):
        """ authenticated flag """
        return True

    def get_username(self):
        """ username """
        return self.username


class KeycloakAuthentication(BaseAuthentication):
    """
    Authorization: Bearer 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Bearer'

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        authorization_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not authorization_header:
            return None

        key, token = parse_authorization_header(authorization_header)

        if key.lower() != self.keyword.lower():
            return None

        return _authenticate_credentials(token)

    def authenticate_header(self, request):
        return self.keyword


def _authenticate_credentials(access_token):
    with KeycloakGateway(keycloak_config) as gateway:
        try:
            token_info = gateway.decode_token(token=access_token, key=gateway.public_key)
        except Exception as ex:
            logger.exception(ex)
            raise exceptions.AuthenticationFailed('Invalid access token.') from ex

        user = _create_keycloak_user(token_info)

        return user, None


def _create_keycloak_user(token_info: Dict[str, Any]) -> KeycloakUser:
    user = KeycloakUser()
    user.username = token_info['sub']
    user.realm_access = token_info.get('realm_access', None)
    user.resource_access = token_info.get('resource_access', None)
    user.preferred_username = token_info.get('preferred_username', '')
    user = prepare_user(user, token_info)

    return user
