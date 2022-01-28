import logging
import base64
import json
from distutils.util import strtobool
from uuid import uuid4

from django.contrib.auth import get_backends, get_user_model
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.conf import settings

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from keycloak import KeycloakAdmin, KeycloakOpenID
from dnoticias_services.mail import mail

User = get_user_model()
logger = logging.getLogger(__name__)


class BaseKeyCloak(object):
    def __init__(self):
        self.server_url = getattr(settings, "KEYCLOAK_SERVER_URL", "")
        self.admin_realm_name = getattr(settings, "KEYCLOAK_ADMIN_REALM_NAME", "")
        self.user_realm_name = getattr(settings, "KEYCLOAK_USER_REALM_NAME", "") or self.admin_realm_name
        self.username = getattr(settings, "KEYCLOAK_ADMIN_USERNAME", "")
        self.password = getattr(settings, "KEYCLOAK_ADMIN_PASSWORD", "")
        self.client_id = getattr(settings, "KEYCLOAK_CLIENT_ID", "")
        self.client_secret_key = getattr(settings, "KEYCLOAK_CLIENT_SECRET_KEY", "")

        self.keycloak_admin = KeycloakAdmin(
                                server_url=self.server_url,
                                username=self.username,
                                password=self.password,
                                realm_name=self.admin_realm_name,
                                user_realm_name=self.user_realm_name,
                                verify=True
                            )

        self.keycloak_openid = KeycloakOpenID(
                                server_url=self.server_url,
                                client_id=self.client_id,
                                realm_name=self.user_realm_name,
                                client_secret_key=self.client_secret_key,
                                verify=True
                            )

    def get_backend(self):
        backends = get_backends()

        for backend in backends:
            if issubclass(backend.__class__, OIDCAuthenticationBackend):
                return backend

        raise ValueError("No backend that is subclass of OIDCAuthenticationBackend")


class UpdateUser(BaseKeyCloak):
    """
    Updates an user in both sides (Keycloak and backends).
    """
    def __call__(self, email, first_name='', last_name='', enabled=True, is_staff=False, is_superuser=False, max_sessions=2, update_attributes=True):
        self.keycloak_admin.refresh_token()
        user_id_keycloak = self.keycloak_admin.get_user_id(email)

        if user_id_keycloak is None:
            message = "That user doesn't exists in keycloak"
            raise SuspiciousOperation(message)

        payload = {
            'firstName': first_name,
            'lastName': last_name,
            'enabled': enabled,
        }

        if update_attributes:
            payload['attributes'] = {
                'is_staff': is_staff,
                'is_superuser': is_superuser,
                'max_sessions': max_sessions,
            }

        self.keycloak_admin.update_user(
            user_id=user_id_keycloak,
            payload=payload,
        )

        user_info = self.keycloak_admin.get_user(user_id_keycloak)

        backend = self.get_backend()
        claims_verified = backend.verify_claims(user_info)

        if not claims_verified:
            message = 'Claims verification failed'
            raise SuspiciousOperation(message)

        users = backend.filter_users_by_claims(user_info)

        user_info['given_name'] = first_name
        user_info['family_name'] = last_name
        user_info['is_active'] = enabled
        user_info['is_staff'] = is_staff
        user_info['is_superuser'] = is_superuser

        if len(users) == 1:
            return backend.update_user(users[0], user_info)
        else:
            message = 'Cannot update the user. Users returned zero or more than one entry.'
            raise SuspiciousOperation(message)

        return None


