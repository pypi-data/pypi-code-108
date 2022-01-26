import calendar
import json
from datetime import datetime

import jwt
import requests
from oauth2client.client import Credentials

from . import context, credentials, response


def is_token_expired(token):
    try:
        payload = jwt.decode(
            token, algorithms=["ES256"], options={"verify_signature": False}
        )
    except jwt.ExpiredSignatureError:
        return True

    if "exp" not in payload:
        return True

    now = calendar.timegm(datetime.utcnow().utctimetuple())
    expired = payload["exp"] < now
    return expired


class TokenStore(Credentials):
    def __init__(self, data=None):
        self.valid = True
        if data:
            self.data = data
        else:
            self.data = {}
            self.data["_module"] = "agilicus.access"
            self.data["_class"] = "TokenStore"
        self.token_cache = {}

    def set_store(self, store):
        self.store = store

    def set_ctx(self, ctx):
        self.ctx = ctx

    def set_id_token(self, id_token):
        self.id_token = id_token

    @classmethod
    def from_json(self, json_data):
        data = json.loads(json_data)
        return self(data)

    def _to_json(self, strip, to_serialize=None):
        return json.dumps(self.data)

    def add(self, org_id, token):
        self.data[org_id] = token
        self.store.put(self)

    def get(self, org_id, force=False):
        token = self.token_cache.get(org_id, None)
        if token:
            return token

        token = self.data.get(org_id, None)

        if token and is_token_expired(token):
            # expired, get a new token
            token = None

        if token is None:
            token = self.request_token(org_id)
            self.add(org_id, token)
            self.token_cache[org_id] = token
            return token
        return token

    def request_token(self, org_id):
        headers = {}
        headers["Content-type"] = "application/json"
        post_data = {}
        post_data["id_token"] = self.id_token
        post_data["org_id"] = org_id

        resp = requests.post(
            context.get_api(self.ctx) + "/v1/whoami",
            headers=headers,
            data=json.dumps(post_data),
            verify=context.get_cacert(self.ctx),
        )
        response.validate(resp)
        return resp.json()["token"]


class AccessToken:
    def __init__(self, ctx, crd):
        self.valid = True
        self.data = json.loads(crd.to_json())
        self.ctx = ctx
        self.store = credentials.get_store_from_ctx(self.ctx, token=True)
        self.token_store = self.store.get()
        if not self.token_store:
            self.token_store = TokenStore()
        self.token_store.set_store(self.store)
        self.token_store.set_ctx(ctx)
        self.token_store.set_id_token(self.data["token_response"]["id_token"])

        try:
            self.token_payload = jwt.decode(
                self.data["access_token"],
                algorithms=["ES256"],
                options={"verify_signature": False},
            )
        except jwt.ExpiredSignatureError:
            self.token_payload = {}

    def get_token_for_org(self, org_id):
        if org_id is None or org_id == self.token_payload.get("org", None):
            return self.data["access_token"]

        return self.token_store.get(org_id)

    def get(self, org_id=None):
        if org_id is not None:
            self.get_token_for_org(org_id)

        org_id = context.get_org_id(self.ctx)
        return self.get_token_for_org(org_id)

    def get_id_token(self):
        return self.data["token_response"]["id_token"]

    def scopes(self):
        if not self.token_payload:
            return []
        return self.token_payload.get("scopes", [])


def get_access_token(ctx, org_id=None, refresh=None):
    token = AccessToken(ctx, credentials.get_credentials_from_ctx(ctx, refresh))
    if _need_new_token(ctx, token):
        credentials.delete_credentials_with_ctx(ctx)
        token = AccessToken(ctx, credentials.get_credentials_from_ctx(ctx, refresh))

    return token


def _need_new_token(ctx, token):
    current_scopes = _get_agilicus_scopes(token.scopes())
    new_scopes = _get_agilicus_scopes(context.get_scopes(ctx))
    diff = new_scopes.symmetric_difference(current_scopes)
    if diff:
        # scopes have changed. Need a new one
        return True

    return False


def _get_agilicus_scopes(scopes):
    return {scope for scope in scopes if scope.startswith("urn:agilicus")}
