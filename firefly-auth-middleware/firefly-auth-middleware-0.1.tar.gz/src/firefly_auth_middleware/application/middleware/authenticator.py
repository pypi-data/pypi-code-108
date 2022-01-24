from __future__ import annotations

import firefly as ff
from . import GenericOauthMiddleware
import firefly_iaaa.domain as domain


@ff.authenticator()
class Authenticator(GenericOauthMiddleware):
    _request_validator: domain.OauthRequestValidators = None

    def handle(self, message: ff.Message, *args, **kwargs):
        self.info('Authenticating')
        if self._kernel.http_request and self._kernel.secured:
            token = self._retrieve_token_from_http_request()
            if token:
                token = token.split(' ')[-1]
            if token is None:
                try:
                    token = message.access_token
                except:
                    raise ff.UnauthenticatedError()

            self.debug('Decoding token')
            try:
                resp = self._get_client_user_and_token(token, self._kernel.user.id)
                decoded = resp['decoded']
                user = resp['user']
                client_id = resp['client_id']
            except:
                raise ff.UnauthenticatedError()

            self._kernel.user.token = decoded
            self._kernel.user.scopes = decoded['scope'].split(' ')

            return True

        return self._kernel.secured is not True
