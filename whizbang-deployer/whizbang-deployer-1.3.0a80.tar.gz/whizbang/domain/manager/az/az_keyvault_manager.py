from abc import abstractmethod
from typing import Dict, List

from whizbang.config.app_config import AppConfig
from whizbang.domain.exceptions import ActiveDirectoryObjectDoesNotExist
from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.manager.az.az_resource_manager_base import IAzResourceManager, AzResourceManagerBase
from whizbang.domain.models.keyvault.keyvault_access_policy import KeyVaultAccessPolicy
from whizbang.domain.models.keyvault.keyvault_resource import KeyVaultResource
from whizbang.domain.models.keyvault.keyvault_secret import KeyVaultSecret
from whizbang.domain.repository.az.az_active_directory_repository import IAzActiveDirectoryRepository
from whizbang.domain.repository.az.az_keyvault_repository import AzKeyVaultRepository

import logging
_log = logging.getLogger(__name__)

class IAzKeyVaultManager(IAzResourceManager):
    @abstractmethod
    def get_keyvault(self, keyvault: KeyVaultResource):
        """"""

    @abstractmethod
    def get_keyvault_secret(self, keyvault: KeyVaultResource, secret_name: str):
        """"""

    @abstractmethod
    def save_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret):
        """"""

    @abstractmethod
    def save_keyvault_secrets(self, keyvault: KeyVaultResource, secrets: 'List[KeyVaultSecret]')\
            -> Dict[str, KeyVaultSecret]:
        """"""

    @abstractmethod
    def set_access_policy(self, keyvault: KeyVaultResource, policy: KeyVaultAccessPolicy) -> str:
        """"""

    @abstractmethod
    def set_access_policies(self, keyvault: KeyVaultResource, policies: List[KeyVaultAccessPolicy]):
        """"""


class AzKeyVaultManager(AzResourceManagerBase, IAzKeyVaultManager):
    def __init__(self, app_config: AppConfig, repository: AzKeyVaultRepository,
                 active_directory_repository: IAzActiveDirectoryRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: AzKeyVaultRepository
        self.app_config = app_config
        self.active_directory_repository = active_directory_repository

    def get_keyvault(self, keyvault: KeyVaultResource):
        return self._repository.get(keyvault)

    def get_keyvault_secret(self, keyvault: KeyVaultResource, secret_name: str):
        return self._repository.get_keyvault_secret(keyvault, secret_name)

    def save_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret):
        return self._repository.save_keyvault_secret(keyvault, secret)

    def save_keyvault_secrets(self, keyvault: KeyVaultResource, secrets: 'List[KeyVaultSecret]')\
            -> Dict[str, KeyVaultSecret]:
        saved_secrets = {}
        for secret in secrets:
            result = self._repository.save_keyvault_secret(keyvault, secret)
            saved_secrets[secret.key] = result

        return saved_secrets

    def set_access_policy(self, keyvault: KeyVaultResource, policy: KeyVaultAccessPolicy) -> str:

        object_id = self.active_directory_repository.get_object_id(policy.lookup_type, policy.lookup_value)
        if object_id is None:
            error_str = f'object id for {policy.lookup_value} {policy.lookup_type} not found.'
            
            _log.error(error_str)
            raise ActiveDirectoryObjectDoesNotExist(error_str)

        policy.object_id = object_id
        policy_identifier = self._repository.set_access_policy(keyvault, policy)

        return policy_identifier

    def set_access_policies(self, keyvault: KeyVaultResource, policies: List[KeyVaultAccessPolicy]):
        policies_added: List[str] = []

        for policy in policies:
            policy_identifier = self.set_access_policy(keyvault, policy)
            policies_added.append(policy_identifier)

        return policies_added


