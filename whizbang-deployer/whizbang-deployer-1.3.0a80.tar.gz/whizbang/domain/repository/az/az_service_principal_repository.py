from typing import List

from azure.graphrbac.models import ServicePrincipal, PasswordCredential

from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.repository.az.az_repository_base import AzRepositoryBase


class AzServicePrincipalRepository(AzRepositoryBase):
    def __init__(self, context: AzCliContext):
        AzRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str:
        return "ad sp"

    # will patch and create new secret if service principal already exists
    def create_for_rbac(self, service_principal: ServicePrincipal, scopes: List[str], years: int, role):
        response = self._execute(
            command=f'create-for-rbac'
            f' --name {service_principal.display_name}'
            f' --scopes {" ".join(scopes)}'
            f' --years {years} --skip-assignment'
            f' --role {role}',
            secret_response=True
        )
        result = response.results


        if result is not None:
            # We could do a second call (below) but the password is returned.
            #credentials = self.get_credentials_by_id(result['appId'])
            
            # Disabling rbac credential for now
            #rbac_credential = [cred for cred in credentials if cred.custom_key_identifier == 'rbac'][0]
            #rbac_credential.value = result['password']

            service_principal.app_id = result['appId']
            service_principal.password_credentials = result['password']
            service_principal.app_owner_tenant_id = result['tenant']

        return service_principal

    def list_service_principal(self, service_principal_name: str):
        response = self._execute(
            f'list --display-name {service_principal_name}'
        )
        return response.results

    def _rbac_credential_filter(self, credential: PasswordCredential):
        return bool(credential.custom_key_identifier == 'rbac')

    def get_credentials_by_id(self, id: str) -> List[PasswordCredential]:
        credentials: List[PasswordCredential] = []

        results = self._execute(
            f'credential list'
            f' --id {id}'
        ).results

        for credential_json in results:
            credential = PasswordCredential()
            credential.custom_key_identifier = credential_json['customKeyIdentifier']
            credential.start_date = credential_json['startDate']
            credential.end_date = credential_json['endDate']
            credential.key_id = credential_json['keyId']
            credentials.append(credential)

        return credentials
