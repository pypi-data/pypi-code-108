import abc

from databricks_cli.sdk import ApiClient
from databricks_cli.secrets.api import SecretApi
import requests

from whizbang.data.databricks.databricks_context_base import DatabricksContextBase, IDatabricksContextBase


class IDatabricksSecretContext(IDatabricksContextBase):
    """"""

    @abc.abstractmethod
    def create_keyvault_secret_scope(self, keyvault_name, keyvault_resource_id,
                                     keyvault_dns=None):
        """"""

    @abc.abstractmethod
    def get_secret_scopes(self):
        """"""


class DatabricksSecretContext(DatabricksContextBase, IDatabricksSecretContext):
    def __init__(self, api_client: ApiClient, api: SecretApi):
        super().__init__(api_client=api_client, api=api)

    def create_keyvault_secret_scope(self, keyvault_name, keyvault_resource_id, keyvault_dns=None, scope_name: str = 'primary-key-vault-scope'):
        def _create_keyvault_secret_scope(api: SecretApi, scope_name, keyvault_resource_id, keyvault_dns):
            return api.create_scope(
                scope=f'{scope_name}',
                scope_backend_type='AZURE_KEYVAULT',
                backend_azure_keyvault={
                    'resource_id': f'{keyvault_resource_id}',
                    'dns_name': f'{keyvault_dns}'
                },
                initial_manage_principal='users'
            )

        keyvault_dns = keyvault_dns or f'https://{keyvault_name}.vault.azure.net/'
        
        return self._execute(
            _create_keyvault_secret_scope,
            scope_name=scope_name,
            keyvault_resource_id=keyvault_resource_id,
            keyvault_dns=keyvault_dns)

    def get_secret_scopes(self):
        def _get_secret_scopes(api: SecretApi):
            return api.list_scopes()

        return self._execute(func=_get_secret_scopes)

    def delete_scope(self, scope_name: str = 'primary-key-vault-scope'):
        def _delete_scope(api: SecretApi, scope_name: str):
            try:
                return api.delete_scope(scope=f'{scope_name}')
            except requests.exceptions.HTTPError:
                print(f'scope {scope_name} does not exist and cannot be deleted')
        return self._execute(func=_delete_scope, scope_name=scope_name)
