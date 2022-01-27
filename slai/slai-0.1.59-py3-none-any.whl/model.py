import re


from slai.clients.inference import get_inference_client
from slai.exceptions import InvalidModelURI
from slai.constants import MODEL_ROUTE_URI


class Model:
    def __init__(self, model_uri):
        self._parse_model_uri(model_uri)

        self.inference_client = get_inference_client(
            org_name=self.org_name,
            model_name=self.model_name,
            model_version_name=self.model_version_name,
        )

    def _parse_model_uri(self, model_uri):
        m = re.match(MODEL_ROUTE_URI, model_uri)
        if not m:
            raise InvalidModelURI("invalid_model_route")

        org_name = m.group(1)
        model_name = m.group(2)
        model_version_name = m.group(3)

        if model_version_name == "":
            model_version_name = None

        self.org_name = org_name
        self.model_name = model_name
        self.model_version_name = model_version_name

    def __call__(self, **inputs):
        return self.inference_client.call(payload=inputs)

    def call(self, **inputs):
        return self.inference_client.call(payload=inputs)

    def info(self):
        return self.inference_client.info()
