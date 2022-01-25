from __future__ import annotations

import firefly as ff
from . import GenericOauthMiddleware
import firefly_iaaa.domain as domain


@ff.authenticator()
class Authenticator(GenericOauthMiddleware, ff.SystemBusAware):
    _request_validator: domain.OauthRequestValidators = None
    _context_map: ff.ContextMap = None

    def __init__(self):
        self._authorization_service = self._context_map.contexts['firefly_auth_middleware'].config.get(
            'auth_service', 'iaaa'
        )

    def handle(self, message: ff.Message, *args, **kwargs):
        self.info('Authenticating')
        if self._kernel.http_request and self._kernel.secured:
            token = self._retrieve_token_from_http_request()
            resp = self.request(f'{self._authorization_service}.DecodedToken', data={
                'token': token,
            })
            if not isinstance(resp, dict) or 'scope' not in resp:
                return False

            self._kernel.user.token = resp
            self._kernel.user.scopes = resp['scope'].split(' ')
            self._kernel.user.id = resp['aud']

            return True

        return self._kernel.secured is not True
