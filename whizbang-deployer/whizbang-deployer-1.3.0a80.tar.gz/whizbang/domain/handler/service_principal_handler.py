from typing import List

from azure.graphrbac.models import ServicePrincipal

from whizbang.config.app_config import AppConfig
from whizbang.domain.handler.handler_base import HandlerBase

from whizbang.domain.manager.az.az_service_principal_manager import AzServicePrincipalManager


class ServicePrincipalHandler(HandlerBase):
    def __init__(self, app_config: AppConfig, service_principal_manager: AzServicePrincipalManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.__service_principal_manager = service_principal_manager

    def save(self, display_name: str, scopes: List[str], years: int = 1, role='Contributor') -> ServicePrincipal:
        service_principal = ServicePrincipal(display_name=display_name)
        result = self.__service_principal_manager.create_for_rbac(
            service_principal=service_principal,
            scopes=scopes,
            years=years,
            role=role
        )
        return result

    def list(self, service_principal_name: str):
        return self.__service_principal_manager.list_service_principal(service_principal_name=service_principal_name)

    def add_group_members_as_owner(self, app_id: str, group_object_id: str) -> None:
        self.__service_principal_manager.add_group_members_as_owner(app_id=app_id, group_object_id=group_object_id)

