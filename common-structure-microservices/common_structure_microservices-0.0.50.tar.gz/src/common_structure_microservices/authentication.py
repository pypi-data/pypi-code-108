import json

from munch import Munch
from rest_framework.authentication import BaseAuthentication, get_authorization_header


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request)
        if not auth:
            return None
        try:
            auth_json = json.loads(auth)
        except Exception:
            return None
        if auth_json == 'INVALIDO' or auth_json == 'EXPIRADO':
            return auth_json, auth_json
        user_json = auth_json.get('user', None)
        if user_json is None:
            return None
        user_munch = Munch(user_json)
        auth_munch = Munch(auth_json)
        return user_munch, auth_munch