class CreateUser(BaseKeyCloak):
    def __call__(self, email, first_name='', last_name='', enabled=True, email_verified=False, password=None, temporary_password=True, is_staff=False, is_superuser=False, send_email_to_user=False, max_sessions=2, **kwargs):
        self.keycloak_admin.refresh_token()

        user_id_keycloak = self.keycloak_admin.get_user_id(email)

        if user_id_keycloak is None:
            if temporary_password:
                password = User.objects.make_random_password(length=14)

            credentials = {
                "type": "password",
            }

            if kwargs.get('credential_data') and kwargs.get('secret_data'):
                salt = kwargs['secret_data'].get('salt', '')
                salt = salt.encode()
                kwargs['secret_data']['salt'] = base64.b64encode(salt).decode()
                credentials['credentialData'] = json.dumps(kwargs.get('credential_data'))
                credentials['secretData'] = json.dumps(kwargs.get('secret_data'))
            else:
                credentials['value'] = str(password)
            
            credentials["temporary"] = temporary_password

            user_id_keycloak = self.keycloak_admin.create_user(
                {
                    "email": email,
                    "username": email,
                    "firstName": first_name,
                    "lastName": last_name,
                    "enabled": enabled,
                    "emailVerified" : email_verified,
                    "credentials": [credentials],
                    "realmRoles": ["user_default",],
                    "attributes": {
                        "is_staff": is_staff,
                        "is_superuser": is_superuser,
                        "max_sessions" : max_sessions,
                    }
                }
            )

        user_info = self.keycloak_admin.get_user(user_id_keycloak)
        self.normalize_user_info(user_info)

        email = user_info.get('email')

        backend = self.get_backend()
        claims_verified = backend.verify_claims(user_info)
        if not claims_verified:
            msg = 'Claims verification failed'
            raise SuspiciousOperation(msg)

        # email based filtering
        users = backend.filter_users_by_claims(user_info)

        user_info['given_name'] = first_name
        user_info['family_name'] = last_name
        user_info['is_active'] = enabled
        user_info['is_staff'] = is_staff
        user_info['is_superuser'] = is_superuser

        if len(users) == 1:
            return backend.update_user(users[0], user_info)
        elif len(users) > 1:
            # In the rare case that two user accounts have the same email address,
            # bail. Randomly selecting one seems really wrong.
            msg = 'Multiple users returned'
            raise SuspiciousOperation(msg)
        elif backend.get_settings('OIDC_CREATE_USER', True):
            if send_email_to_user:
                try:
                    mail.send_email(
                        email=email,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        template_uuid=settings.EMAIL_TEMPLATE_RESET_LOGIN_INFO_UUID,
                        brand_group_uuid=settings.EMAIL_BRAND_GROUP_UUID,
                        subject=settings.EMAIL_USER_CREATION_SUBJECT,
                        context={
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'plain_password': str(password),
                        }
                    )
                except:
                    logger.exception("Cannot send create user email")

            return backend.create_user(user_info)
        
        return None

    def normalize_user_info(self, user_info):
        attributes = user_info.get("attributes", {})

        for key in attributes:
            if isinstance(attributes[key], list):
                value = attributes[key][0] if len(attributes[key]) == 1 else attributes[key] 
                try:
                    attributes[key] = bool(strtobool(value))
                except ValueError as e:
                    attributes[key] = value
        
        user_info.update(attributes)


class UpdatePassword(BaseKeyCloak):
    def __call__(self, email, password=None, temporary=False, send_email_to_user=False, **kwargs):
        self.keycloak_admin.refresh_token()
        status = 200
        data = {'result': 'OK', 'reason': 'SUCCESS', 'message': ''}

        try:
            user_id_keycloak = self.keycloak_admin.get_user_id(email)
        except:
            data['result'] = 'KO'
            data['reason'] = 'ERROR'
            data['message'] = 'Error trying to find user in keycloak'
            status = 500

        if temporary:
            password = User.objects.make_random_password(length=14)

        self.keycloak_admin.set_user_password(user_id=user_id_keycloak, password=password, temporary=temporary)

        if send_email_to_user:
            try:
                mail.send_email(
                    email=email,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    template_uuid=settings.EMAIL_TEMPLATE_RESET_LOGIN_INFO_UUID,
                    brand_group_uuid=settings.EMAIL_BRAND_GROUP_UUID,
                    subject=settings.EMAIL_USER_PASSWORD_NOTIFICATION_SUBJECT,
                    context={
                        'name': kwargs.get('name', ''),
                        'email': email,
                        'plain_password': password,
                    }
                )
            except:
                logger.exception("Cannot send update password email")

        return JsonResponse(data=data, safe=False, status=200)


class SendUpdateAccount(BaseKeyCloak):

    def _action_exists(self, action):
        actions = ('UPDATE_PASSWORD', )
        return bool(action in actions)

    def __call__(self, email, action):
        status = 200
        data = {'result': 'KO', 'reason': 'ERROR', 'message': ''}

        if not self._action_exists(action):
            data['message'] = 'The provided action doesn\'t exists.'
            status = 400

        try:
            self.keycloak_admin.refresh_token()
            user_id = self.keycloak_admin.get_user_id(email)
            self.keycloak_admin.send_update_account(
                user_id=user_id,
                payload=json.dumps([action])
            )
            data['result'] = 'OK'
            data['reason'] = 'SUCCESS'
        except:
            status = 500
            logger.exception('Error on UpdateAccount service (dnoticias_service > keycloak)')
            data['message'] = 'An error has been ocurred on update account'

        return JsonResponse(data=data, safe=False, status=status)


class GetToken(BaseKeyCloak):
    def __call__(self, email, password):
        return self.keycloak_openid.token(email, password)


class RefreshToken(BaseKeyCloak):
    def __call__(self, refresh_token):
        return self.keycloak_openid.refresh_token(refresh_token)


class LogoutUser(BaseKeyCloak):
    def __call__(self, refresh_token):
        return self.keycloak_openid.logout(refresh_token)


class GetTokenInfo(BaseKeyCloak):
    def __call__(self, access_token):
        return self.keycloak_openid.introspect(access_token)


class KeycloakUserExists(BaseKeyCloak):
    def __call__(self, email: str) -> bool:
        if not email:
            return False

        return bool(self.keycloak_admin.get_user_id(email))


update_user = UpdateUser()
send_update_account = SendUpdateAccount()
create_user = CreateUser()
update_password = UpdatePassword()
get_token = GetToken()
refresh_token = RefreshToken()
logout_user = LogoutUser()
get_token_info = GetTokenInfo()
keycloak_user_exists = KeycloakUserExists()
