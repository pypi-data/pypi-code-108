import json
import os
import certifi

from .agilicus_api.api_client import ApiClient
from .agilicus_api.configuration import Configuration


class _ApiClientWrapper(ApiClient):
    def __init__(self, configuration: Configuration = None, **kwargs):
        if not configuration:
            configuration = Configuration()

        cert_path = os.environ.get("SSL_CERT_FILE")

        if cert_path and not configuration.ssl_ca_cert:
            configuration.ssl_ca_cert = cert_path
        elif configuration.ssl_ca_cert is None:
            configuration.ssl_ca_cert = certifi.where()

        super().__init__(configuration=configuration, **kwargs)

    def deserialize_dict(self, data: dict, response_type):
        return self.deserialize_json(json.dumps(data), response_type)

    def deserialize_json(self, json_data: str, response_type):
        response = _Response(json_data)
        return self.deserialize(response, response_type, True)


def patched_api_client():
    return _ApiClientWrapper


class _Response:
    def __init__(self, data):
        self.data = data
