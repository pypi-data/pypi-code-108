import requests

from requests.auth import HTTPBasicAuth
from importlib import import_module

from slai.config import get_api_base_urls
from slai.modules.parameters import from_config
from slai.modules.runtime import detect_credentials

REQUESTS_TIMEOUT = 15


def get_cli_client(client_id=None, client_secret=None):
    import_path = from_config(
        "CLI_CLIENT",
        "slai.clients.cli.SlaiCliClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])
    return getattr(import_module(path), class_)(
        client_id=client_id, client_secret=client_secret
    )


class SlaiCliClient:
    BACKEND_BASE_URL, _ = get_api_base_urls()

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        user_agent_header="SlaiCli smartshare/0.1.0",
    ):

        if client_id is None or client_secret is None:
            credentials = detect_credentials()
            self.client_id = credentials["client_id"]
            self.client_secret = credentials["client_secret"]
        else:
            self.client_id = client_id
            self.client_secret = client_secret

        self.user_agent_header = user_agent_header

    def retrieve_model(self, *, name, org_name):
        body = {"action": "retrieve", "name": name, "org_name": org_name}
        body = {k: v for k, v in body.items() if v is not None}

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/model",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def create_model_version(self, *, model_id, name):
        body = {"action": "create", "model_id": model_id, "name": name}

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_model_version_by_name(self, *, model_id, model_version_name):
        body = {
            "action": "retrieve",
            "model_id": model_id,
            "model_version_name": model_version_name,
        }

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_model_version_by_id(self, *, model_version_id):
        body = {
            "action": "retrieve",
            "model_version_id": model_version_id,
        }

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def list_model_versions(self, *, model_id):
        body = {"action": "list", "model_id": model_id}

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/model-version",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def list_model_artifacts(self, *, model_version_id):
        body = {
            "action": "list",
            "model_version_id": model_version_id,
        }

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/model-artifact",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def retrieve_model_artifact(self, *, model_version_id, model_artifact_id):
        body = {
            "action": "retrieve",
            "model_version_id": model_version_id,
            "model_artifact_id": model_artifact_id,
        }

        body = {k: v for k, v in body.items() if v is not None}

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/model-artifact",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def get_user(self):
        body = {"action": "retrieve"}

        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/user",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def update_user(self, email=None, gauth_creds=None):
        body = {"action": "update", "email": email, "gauth_creds": gauth_creds}

        body = {k: v for k, v in body.items() if v is not None}
        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/user",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()

    def get_cli_version(self):
        body = {}
        res = requests.post(
            f"{self.BACKEND_BASE_URL}/cli/cli-version",
            headers={
                "User-Agent": self.user_agent_header,
            },
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()
