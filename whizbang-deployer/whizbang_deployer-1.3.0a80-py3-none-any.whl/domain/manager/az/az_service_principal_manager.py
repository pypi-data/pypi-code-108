from typing import List

from azure.graphrbac.models import ServicePrincipal

from whizbang.domain.manager.az.az_app_registration_manager import AzAppRegistrationManager
from whizbang.domain.manager.az.az_manager_base import AzManagerBase
from whizbang.domain.repository.az.az_service_principal_repository import AzServicePrincipalRepository


class AzServicePrincipalManager(AzManagerBase):
    def __init__(self, repository: AzServicePrincipalRepository, az_app_registration_manager: AzAppRegistrationManager):
        AzManagerBase.__init__(self, repository)
        self._az_app_registration_manager = az_app_registration_manager
        self._repository: AzServicePrincipalRepository

    def create_for_rbac(self, service_principal: ServicePrincipal, scopes: List[str], years: int = 1,
                        role: str = 'Contributor') -> ServicePrincipal:
        return self._repository.create_for_rbac(
            service_principal=service_principal,
            scopes=scopes, years=years,
            role=role
        )

    def list_service_principal(self, service_principal_name: str):
        return self._repository.list_service_principal(service_principal_name=service_principal_name)

    # adding owners lives on the app registration azure api, and thus is part of the app registration stack
    def add_group_members_as_owner(self, app_id: str, group_object_id: str) -> None:
        self._az_app_registration_manager.add_group_members_as_owner(app_id=app_id, group_object_id=group_object_id)
