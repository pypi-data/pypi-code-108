from typing import NamedTuple, Optional


class Children(NamedTuple):
    """ Потомок организации """
    name: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    parent: Optional[str] = None
    kind: Optional[str] = None
    children_count: Optional[int] = None


class Folder(NamedTuple):
    """ Организация """
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    kind: Optional[str] = None
    organization: Optional[str] = None
    parent: Optional[str] = None
    children_count: Optional[int] = None


class Project(NamedTuple):
    """ Проект организации """
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    organization: Optional[str] = None
    folder: Optional[str] = None
    information_system_id: Optional[str] = None
    project_environment_id: Optional[str] = None
    environment_prefix_id: Optional[str] = None


class Organization(NamedTuple):
    """ Организация """
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class User(NamedTuple):
    """ Пользователь """
    remote_id: Optional[str] = None
    email: Optional[str] = None
    user_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ResourceService(NamedTuple):
    """ Сервис """
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class ResourceType(NamedTuple):
    """ Ресурсный тип """
    code: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    actions: Optional[str] = None


class ResourceRule(NamedTuple):
    """ Ресурсное правило """
    id: int
    url_pattern: Optional[str] = None
    http_method: Optional[str] = None
    access_type: Optional[str] = None
    operation_name: Optional[str] = None
    code: Optional[str] = None
