from datetime import datetime
from datetime import timedelta
from datetime import timezone
import jwt
import random

from . import tokens
import agilicus
import agilicus_api


def get_date_now():
    return datetime.now(timezone.utc)


class BearerToken:
    def __init__(
        self, raw_token=None, pubkey=None, verify=False, audience=None, random_range=60
    ):
        self.raw_token = raw_token
        self.pubkey = pubkey
        self.verify = verify
        self.audience = audience
        self.random_range = random_range

    def get(self):
        return self.raw_token

    def get_valid_token(self):
        token = None
        if not self.is_expired():
            token = self.get()

        if not token:
            self.raw_token = self._get_new_token()
            token = self.raw_token

        if not token:
            raise Exception("Failed to get valid token")

        return token

    def _get_new_token(self):
        return

    def get_random_timedelta(self):
        random_minutes = random.randint(-self.random_range, self.random_range)
        return timedelta(minutes=random_minutes)

    def is_expired(self):
        if not self.raw_token:
            return True

        _token_dict = jwt.decode(
            self.raw_token,
            self.pubkey,
            audience=self.audience,
            algorithms=["ES256"],
            options={"verify_signature": self.verify},
        )
        _exp = datetime.fromtimestamp(_token_dict["exp"], tz=timezone.utc)
        _iat = datetime.fromtimestamp(_token_dict["iat"], tz=timezone.utc)

        # grab a new token when expiry is half expired, plus some randomness
        token_expiry = _iat + ((_exp - _iat) / 2) + self.get_random_timedelta()

        if get_date_now() > token_expiry:
            return True
        return False


class AppServiceToken(BearerToken):
    def __init__(
        self,
        application_service,
        raw_token=None,
        api_config=None,
        pubkey=None,
        verify=False,
        audience=None,
        random_range=60,
        app_services_api=None,
    ):
        super().__init__(
            raw_token,
            pubkey=pubkey,
            verify=verify,
            audience=audience,
            random_range=random_range,
        )
        self.app_service = application_service
        if app_services_api:
            self.app_services_api = app_services_api
        else:
            self.app_services_api = agilicus_api.ApplicationServicesApi(
                agilicus.ApiClient(api_config)
            )

    def _get_new_token(self):
        token = self.app_services_api.create_application_service_token(
            self.app_service.id, self.app_service.org_id
        )
        return token.token


class Token:
    """Class for managing token lifecycle for service accounts."""

    def __init__(
        self=None,
        org_id=None,
        user_id=None,
        auth_issuer_url=None,
        auth_expiry_secs=None,
        scope=None,
        client_id=None,
        referer=None,
        auth_doc=None,
        api_config=None,
        auth_doc_static=False,
        tokens_api=None,
        **kwargs,
    ):
        self.org_id = org_id
        self.user_id = user_id
        self.auth_issuer_url = auth_issuer_url
        self.auth_expiry_secs = auth_expiry_secs
        self.client_id = client_id
        self.api_config = api_config
        if tokens_api:
            self.tokens_api = tokens_api
        else:
            self.tokens_api = agilicus_api.TokensApi(agilicus.ApiClient(api_config))
        self.referer = referer
        self.scope = scope
        self.token = None
        self.auth_doc = auth_doc
        self.auth_doc_static = auth_doc_static

    def is_expired(self):
        if not self.token:
            return True
        if datetime.now(timezone.utc) > self.token_expiry:
            return True

    def set_access_token(self, token):
        self.api_config.access_token = token

    def set_token(self, token):
        self.token = token
        _token_dict = jwt.decode(
            self.token, algorithms=["ES256"], options={"verify_signature": False}
        )
        _exp = datetime.fromtimestamp(_token_dict["exp"], tz=timezone.utc)
        _iat = datetime.fromtimestamp(_token_dict["iat"], tz=timezone.utc)
        # grab a new token when expiry is half expired
        self.token_expiry = _iat + ((_exp - _iat) / 2)

    def get_auth_document_expiry(self):
        if self.auth_doc:
            if isinstance(self.auth_doc["spec"]["expiry"], str):
                return datetime.fromisoformat(self.auth_doc["spec"]["expiry"])
            else:
                return self.auth_doc["spec"]["expiry"]

    def valid_user(self):
        if not self.auth_doc:
            return False

        # no user_id/org_id, we take the spec as is
        if not self.user_id and not self.org_id:
            return True

        spec = self.auth_doc["spec"]
        if spec["user_id"] == self.user_id and spec["org_id"] == self.org_id:
            return True
        return False

    def get_auth_document(self):
        if self.auth_doc and self.valid_user():
            if self.auth_doc["spec"].get("expiry"):
                if isinstance(self.auth_doc["spec"]["expiry"], str):
                    expiry = datetime.fromisoformat(self.auth_doc["spec"]["expiry"])
                else:
                    expiry = self.auth_doc["spec"]["expiry"]

                if datetime.now(timezone.utc) < expiry:
                    return self.auth_doc
            else:
                # no expiry in doc
                return self.auth_doc

        if self.auth_doc_static:
            if not self.valid_user():
                raise Exception(
                    "Static authentication document has mismatched requested org/user"
                )
            else:
                raise Exception("Static authentication document has expired")

        auth_expiry = None
        if self.auth_expiry_secs:
            auth_expiry = datetime.now(timezone.utc) + timedelta(
                seconds=self.auth_expiry_secs
            )
        kwargs = {}
        if auth_expiry:
            kwargs["expiry"] = auth_expiry

        spec = agilicus_api.AuthenticationDocumentSpec(
            org_id=self.org_id,
            user_id=self.user_id,
            auth_issuer_url=self.auth_issuer_url,
            **kwargs,
        )
        model = agilicus_api.AuthenticationDocument(spec=spec)
        self.auth_doc = self.tokens_api.create_authentication_document(model).to_dict()
        return self.auth_doc

    def get(self):
        if self.is_expired():
            _token = tokens.create_service_token(
                self.get_auth_document(),
                verify=self.api_config.ssl_ca_cert,
                scope=self.scope,
                client_id=self.client_id,
                referer=self.referer,
            )
            self.set_token(_token["access_token"])
        return self.token
