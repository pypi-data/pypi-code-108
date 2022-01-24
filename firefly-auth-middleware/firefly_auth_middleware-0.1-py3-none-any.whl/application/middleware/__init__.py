from __future__ import annotations

from .authenticator import *
from .authorizer import *

import firefly as ff
import firefly_iaaa.domain as domain


class GenericOauthMiddleware(ff.Handler, ff.LoggerAware, ff.SystemBusAware):
    _kernel: ff.Kernel = None
    _oauth_provider: domain.OauthProvider = None
    _get_client_user_and_token: domain.GetClientUserAndToken = None

    def handle(self, message: ff.Message):
        pass

    def _retrieve_token_from_http_request(self):
        for k, v in self._kernel.http_request['headers'].items():
            if k.lower() == 'authorization':
                if not v.lower().startswith('bearer'):
                    raise ff.UnauthorizedError()
                return v
        return None
