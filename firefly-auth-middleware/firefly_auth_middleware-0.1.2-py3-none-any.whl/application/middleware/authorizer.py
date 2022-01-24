from __future__ import annotations

import firefly as ff
from . import GenericOauthMiddleware
import firefly_iaaa.domain as domain


class AuthorizeRequest(GenericOauthMiddleware):
    _registry: ff.Registry = None

    def handle(self, message: ff.Message):
        try:
            if not message.access_token:
                token = self._get_token()
                if not token:
                    return False
                message.access_token = token
            else:
                token = message.access_token
        except AttributeError:
            token = self._get_token()
            if not token:
                return False
            message.access_token = token
        if not message.access_token and not token:
            return False
        if message.access_token.lower().startswith('bearer'):
            message.access_token = message.access_token.split(' ')[-1]

        try:
            resp = self._get_client_user_and_token(token, self._kernel.user.id)
            decoded = resp['decoded']
            user = resp['user']
            client_id = resp['client_id']
        except:
            raise ff.UnauthorizedError()
        try:
            if not message.scopes:
                message.scopes = decoded.get('scope').split(' ') if decoded else self._kernel.user.scopes
        except AttributeError:
            message.scopes = decoded.get('scope').split(' ') if decoded else self._kernel.user.scopes

        message.token = message.access_token
        validated, resp = self._oauth_provider.verify_request(message, message.scopes)

        return validated

    def _get_token(self):
        token = None
        try:
            token = self._retrieve_token_from_http_request()
        except TypeError as e:
            if str(e).startswith("'NoneType'"):
                pass
            else:
                raise

        if not token:
            try:
                token = self._kernel.user.token
            except Exception:
                raise
        return token
