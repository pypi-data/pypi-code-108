from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Set

from vtb_authorizer_utils.data_objects import ResourceService, ResourceType, ResourceRule
from vtb_authorizer_utils.errors import ServiceImportError
from vtb_authorizer_utils.gateway import AuthorizerGateway


@dataclass
class ImportServiceResult:
    """ Результат импорта """
    service: ResourceService
    resource_types: Optional[List[ResourceType]]
    resource_rules: Optional[List[ResourceRule]]


# pylint: disable=too-many-locals
async def import_service_from_dict(gateway: AuthorizerGateway,
                                   cfg: Dict[str, Dict]) -> \
        List[ImportServiceResult]:
    """ Загрузка конфигурации ресурсных типов и правил для сервиса в виде словаря """
    import_result = []
    for service_name, service_cfg in cfg.items():
        # Создание/редактирование сервиса
        service_cfg['name'] = service_name
        service = await _create_or_update_service(gateway, service_cfg)
        if not service:
            raise ServiceImportError(f'Create or update service "{service_name}" error')
        # Работа с ресурсными правилами, создание/обновление и удаление нужно делать в ручном режиме
        resource_types_cfg = service_cfg.get('resource_types', {})
        existing_resource_types = await _get_existing_resource_types(gateway, service_name)
        new_resource_types = set(resource_types_cfg.keys())
        unused_resource_types = existing_resource_types - new_resource_types
        # Удаляем старые ресурсные типы
        for unused_resource_type in unused_resource_types:
            code = f'{service_name}:{unused_resource_type}'
            status = await gateway.delete_resource_type(code)
            if not status:
                raise ServiceImportError(f'Delete resource type "{code}" error')

        resource_types = []
        for resource_type_name, resource_type_cfg in resource_types_cfg.items():
            resource_type_cfg['name'] = resource_type_name
            resource_type = await _create_or_update_resource_type(gateway, service, resource_type_cfg)
            if not resource_type:
                raise ServiceImportError(f'Create or update resource type "{service_name}:{resource_type_name}" error')
            resource_types.append(resource_type)

        # Работа с ресурсными типами, создание/обновление и удаление производится на сервере
        resource_rules_cfg = service_cfg.get('resource_rules', [])
        resource_rules = []
        if resource_rules_cfg:
            resource_rules = await gateway.bulk_update_resource_rules(service.name, resource_rules_cfg)
            if not resource_rules:
                raise ServiceImportError('Bulk update resource rules error')

        import_result.append(ImportServiceResult(service, resource_types, resource_rules))

    return import_result


async def _get_existing_resource_types(gateway: AuthorizerGateway, service_name: str) -> Set[str]:
    existing_resource_types = await gateway.get_resource_types(resource_service=service_name)
    result = {x.code.split(':')[-1] for x in existing_resource_types}
    return result


async def _create_or_update_resource_type(gateway: AuthorizerGateway,
                                          service: ResourceService,
                                          cfg: Dict[str, Any]) -> ResourceType:
    name = cfg['name']
    title = cfg.get('title', '')
    description = cfg.get('description', '')
    actions = cfg.get('actions', '')

    resource_type = await gateway.get_resource_type(f'{service.name}:{name}')
    if resource_type:
        return await gateway.update_resource_type(f'{service.name}:{name}',
                                                  title=title,
                                                  description=description,
                                                  actions=actions)

    return await gateway.create_resource_type(resource_service=service.name,
                                              title=title,
                                              name=name,
                                              description=description,
                                              actions=actions)


async def _create_or_update_service(gateway: AuthorizerGateway, cfg: Dict[str, Any]) -> ResourceService:
    name = cfg['name']
    title = cfg['title']
    url = cfg['url']
    description = cfg.get('description', '')

    service = await gateway.get_resource_service(name)
    if service:
        return await gateway.update_resource_service(name,
                                                     title=title,
                                                     description=description,
                                                     url=url)

    return await gateway.create_resource_service(name=name,
                                                 title=title,
                                                 description=description,
                                                 url=url)
