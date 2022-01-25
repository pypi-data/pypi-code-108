import os
from typing import Dict, List

from tktl.core.clients.taktile import TaktileApiClient
from tktl.core.exceptions import APIClientException
from tktl.core.loggers import LOG, Logger
from tktl.core.schemas.repository import RepositorySecret


class SecretsManager:
    def __init__(self, secrets_repository: str, logger: Logger = LOG):
        self.logger = logger
        self.secrets_repository = secrets_repository
        self.client = TaktileApiClient()

    def get_remote_secrets(self) -> List[RepositorySecret]:
        try:
            return self.client.get_secrets_for_local_repository(self.secrets_repository)
        except APIClientException as e:
            self.logger.error(
                f"Failed to fetch repository secrets: {e.detail}, no remote secrets will be consumed."
                "Have you run `tktl login` first?"
            )
            exit(1)

    def get_secrets(self) -> Dict[str, str]:
        local_secrets = dict()
        remote_secrets = self.get_remote_secrets()
        not_found_secrets = []
        for secret in remote_secrets:
            name = secret.secret_name
            value = os.environ.get(name, None)
            if value is None:
                not_found_secrets.append(name)
            else:
                local_secrets[name] = value
        if not_found_secrets:
            not_found_string = "\n  - " + "\n  - ".join(not_found_secrets) + "\n"
            self.logger.warning(
                f"Secrets with names: {not_found_string}"
                "Found remotely but no matching environment variable found. "
                "The secret won't be ingested by the Docker image."
            )
        return local_secrets
