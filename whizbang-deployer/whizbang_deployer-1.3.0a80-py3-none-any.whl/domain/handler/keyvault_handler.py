from abc import abstractmethod
from typing import Dict

from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_keyvault_manager import IAzKeyVaultManager
from whizbang.domain.models.keyvault.keyvault_resource import KeyVaultResource
from whizbang.domain.models.keyvault.keyvault_secret import KeyVaultSecret


class IKeyVaultHandler(IHandler):
    """"""

    @abstractmethod
    def create_keyvault(self, keyvault_name: str, environment_config: EnvironmentConfig) -> KeyVaultResource:
        """"""

    @abstractmethod
    def save_keyvault_secrets(self, keyvault: KeyVaultResource, secrets: 'list[KeyVaultSecret]') -> Dict[
        str, KeyVaultSecret]:
        """"""

    @abstractmethod
    def set_keyvault_access_policies(self, resource_ids: dict):
        """"""


class KeyVaultHandler(HandlerBase, IKeyVaultHandler):
    def __init__(
            self,
            app_config: AppConfig,
            environment_config: EnvironmentConfig,
            keyvault_manager: IAzKeyVaultManager
    ):
        HandlerBase.__init__(self, app_config=app_config)
        self.environment_config = environment_config
        self.__keyvault_manager = keyvault_manager
        self.keyvault_access_policies_from_config = self.environment_config.keyvault_access_policies

    def create_keyvault(self, keyvault_name: str, environment_config: EnvironmentConfig) -> KeyVaultResource:
        
        keyvault = KeyVaultResource(
            resource_name=keyvault_name,
            resource_group_name=environment_config.resource_group_name,
            location=environment_config.resource_group_location
        )

        self.__keyvault_manager.create(keyvault)
        return keyvault

    def save_keyvault_secrets(self, keyvault: KeyVaultResource, secrets: 'list[KeyVaultSecret]') -> Dict[
        str, KeyVaultSecret]:
        result = self.__keyvault_manager.save_keyvault_secrets(keyvault=keyvault, secrets=secrets)
        return result

    def set_keyvault_access_policies(self, resource_ids: dict):

        access_policies = self.keyvault_access_policies_from_config
        for policy in access_policies:
            assignee_name = policy.lookup_value
            keyvault_name = policy.keyvault_name

            if assignee_name in resource_ids:
                policy.lookup_value = resource_ids[assignee_name].split('/')[-1]

            if keyvault_name in resource_ids:
                keyvault_name = resource_ids[keyvault_name].split('/')[-1]

            keyvault = KeyVaultResource(
                resource_name=f'{keyvault_name}',
                resource_group_name=self.environment_config.resource_group_name,
                location=self.environment_config.resource_group_location
            )

            self.__keyvault_manager.set_access_policies(keyvault=keyvault, policies=access_policies)
