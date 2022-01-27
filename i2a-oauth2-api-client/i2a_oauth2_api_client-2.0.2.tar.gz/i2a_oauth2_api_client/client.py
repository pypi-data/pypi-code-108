import requests
import os
from urllib.parse import urljoin

from i2a_oauth2_api_client.exceptions import I2AOauth2ClientException
from i2a_oauth2_api_client.enums import Environment


class I2AOauth2Client:

    I2A_OAUTH2_API_QA_SERVER_URL = 'https://oauth2-qa.i2asolutions.com'
    I2A_OAUTH2_API_PROD_SERVER_URL = 'https://oauth2.i2asolutions.com'
    I2A_OAUTH2_API_ROOT_PATH = '/api/v2'

    def __init__(self, client_id, client_secret, environment=Environment.QA):
        assert isinstance(environment, Environment)

        if environment is Environment.QA:
            self.__url = self.I2A_OAUTH2_API_QA_SERVER_URL
        elif environment is Environment.PROD:
            self.__url = self.I2A_OAUTH2_API_PROD_SERVER_URL
        else:
            raise NotImplementedError

        self.__environment = environment
        self.__client_id = client_id
        self.__client_secret = client_secret

        self.headers = {
            "Client-Id": self.__client_id
        }
        self.server_to_server_headers = {
            "Client-Id": self.__client_id,
            "Client-Secret": self.__client_secret
        }

    @property
    def client_id(self):
        return self.__client_id

    @property
    def client_secret(self):
        return self.__client_secret

    @property
    def url(self):
        return self.__url

    @property
    def environment(self):
        return self.__environment

    def ping(self):
        url = self._get_full_url('ping/')
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Ping attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def register(
            self, email, password1, password2, first_name=None, last_name=None
    ):
        url = self._get_full_url('application-users/register/')
        data = {
            "username": email,
            "password1": password1,
            "password2": password2,
        }
        if first_name is not None:
            data['first_name'] = first_name
        if last_name is not None:
            data['last_name'] = last_name

        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Register attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def get_token(self, email, password):
        url = self._get_full_url('auth/token/')
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": email,
            "password": password
        }
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Get token attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def convert_token(self, backend, social_app_token):
        url = self._get_full_url('auth/convert-token/')
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "convert_token",
            "backend": backend,
            "token": social_app_token
        }
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Convert token attempt at {url} has failed failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def get_me(self, token):
        url = self._get_full_url('application-users/me/')
        headers = self.headers.copy()
        headers['Authorization'] = f"Bearer {token}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Get me attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def get_my_application_user(self, token):
        url = self._get_full_url('application-users/my-application-user/')
        headers = self.headers.copy()
        headers['Authorization'] = f"Bearer {token}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Get me attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def password_change(self, token, old_password, new_password1, new_password2):
        url = self._get_full_url('application-users/password-change/')
        headers = self.headers.copy()
        headers['Authorization'] = f"Bearer {token}"
        data = {
            "old_password": old_password,
            "new_password1": new_password1,
            "new_password2": new_password2
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Password change attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def delete_account(self, token):
        url = self._get_full_url('application-users/delete-account/')
        headers = self.headers.copy()
        headers['Authorization'] = f"Bearer {token}"
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Delete account attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def add_new_identity(self, token, email, password1, password2, first_name=None, last_name=None):
        url = self._get_full_url('add-new-identity/username-and-password/')
        headers = self.headers.copy()
        headers['Authorization'] = f"Bearer {token}"
        data = {
            "username": email,
            "password1": password1,
            "password2": password2,
        }
        if first_name is not None:
            data['first_name'] = first_name
        if last_name is not None:
            data['last_name'] = last_name
        response = requests.delete(url, json=data, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Add new identity attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def add_new_social_app_identity(self, token, backend, social_app_token):
        url = self._get_full_url('add-new-identity/social-app/')
        headers = self.headers.copy()
        headers['Authorization'] = f"Bearer {token}"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "convert_token",
            "backend": backend,
            "token": social_app_token
        }
        response = requests.delete(url, json=data, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Add new social app identity attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_ping(self):
        url = self._get_full_url('server-to-server/ping/')
        response = requests.get(url, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Server to server ping attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_register(self, email, password1, password2, first_name=None, last_name=None):
        url = self._get_full_url('server-to-server/application-users/register/')
        data = {
            "username": email,
            "password1": password1,
            "password2": password2,
        }
        if first_name is not None:
            data['first_name'] = first_name
        if last_name is not None:
            data['last_name'] = last_name

        response = requests.post(url, json=data, headers=self.server_to_server_headers)
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(f'Server to server register attempt at {url} has failed for unknown reason.')
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_get_application_users(self):
        url = self._get_full_url('server-to-server/application-users/')
        response = requests.post(url, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server get application users attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_get_application_user(self, i2a_identifier):
        url = self._get_full_url(f'server-to-server/application-users/{i2a_identifier}/')
        response = requests.post(url, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server get application user attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_password_reset_request(self, email):
        url = self._get_full_url('server-to-server/password-reset-request/')
        data = {
            "username": email
        }
        response = requests.post(url, json=data, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server password reset request attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_password_reset(self, code, new_password1, new_password2):
        url = self._get_full_url('server-to-server/password-reset/')
        data = {
            "code": str(code),
            "new_password1": new_password1,
            "new_password2": new_password2
        }
        response = requests.post(url, json=data, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server ot server password reset attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_password_reset_code_check(self, code):
        url = self._get_full_url('server-to-server/password-reset-code-check/')
        data = {
            "code": str(code)
        }
        response = requests.post(url, json=data, headers=self.server_to_server_headers)
        if response.status_code == 204:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server password reset code check attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_username_change(self, old_email, new_email):
        url = self._get_full_url('server-to-server/application-users/username-change/')
        data = {
            "old_username": old_email,
            "new_username": new_email
        }
        response = requests.post(url, json=data, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server username change attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_delete_account(self, i2a_identifier):
        url = self._get_full_url(f'server-to-server/application-users/delete-account/{i2a_identifier}/')
        response = requests.delete(url, headers=self.server_to_server_headers)
        if response.status_code == 204:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server delete account attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_get_application_user_groups(self):
        url = self._get_full_url(f'server-to-server/application-user-groups/')
        response = requests.delete(url, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server get application user groups attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def server_to_server_get_application_user_group(self, application_user_group_id):
        url = self._get_full_url(f'server-to-server/application-user-groups/{application_user_group_id}/')
        response = requests.delete(url, headers=self.server_to_server_headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            raise I2AOauth2ClientException(
                f'Server to server get application user group attempt at {url} has failed for unknown reason.'
            )
        else:
            raise I2AOauth2ClientException(data=response.json())

    def _get_full_url(self, resource_path):
        return urljoin(self.__url, os.path.join(self.I2A_OAUTH2_API_ROOT_PATH, resource_path))
