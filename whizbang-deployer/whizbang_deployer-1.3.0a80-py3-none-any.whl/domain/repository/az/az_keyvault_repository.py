import time
from abc import abstractmethod

from whizbang.data.az_cli_context import AzCliContext

from whizbang.domain.models.keyvault.keyvault_access_policy import KeyVaultAccessPolicy
from whizbang.domain.models.keyvault.keyvault_resource import KeyVaultResource
from whizbang.domain.models.keyvault.keyvault_secret import KeyVaultSecret

from whizbang.domain.exceptions import AzCliResourceDoesNotExist, DeploymentTimeoutException
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase
from whizbang.domain.repository.az.az_resource_repository_base import IAzResourceRepository, AzResourceRepositoryBase
from whizbang.util.deployment_helpers import timestamp

import logging
_log = logging.getLogger(__name__) 


class IAzKeyVaultRepository(IAzResourceRepository):
    @abstractmethod
    def get(self, resource: KeyVaultResource):
        """"""

    @abstractmethod
    def get_keyvault_secret(self, keyvault: KeyVaultResource, secret_name: str) -> KeyVaultSecret:
        """"""

    @abstractmethod
    def save_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret) -> KeyVaultSecret:
        """"""

    @abstractmethod
    def set_access_policy(self, keyvault: KeyVaultResource, policy: KeyVaultAccessPolicy):
        """"""

    @abstractmethod
    def _set_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret, encoding='utf-8'):
        """"""


class AzKeyVaultRepository(AzResourceRepositoryBase, IAzKeyVaultRepository):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, az_cli_context=context)

    @property
    def _resource_provider(self) -> str:
        return 'keyvault'

    def get(self, resource: KeyVaultResource, throw_on_not_found=True):
        """Fetch a list of KV's with the specified metadata.  Based on throw_if_not_found, either throws or returns Null if the resource is not found."""
        
        try:
            response = self._execute(f'show --resource-group {resource.resource_group_name} --name {resource.resource_name}')
            return response.results
        except AzCliResourceDoesNotExist as dne:
            if throw_on_not_found:
                raise dne
            return None
            
    def create(self, resource: KeyVaultResource):
        # Check to see if the KV exists
        keyvault = self.get(resource, throw_on_not_found=False)
        
        if keyvault is None:
            # If not, create it.
            _log.info(
                f'creating keyvault {resource.resource_name} in location: {resource.location} '
                f'and resource group: {resource.resource_group_name}')

            keyvault = self._execute(
                f'create'
                f' --resource-group {resource.resource_group_name}'
                f' --name {resource.resource_name}'
                f' --location {resource.location}'
                f' --enabled-for-template-deployment true'
            ).results

            
            # For some reason the graph API lags, so we wait for the get call to return the KV details.
            iteration = 0
            while keyvault is None:
                time.sleep(10)
                _log.info(timestamp(f'pausing for resource {resource.resource_name} to finish deploying'))
                
                # See if we can see the KV from graph
                keyvault = self.get(resource, throw_on_not_found=False)
                iteration+=1
                
                # if we waited too long, bail
                if iteration > 6:
                    raise DeploymentTimeoutException(f'failed to create resource {resource.resource_name}')
        else:
            # If existing, take no action.
            _log.info(f'keyvault {resource.resource_name} already exists')
            
        return keyvault

    def get_keyvault_secret(self, keyvault: KeyVaultResource, secret_name: str) -> KeyVaultSecret:
        try:
            response = self._execute(f'secret show --vault-name {keyvault.resource_name} --name {secret_name}', secret_response=True)
            
            # If the secret doesn't exist, that only surfaces as as log message in some versions.
            if response.logs.find('SecretNotFound') != -1:
                return None
        
        except AzCliResourceDoesNotExist as dne:    
            # If the secret doesn't exist, we may get a full exception. Same handling...
            # We call the str method on the exception to get the full message.
            if str(dne).find('SecretNotFound') != -1:
                return None
            
            # Something else went wrong.
            raise dne
                
        return KeyVaultSecret(key=secret_name, value=response.results['value'])


    #todo: save logic should move to manager
    def save_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret) -> KeyVaultSecret:
        if secret.overwrite is False:
            existing_secret = self.get_keyvault_secret(keyvault, secret.key)
            if existing_secret is not None:
                _log.info(f'secret {secret.key} already exists, overwrite set to "False"')
                return existing_secret

        saved_secret = self._set_keyvault_secret(keyvault, secret)
        return saved_secret

    def set_access_policy(self, keyvault: KeyVaultResource, policy: KeyVaultAccessPolicy):
        secret_permissions = self._handle_permissions_list(policy.permissions.secrets)
        certificate_permissions = self._handle_permissions_list(policy.permissions.certificates)
        key_permissions = self._handle_permissions_list(policy.permissions.keys)
        storage_permissions = self._handle_permissions_list(policy.permissions.storage)

        _log.info(f'attempting to set key vault access policy for {policy.name}')

        self._execute(
            f'set-policy -n {keyvault.resource_name}'
            f' --object-id {policy.object_id}'
            f' --certificate-permissions {certificate_permissions}'
            f' --key-permissions {key_permissions}'
            f' --secret-permissions {secret_permissions}'
            f' --storage-permissions {storage_permissions}'
        )

        access_policy_identifier = policy.object_id.lower()
        return access_policy_identifier

    def _set_keyvault_secret(self, keyvault: KeyVaultResource, secret: KeyVaultSecret, encoding='utf-8'):
        if secret.value is None or secret.value == '':
            _log.warning(f'Skipping unspecified secret for key: {secret.key} - secret cannot be null or empty')
            return None

        _log.info(f'setting secret {secret.key} for vault: {keyvault.resource_name}')

        response = self._execute(
            f'secret set --vault-name {keyvault.resource_name} --name {secret.key} --value "{secret.value}" --encoding {encoding}', 
            f'secret set --vault-name {keyvault.resource_name} --name {secret.key} --value "**REMOVED**" --encoding {encoding}', 
            secret_response=True
        )

        if response.results is not None:
            secret = KeyVaultSecret(key=secret.key, value=response.results['value'])
            
        return secret
        
    @staticmethod
    def _handle_permissions_list(permissions: list) -> str:
        return ' '.join(permissions) if permissions else ""
