import requests

from requests.auth import HTTPBasicAuth
from importlib import import_module
from slai.modules.parameters import from_config
from slai.config import get_api_base_urls
from slai.modules.runtime import detect_credentials
from slai.clients.model import get_model_client


REQUESTS_TIMEOUT = 15


def get_inference_client(*, org_name, model_name, model_version_name):
    import_path = from_config(
        "MODEL_INFERENCE_CLIENT",
        "slai.clients.inference.ModelInferenceClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])

    return getattr(import_module(path), class_)(
        org_name=org_name,
        model_name=model_name,
        model_version_name=model_version_name,
    )


class ModelInferenceClient:
    BACKEND_BASE_URL, MODEL_BASE_URL = get_api_base_urls()

    def __init__(self, *, org_name, model_name, model_version_name=None):
        credentials = detect_credentials()

        self.client_id = credentials["client_id"]
        self.client_secret = credentials["client_secret"]

        self.model_server_id = None
        self.org_name = org_name
        self.model_name = model_name
        self.model_version_name = model_version_name

        self._load_model()

    def _load_model(self):
        self.model_client = get_model_client(
            org_name=self.org_name,
            model_name=self.model_name,
        )
        self.model = self.model_client.get_model()

        if self.model_version_name is not None:
            self.model_version = self.model_client.get_model_version_by_name(
                model_version_name=self.model_version_name
            )
            self.model_version_id = self.model_version["id"]
        else:
            self.model_version_id = None

    def call(self, payload):
        body = {
            "model_id": self.model["id"],
            "model_version_id": self.model_version_id,
            "payload": payload,
        }

        if body.get("model_version_id") is None:
            del body["model_version_id"]

        res = None
        res = requests.post(
            f"{self.BACKEND_BASE_URL}/model/call",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )

        res.raise_for_status()
        response_data = res.json()

        if response_data.get("model_server_id") is not None:
            self.model_server_id = response_data["model_server_id"]
            del response_data["model_server_id"]

        return response_data["result"]

    def info(self):
        body = {
            "model_id": self.model["id"],
            "model_version_id": self.model_version_id,
        }

        if body.get("model_version_id") is None:
            del body["model_version_id"]

        res = requests.post(
            f"{self.BASE_URL}/model/info",
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            json=body,
            timeout=REQUESTS_TIMEOUT,
        )
        res.raise_for_status()
        return res.json()
