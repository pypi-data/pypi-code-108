import os
import toml
from pathlib import Path
import logging

import boto3
import base64
from botocore.exceptions import ClientError


from .exceptions import RelyComplyClientException

log = logging.getLogger(__name__)
keys = ["token", "url", "impersonate"]


def merge_credentials(layers):
    credentials = {}
    for layer_credentials in layers:
        credentials.update(layer_credentials)
    return credentials


class Loader:
    def __str__(self):
        return type(self).__name__ + "()"


class Default(Loader):
    def credentials(self):
        return {"url": "https://app.relycomply.com"}


class Environment(Loader):
    def credentials(self):
        return {
            key: os.environ[f"RELYCOMPLY_{key.upper()}"]
            for key in keys
            if f"RELYCOMPLY_{key.upper()}" in os.environ
        }


class ConfigFolder(Loader):
    def __init__(self, folder: Path):
        self.folder = folder

    def credentials(self):
        config_path = self.folder / ".rely.toml"
        if not config_path.exists():
            return {}
        else:
            with open(config_path) as f:
                try:
                    config_values = toml.load(f)
                    # TODO Check for string
                    return {
                        key: config_values[key] for key in keys if key in config_values
                    }
                except:
                    pass

    def __str__(self):
        return type(self).__name__ + f"({self.folder})"


class SecretsManager(Loader):
    def load_secret(self, key):
        session = boto3.session.Session()
        client = session.client(
            service_name="secretsmanager",
        )
        secret_name = key

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise RelyComplyClientException(
                f"Could not retrieve secret {key}: str(e)"
            ) from e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if "SecretString" in get_secret_value_response:
                return get_secret_value_response["SecretString"]
            else:
                return base64.b64decode(get_secret_value_response["SecretBinary"])

    def credentials(self):
        secret_keys = {
            key: os.environ[f"RELYCOMPLY_{key.upper()}_AWS_SECRET"]
            for key in keys
            if f"RELYCOMPLY_{key.upper()}_AWS_SECRET" in os.environ
        }
        return {key: self.load_secret(value) for key, value in secret_keys.items()}


class Arguments(Loader):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def credentials(self):
        return {key: self.kwargs[key] for key in keys if self.kwargs.get(key)}


def folder_loaders():
    root = Path(".").resolve()
    folder_credentials = []
    while root:
        folder_credentials.insert(0, ConfigFolder(root))
        if root == root.parent:
            break
        root = root.parent
    return folder_credentials


class StandardCredentials(Loader):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.loaders = [
            Default(),
            *folder_loaders(),
            SecretsManager(),
            Environment(),
            Arguments(**self.kwargs),
        ]
        log.info(f"Loading Credentials")
        self.layers = [loader.credentials() for loader in self.loaders]
        self.results = merge_credentials(self.layers)

        for loader, layer in zip(self.loaders, self.layers):
            log.info(f"{loader}: {layer}")
        log.info(f"Final Credentials: {self.results}")

    def credentials(self):
        return self.results

    def get(self, key):
        return self.credentials().get(key)

    def require(self, key):
        value = self.get(key)
        if not value:
            raise RelyComplyClientException(
                f"Credential '{key}' is required but not present"
            )
        return value
