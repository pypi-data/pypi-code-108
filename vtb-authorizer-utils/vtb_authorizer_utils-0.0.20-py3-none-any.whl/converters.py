from typing import Dict, Any, Set

from vtb_authorizer_utils.data_objects import User, Organization, Project, Folder, Children, ResourceService, \
    ResourceType, ResourceRule


def convert_user(data: Dict[str, Any]) -> User:
    """ Конвертация ответа в data класс RemoteUser """
    return User(
        remote_id=data.get('id', None),
        email=data.get('email', None),
        user_name=data.get('username', None),
        first_name=data.get('firstname', None),
        last_name=data.get('lastname', None)
    )


def convert_organization(data: Dict[str, Any]) -> Organization:
    """ Конвертация ответа в data класс RemoteOrganization """
    return Organization(
        **_default_mapper({'name', 'title', 'description'}, data)
    )


def convert_project(data: Dict[str, Any]) -> Project:
    """ Конвертация ответа в data класс Project """
    return Project(
        **_default_mapper({'name', 'title', 'description', 'organization', 'folder', 'information_system_id',
                           'project_environment_id', 'environment_prefix_id'}, data)
    )


def convert_children(data: Dict[str, Any]) -> Children:
    """ Конвертация ответа в data класс Children """
    return Children(
        **_default_mapper({'name', 'title', 'type', 'parent', 'kind', 'children_count'}, data)
    )


def convert_folder(data: Dict[str, Any]) -> Folder:
    """ Конвертация ответа в data класс Folder """
    return Folder(
        **_default_mapper({'name', 'title', 'description', 'kind', 'organization', 'parent', 'children_count'}, data)
    )


def convert_resource_service(data: Dict[str, Any]) -> ResourceService:
    """ Конвертация ответа в data класс ResourceService """
    return ResourceService(
        **_default_mapper({'name', 'title', 'description', 'url'}, data)
    )


def convert_resource_type(data: Dict[str, Any]) -> ResourceType:
    """ Конвертация ответа в data класс ResourceType """
    return ResourceType(
        **_default_mapper({'code', 'title', 'description', 'actions'}, data)
    )


def convert_resource_rule(data: Dict[str, Any]) -> ResourceRule:
    """ Конвертация ответа в data класс ResourceRule """
    return ResourceRule(
        **_default_mapper({'id', 'url_pattern', 'http_method', 'access_type', 'operation_name', 'code'}, data)
    )


def convert_path(data: Dict[str, Any]) -> str:
    """ Получение пути из ответа """
    path = data['path'].strip('/')
    return f'/{path}/'


def _default_mapper(fields: Set[str], data: Dict[str, Any]) -> Dict[str, Any]:
    result = dict.fromkeys(fields)
    for field in fields:
        result[field] = data.get(field, None)

    return result
