from typing import Union, Optional

from vtb_authorizer_utils.data_objects import Organization, Project, Folder
from vtb_authorizer_utils.gateway import AuthorizerGateway


async def get_path(gateway: AuthorizerGateway,
                   context_object: Union[Organization, Project, Folder]) -> Optional[str]:
    """
    Получение полного пути объекта контекста в иерархии
    :param gateway: AuthorizerGateway
    :param context_object: объект контекста
    :return: полный путь объекта контекста в иерархии
    """
    name = context_object.name
    if not name:
        raise ValueError('context_object.name is null or empty.')

    if isinstance(context_object, Organization):
        return f"/organization/{name}/"

    if isinstance(context_object, Project):
        return await gateway.get_project_path(name)

    return await gateway.get_folder_path(name)
