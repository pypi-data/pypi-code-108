"""
Расширения Django Backend's для аутентификации пользователей
"""
import logging
from typing import Dict, Any, Optional, Tuple

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from keycloak.exceptions import KeycloakAuthenticationError
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from vtb_http_interaction.keycloak_gateway import KeycloakGateway, UserCredentials

from vtb_django_utils.keycloak_utils import keycloak_config
from vtb_django_utils.utils.settings import get_settings

UserModel = get_user_model()


class KeycloakOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """ Django Backend с использованием open id connect """

    def get_userinfo(self, access_token, id_token, payload):
        user_info = super().get_userinfo(access_token, id_token, payload)

        token_info = _decode_token(access_token)
        super_admin, svc_admin = token_admin_info(token_info)

        user_info['super_admin'] = super_admin
        user_info['svc_admin'] = svc_admin
        return user_info

    def create_user(self, claims):
        user = super().create_user(claims)

        _set_user_flags(user, claims)
        user.is_active = True
        user.save()

        return user

    def update_user(self, user, claims):
        _set_user_flags(user, claims)
        user.save()

        return user


class KeycloakBackend(ModelBackend):
    """ Django Backend для аутентификации пользователей с использованием логина/пароля из keycloak """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if username is None or password is None:
                return None

            token_info = _keycloak_validate(username, password)
            if token_info is None:
                return None

            user_name = token_info.get('preferred_username', token_info['sub'])

            user, _ = UserModel.objects.get_or_create(
                **{UserModel.USERNAME_FIELD: user_name}
            )

            user = prepare_user(user, token_info)
            user.save()

            if self.user_can_authenticate(user):
                return user

            return None
        except Exception as ex:  # pylint: disable=broad-except
            logger = logging.getLogger(__name__)
            logger.exception(ex)

            return None


def token_admin_info(token_info: Optional[Dict[str, Any]]) -> Tuple[bool, bool]:
    """
    Определение ролей администратора для пользователя
    """
    # Пользователь имеет роль глобального администратора
    super_admin = False
    # Пользователь имеет роль администратора сервиса
    svc_admin = False

    realm_access = token_info.get('realm_access', None)
    if realm_access is not None:
        roles = realm_access.get('roles', None)

        if roles is not None:
            user_keycloak_roles = set(roles)

            expected_super_admin = get_settings('KEYCLOAK_SUPER_ADMIN_ROLES', None) or get_settings(
                'KEY_CLOAK_SUPER_ADMIN_ROLES', None) or []
            expected_super_admin = set(expected_super_admin)

            expected_svc_admin = get_settings('KEYCLOAK_SVC_ADMIN_ROLES', None) or get_settings(
                'KEY_CLOAK_SVC_ADMIN_ROLES', None) or []
            expected_svc_admin = set(expected_svc_admin)
            super_admin = len(expected_super_admin & user_keycloak_roles) > 0
            svc_admin = len(expected_svc_admin & user_keycloak_roles) > 0

    return super_admin, svc_admin


def prepare_user(user, token_info: Optional[Dict[str, Any]]):
    """
    Подготовка пользователя на основе данных из keycloak
    """
    super_admin, svc_admin = token_admin_info(token_info)
    is_admin = super_admin or svc_admin

    user.is_staff = is_admin
    user.is_superuser = super_admin
    if hasattr(user, 'is_svc_admin'):
        user.is_svc_admin = svc_admin

    user.is_active = True

    user.email = token_info.get('email', '')

    user.first_name = token_info.get('given_name', token_info.get('preferred_username'))
    user.last_name = token_info.get('family_name', '')

    return user


def _keycloak_validate(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Валидация пользователя в Keycloak
    """
    with KeycloakGateway(keycloak_config) as gateway:
        try:
            gateway.obtain_token(UserCredentials(username, password), grant_type=("password",))
        except KeycloakAuthenticationError:
            return None

        token_info = gateway.decode_token(token=gateway.access_token,
                                          key=gateway.public_key)

        return token_info


def _set_user_flags(user, claims):
    is_admin = claims['super_admin'] or claims['svc_admin']

    user.is_staff = is_admin
    user.is_superuser = is_admin

    return user


def _decode_token(access_token: str) -> Optional[Dict[str, Any]]:
    with KeycloakGateway(keycloak_config) as gateway:
        token_info = gateway.decode_token(token=access_token,
                                          key=gateway.public_key)

        return token_info
