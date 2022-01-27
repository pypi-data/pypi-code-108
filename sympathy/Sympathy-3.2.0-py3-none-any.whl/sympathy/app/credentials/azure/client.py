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
import msal
import urllib.parse

try:
    from azure.core.credentials import AccessToken
except ImportError:
    from collections import namedtuple
    AccessToken = namedtuple("AccessToken", ["token", "expires_on"])

from . import interfaces


class ClientError(Exception):
    pass


class PublicAuthCodeClient(interfaces.AzureAuth):

    def __init__(self, client, token_cache):
        super().__init__(client)
        self._token_cache = token_cache
        self._flows = {}
        self._app = msal.PublicClientApplication(
            self._client.client_id(),
            authority=self.authority_url(),
            token_cache=self._token_cache)

    def acquire_token_silent(self, scopes=None, userid=None):
        client_scopes = self._client.client_scopes()
        if scopes is None:
            scopes = client_scopes

        accounts = self._app.get_accounts()
        account = None
        if set(scopes) == set(client_scopes):
            if userid is not None:
                by_user_id = {
                    account['home_account_id']: account
                    for account in accounts}
                account = by_user_id.get(userid)
            elif accounts and len(accounts) == 1:
                account = accounts[0]
        if account:
            return self._app.acquire_token_silent(
                self.get_scopes(), account=account)

    def get_token(self, *scopes, **kwargs):
        token = self.acquire_token_silent(scopes or None)
        return AccessToken(**self.secrets(token))

    def initiate_auth_code_flow(self, username=None, port=None) -> str:
        """
        Redirect URL can be used to specify a custom port in case of local
        host url.

        Returns auth_url.
        """
        kwargs = {}
        if username:
            kwargs['login_hint'] = username

        redirect_url = self._client.redirect_url()
        if port:
            parsed = urllib.parse.urlsplit(redirect_url)
            if not parsed.port:
                # Will only work for localhost url.
                parsed = parsed._replace(netloc=f'{parsed.netloc}:{port}')
                redirect_url = urllib.parse.urlunsplit(parsed)

        flow = self._app.initiate_auth_code_flow(
            scopes=self.get_scopes(), redirect_uri=redirect_url,
            **kwargs)
        if flow:
            error = flow.get('error')
            if 'error' in flow:
                raise ClientError(str(error))
            else:
                state = flow['state']
                self._flows[state] = flow
                return flow
        else:
            raise ClientError(
                'Failed to initiate_auth_code_flow')

    def acquire_token_by_auth_code_flow(self, auth_response):
        state = None
        code = None
        if auth_response:
            state = auth_response.get('state')
            code = auth_response.get('code')
        flow = self._flows.pop(state, None)
        if flow:
            if code is not None:
                result = self._app.acquire_token_by_auth_code_flow(
                    flow, auth_response)
                return result
            else:
                # This is abort/cancel.
                pass
        else:
            raise ClientError(
                'Must initiate_auth_code_flow before '
                'acquire_token_by_auth_code_flow')
