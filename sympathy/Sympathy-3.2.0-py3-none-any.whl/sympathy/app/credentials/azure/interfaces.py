# This file is part of Sympathy for Data.
# Copyright (c) 2021 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from abc import ABC, abstractmethod
import time


class AzureClient(ABC):

    # Could be used instead of tenant_id
    authority_work_or_school = 'organizations'
    authority_work_or_school_or_personal = 'common'

    @classmethod
    @abstractmethod
    def name(cls):
        NotImplementedError('Abstract')

    @classmethod
    @abstractmethod
    def client_url(cls) -> str:
        raise NotImplementedError('Abstract')

    @classmethod
    @abstractmethod
    def client_scopes(cls) -> list:
        raise NotImplementedError('Abstract')

    @classmethod
    @abstractmethod
    def client_id(cls) -> str:
        raise NotImplementedError('Abstract')

    @classmethod
    @abstractmethod
    def tenant_id(cls) -> str:
        # https://docs.microsoft.com/en-us/azure/active-directory/
        # develop/active-directory-v2-protocols#endpoints
        raise NotImplementedError('Abstract')

    @classmethod
    @abstractmethod
    def resource_url(cls) -> str:
        raise NotImplementedError('Abstract')

    @classmethod
    def authority_url(cls) -> str:
        return 'https://login.microsoftonline.com'

    @classmethod
    def redirect_url(cls) -> str:
        return 'http://localhost'


class AzureAuth(ABC):
    def __init__(self, client):
        super().__init__()
        self._client = client

    @abstractmethod
    def acquire_token_silent(self, scopes=None):
        pass

    @abstractmethod
    def get_token(self, *scopes, **kwargs):
        pass

    def authority_url(self):
        return f'{self._client.authority_url()}/{self._client.tenant_id()}'

    def get_scopes(self, scopes=None):
        if not scopes:
            scopes = self._client.client_scopes()
        client_url = self._client.client_url()
        return [f'{client_url}/{scope}' for scope in scopes]

    def get_response_account(self, auth_response):
        # https://docs.microsoft.com/en-us/azure/active-directory/
        # develop/id-tokens
        claims = auth_response['id_token_claims']
        # Tenant Id
        tid = claims['tid']
        # Object Id (for user)
        oid = claims['oid']

        home_account_id = f'{oid}.{tid}'
        for account in self._app.get_accounts():
            if account['home_account_id'] == home_account_id:
                return account

    def secrets(self, auth_response):
        now = int(time.time())
        return {
            'token': auth_response['access_token'],
            'expires_on': now + auth_response['expires_in'],
        }
