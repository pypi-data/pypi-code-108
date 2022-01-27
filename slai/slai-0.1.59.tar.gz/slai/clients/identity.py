from slai.exceptions import NoCredentialsFound
import requests

from requests.auth import HTTPBasicAuth
from importlib import import_module

from slai.modules.parameters import from_config
from slai.config import get_api_base_urls
from slai.modules.runtime import detect_credentials


REQUESTS_TIMEOUT = 15


def get_identity_client(*, client_id=None, client_secret=None, key_type=None):
    import_path = from_config(
        "IDENTITY_CLIENT",
        "slai.clients.identity.IdentityClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])
    return getattr(import_module(path), class_)(
        client_id=client_id, client_secret=client_secret, key_type=key_type
    )


class IdentityClient:
    BACKEND_BASE_URL, _ = get_api_base_urls()

    def __init__(self, client_id=None, client_secret=None, key_type=None):
        self.credentials_loaded = False
        self.key_type = key_type

        if not client_id or not client_secret:
            try:
                self.credentials = detect_credentials()
                self.client_id = self.credentials["client_id"]
                self.client_secret = self.credentials["client_secret"]
                self.credentials_loaded = True
            except NoCredentialsFound:
                pass

        else:
            self.client_id = client_id
            self.client_secret = client_secret

            self.credentials_loaded = True

    def get_user(self):
        if not self.credentials_loaded:
            raise NoCredentialsFound("no_credentials_loaded")

        body = {"action": "retrieve"}

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/user",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={},
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def validate_credentials(self):
        if not self.credentials_loaded:
            raise NoCredentialsFound("no_credentials_loaded")

        body = {}
        if self.key_type is not None:
            body["key_type"] = self.key_type

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/validate-credentials",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={},
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()
