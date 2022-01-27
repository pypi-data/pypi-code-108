import warnings
from collections import abc
from typing import Dict, Any, Optional, List, Callable

from vtb_http_interaction.keycloak_gateway import KeycloakConfig
from vtb_http_interaction.services import AuthorizationHttpService, HttpService

from vtb_authorizer_utils.converters import convert_user, convert_organization, convert_project, \
    convert_folder, convert_children, convert_resource_service, convert_resource_type, convert_resource_rule, \
    convert_path
from vtb_authorizer_utils.data_objects import User, Organization, Project, Folder, Children, ResourceService, \
    ResourceType, ResourceRule


# pylint: disable=too-many-public-methods
class AuthorizerGateway:
    """
    Сервис оргструктуры
    Пример вложенности  organization->folder1->folder1.1->project1
    """
    _USERS_URL = 'users'
    _ORGANIZATIONS_URL = 'organizations'
    _FOLDERS_URL = 'folders'
    _PROJECTS_URL = 'projects'
    _RESOURCE_SERVICES_URL = 'resource_services'
    _RESOURCE_TYPE_URL = 'resource_types'
    _RESOURCE_RULE_URL = 'resource_rules'

    # TODO: создание сервиса должно происходить до создания экземпляра AuthorizerGateway.
    #  Сервис должен передаваться как аргумент service
    def __init__(self, base_url: str,
                 keycloak_config: Optional[KeycloakConfig] = None,
                 redis_connection_string: Optional[str] = None,
                 access_token: Optional[str] = None,
                 service: Optional[HttpService] = None):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {access_token}'} if access_token else {}
        if service:
            if isinstance(service, HttpService):
                self.service = service
            else:
                raise ValueError('The parameter "service" must be an instance of "HttpService" class')
        else:
            warnings.warn(
                "Parameters 'keycloak_config' and 'redis_connection_string' are deprecated, use 'service' instead. "
                "Parameters will be removed in version 1.0.0.",
                DeprecationWarning, stacklevel=2
            )

            self.service = HttpService() if access_token else AuthorizationHttpService(keycloak_config,
                                                                                       redis_connection_string)

    # Пользователи
    async def get_user(self, keycloak_id: str) -> Optional[User]:
        """ Получение пользователя по keycloak_id (Keycloak ID) """
        return await self._get_item([self._USERS_URL], keycloak_id, convert_user)

    async def get_users(self, **query_params) -> Optional[List[User]]:
        """ Получение списка пользователей """
        return await self._get_list([self._USERS_URL], convert_user, **query_params)

    # Организации
    async def get_organization(self, name: str) -> Optional[Organization]:
        """ Получение организации по name (кодовое название) """
        return await self._get_item([self._ORGANIZATIONS_URL], name, convert_organization)

    async def get_organizations(self, **query_params) -> Optional[List[Organization]]:
        """ Получение списка организаций """
        return await self._get_list([self._ORGANIZATIONS_URL], convert_organization, **query_params)

    async def get_organization_projects(self, name: str, **query_params) -> Optional[List[Project]]:
        """ Получение проектов организации """
        return await self._get_list([self._ORGANIZATIONS_URL, name, self._PROJECTS_URL], convert_project,
                                    **query_params)

    async def get_organization_children(self, name: str, **query_params) -> Optional[List[Children]]:
        """ Получение потомков организации """
        return await self._get_list([self._ORGANIZATIONS_URL, name, 'children'], convert_children,
                                    **query_params)

    # Folders
    async def get_folder(self, name: str) -> Optional[Folder]:
        """ Получение папки по name """
        return await self._get_item([self._FOLDERS_URL], name, convert_folder)

    async def get_folder_children(self, name: str, **query_params) -> Optional[List[Children]]:
        """ Получение потомков папки """
        return await self._get_list([self._FOLDERS_URL, name, 'children'], convert_children,
                                    **query_params)

    async def get_folder_ancestors(self, name: str, **query_params) -> Optional[List[Children]]:
        """ Получение предков папки """
        return await self._get_list([self._FOLDERS_URL, name, 'ancestors'], convert_children,
                                    **query_params)

    async def get_folder_path(self, name: str) -> Optional[str]:
        """ Получение пути оргструктуры папки по name """
        return await self._get_list([self._FOLDERS_URL, name, 'path'], convert_path)

    # Projects
    async def get_project(self, name: str) -> Optional[Project]:
        """ Получение проекта по name """
        return await self._get_item([self._PROJECTS_URL], name, convert_project)

    async def get_project_ancestors(self, name: str, **query_params) -> Optional[List[Children]]:
        """ Получение предков проекта """
        return await self._get_list([self._PROJECTS_URL, name, 'ancestors'], convert_children,
                                    **query_params)

    async def get_project_path(self, name: str) -> Optional[str]:
        """ Получение пути оргструктуры проекта по name """
        return await self._get_list([self._PROJECTS_URL, name, 'path'], convert_path)

    # Resource services

    async def get_resource_services(self, **query_params) -> Optional[List[ResourceService]]:
        """ Получение списка сервисов """
        return await self._get_list([self._RESOURCE_SERVICES_URL], convert_resource_service, **query_params)

    async def get_resource_service(self, name: str) -> Optional[ResourceService]:
        """ Получение сервиса по name """
        return await self._get_item([self._RESOURCE_SERVICES_URL], name, convert_resource_service)

    async def create_resource_service(self, **params) -> Optional[ResourceService]:
        """ Создание сервиса """
        return await self._create([self._RESOURCE_SERVICES_URL], convert_resource_service, resource_service=params)

    async def delete_resource_service(self, name: str) -> bool:
        """ Удаление сервиса """
        return await self._delete(self._RESOURCE_SERVICES_URL, name)

    async def update_resource_service(self, name: str, **params) -> Optional[ResourceService]:
        """ Обновление сервиса """
        return await self._patch(self._RESOURCE_SERVICES_URL, name, convert_resource_service, resource_service=params)

    # Resource types

    async def get_resource_types(self, **query_params) -> Optional[List[ResourceType]]:
        """ Получение списка ресурсных типов """
        return await self._get_list([self._RESOURCE_TYPE_URL], convert_resource_type, **query_params)

    async def get_resource_type(self, code: str) -> Optional[ResourceService]:
        """ Получение ресурсного типа по code """
        return await self._get_item([self._RESOURCE_TYPE_URL], code, convert_resource_type)

    async def create_resource_type(self, **params) -> Optional[ResourceType]:
        """ Создание ресурсного типа """
        return await self._create([self._RESOURCE_TYPE_URL], convert_resource_type, resource_type=params)

    async def delete_resource_type(self, code: str) -> bool:
        """ Удаление ресурсного типа """
        return await self._delete(self._RESOURCE_TYPE_URL, code)

    async def update_resource_type(self, code: str, **params) -> Optional[ResourceType]:
        """ Обновление ресурсного типа """
        return await self._patch(self._RESOURCE_TYPE_URL, code, convert_resource_type, resource_type=params)

    # Resource rules

    async def get_resource_rules(self, **query_params) -> Optional[List[ResourceRule]]:
        """ Получение списка ресурсных правил """
        return await self._get_list([self._RESOURCE_RULE_URL], convert_resource_rule, **query_params)

    async def bulk_update_resource_rules(self, service: str,
                                         resource_rules: List[Dict[str, str]]) -> Optional[List[ResourceRule]]:
        """ Обновление списка ресурсных правил у сервиса """
        request = {
            'method': "PATCH",
            'url': _join_str(self.base_url, self._RESOURCE_SERVICES_URL, service, self._RESOURCE_RULE_URL),
            'cfg': {'json': {
                "resource_service": {
                    "resource_rules": resource_rules
                }
            }, 'headers': self.headers}
        }

        status, response = await self.service.send_request(**request)

        return [convert_resource_rule(row) for row in response['data']] if status == 200 else None

    # Private
    async def _delete(self, url_path: str, item_id: Any) -> bool:
        """ Удаление объекта """
        request = {
            'method': "DELETE",
            'url': _join_str(self.base_url, url_path, str(item_id)),
            'cfg': {'headers': self.headers}
        }
        status, _ = await self.service.send_request(**request)

        return status == 204

    async def _patch(self, url_path: str, item_id: Any,
                     converter: Callable[[Dict[str, Any]], Any],
                     **json) -> Optional[Any]:
        """ Обновление объекта """
        request = {
            'method': "PATCH",
            'url': _join_str(self.base_url, url_path, str(item_id)),
            'cfg': {'json': json, 'headers': self.headers}
        }
        status, response = await self.service.send_request(**request)

        return converter(response['data']) if status == 200 else None

    async def _get_item(self, url_path: List[str], item_id: Any, converter: Callable[[Dict[str, Any]], Any]) -> \
            Optional[Any]:
        """ Получение объекта """
        request = {
            'method': "GET",
            'url': _join_str(self.base_url, *url_path, str(item_id)),
            'cfg': {'headers': self.headers}
        }
        status, response = await self.service.send_request(**request)

        return converter(response['data']) if status == 200 else None

    async def _get_list(self, url_path: List[str], converter: Callable[[Dict[str, Any]], Any],
                        **query_params) -> Optional[List]:
        """ Получение списка объектов """
        request = {
            'method': "GET",
            'url': _join_str(self.base_url, *url_path),
            'cfg': {'params': query_params, 'headers': self.headers}
        }
        status, response = await self.service.send_request(**request)
        if status == 200:
            data = response['data']

            return list(map(converter, data)) if isinstance(data, abc.MutableSequence) else converter(data)

        return None

    async def _create(self, url_path: List[str], converter: Callable[[Dict[str, Any]], Any],
                      **json) -> Optional[List]:
        """ Создание объекта """
        request = {
            'method': "POST",
            'url': _join_str(self.base_url, *url_path),
            'cfg': {'json': json, 'headers': self.headers}
        }
        status, response = await self.service.send_request(**request)

        return converter(response['data']) if status == 201 else None


def _join_str(*args, sep: Optional[str] = '/') -> str:
    return sep.join(arg.strip(sep) for arg in args)
