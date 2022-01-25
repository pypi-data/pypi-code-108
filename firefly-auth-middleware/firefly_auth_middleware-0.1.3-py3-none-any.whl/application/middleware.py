from __future__ import annotations

from abc import ABC
from typing import Optional

import firefly as ff


class Base(ff.Handler, ff.SystemBusAware, ABC):
    _kernel: ff.Kernel = None

    def _retrieve_token_from_http_request(self):
        for k, v in self._kernel.http_request['headers'].items():
            if k.lower() == 'authorization':
                if not v.lower().startswith('bearer'):
                    raise ff.UnauthorizedError()
                return v
        return None


@ff.authenticator()
class Authenticator(Base):
    _context_map: ff.ContextMap = None

    def __init__(self):
        self._authorization_service = self._context_map.get_context('firefly_auth_middleware').config.get(
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


@ff.authorizer()
class Authorizer(Base):
    def __init__(self):
        self._authorization_service = self._context_map.get_context('firefly_auth_middleware').config.get(
            'auth_service', 'iaaa'
        )

    def handle(self, message: ff.Message, **kwargs) -> Optional[bool]:
        return self.request(f'{self._authorization_service}.AuthorizeRequest', data={
            'token': self._retrieve_token_from_http_request(),
        })
