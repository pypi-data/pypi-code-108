from aiohttp import hdrs, web
from heaobject import root
from heaobject.root import DesktopObject, DesktopObjectTypeVar
from heaobject.registry import Component, Property
from heaobject.volume import DEFAULT_FILE_SYSTEM
from . import appproperty, response
from .aiohttp import StreamReaderWrapper, SupportsAsyncRead
from .representor import nvpjson
from yarl import URL
from typing import Optional, Union, Dict, Type, Mapping
import logging


async def get_streaming(request: web.Request, url: Union[str, URL], headers: Optional[Dict[str, str]] = None) -> web.StreamResponse:
    _logger = logging.getLogger(__name__)
    session = request.app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting streaming content at %s with headers %s', url, headers)
    async with session.get(url, headers=headers, raise_for_status=False) as response_:
        if response_.status == 200:
            content_type = response_.headers.get(hdrs.CONTENT_TYPE, None)
            return await response.get_streaming(request, StreamReaderWrapper(response_.content), content_type=content_type)
        elif response_.status == 404:
            return response.status_not_found()
        else:
            return web.Response(status=response_.status)


async def put_streaming(request: web.Request, url: Union[str, URL], data: SupportsAsyncRead, headers: Optional[Dict[str, str]] = None) -> None:
    session = request.app[appproperty.HEA_CLIENT_SESSION]
    async with session.put(url, data=data, headers=headers) as response_:
        pass


async def get_dict(app, url, headers=None) -> Optional[dict]:
    """
    Co-routine that gets a dict from a HEA service that returns JSON.

    :param app: the aiohttp application context (required).
    :param url: The URL (str or URL) of the resource (required).
    :param headers: optional dict of headers.
    :return: the dict populated with the resource's content, None if no such resource exists, or another HTTP
    status code if an error occurred.
    """
    _logger = logging.getLogger(__name__)
    session = app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting dict at %s with headers %s', url, headers)
    async with session.get(url, headers=headers, raise_for_status=False) as response_:
        if response_.status == 404:
            return None
        else:
            response_.raise_for_status()
            result = await response_.json()
            _logger.debug('Client returning %s', result)
            result_len = len(result);
            if result_len != 1:
                raise ValueError(f'Result from {url} has {result_len} values')
            return result[0] if isinstance(result, list) else result


async def get(app: web.Application, url: Union[URL, str], obj: Union[str, DesktopObjectTypeVar, Type[DesktopObjectTypeVar]], headers: Optional[Mapping[str, str]] = None) -> Optional[DesktopObjectTypeVar]:    # type: ignore[return]
    """
    Co-routine that gets a HEA desktop object from a HEA service.

    :param app: the aiohttp application context (required).
    :param url: The URL (str or URL) of the resource (required).
    :param obj: the HEA desktop object type to populate with the resource's content, or a desktop object instance. If a type or type
    name, this function will attempt to create an instance using the type's no-arg constructor.
    :param headers: optional dict of headers. Attempts to set the Accept header will be ignored. The service will
    always receive Accepts: application/json.
    :return: the HEAObject populated with the resource's content, None if no such resource exists, or another HTTP
    status code if an error occurred.
    """
    _logger = logging.getLogger(__name__)
    if isinstance(obj, str):
        obj__ = root.type_for_name(obj)
        if isinstance(obj__, root.DesktopObject):
            obj = obj__
        else:
            raise ValueError(f'Type {obj} is not a DesktopObject')
    if isinstance(obj, type) and issubclass(obj, root.DesktopObject):
        obj_ = obj()
    elif isinstance(obj, root.DesktopObject):
        obj_ = obj
    else:
        raise TypeError('obj must be an HEAObject instance, an HEAObject type, or an HEAObject type name')
    headers_ = dict(headers) if headers else {}
    headers_[hdrs.ACCEPT] = nvpjson.MIME_TYPE

    session = app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting content at %s with headers %s', url, headers_)
    async with session.get(url, headers=headers_, raise_for_status=False) as response_:
        if response_.status == 404:
            return None
        else:
            response_.raise_for_status()
            result = await response_.json()
            _logger.debug('Client returning %s', result)
            result_len = len(result);
            if result_len != 1:
                raise ValueError(f'Result from {url} has {result_len} values')
            obj_.from_dict(result[0])
            return obj_


async def get_all(app: web.Application, url: Union[URL, str], obj: Type[DesktopObject], headers: Optional[Dict[str, str]] = None):    # type: ignore[return]
    """
    Generator that returns the requested HEAObjects.

    :param app: the aiohttp application context (required).
    :param url: The URL (str or URL) of the resource (required).
    :param obj: the HEAObject type to populate with the resource's content.
    :param headers: optional dict of headers. Attempts to set the Accept header will be ignored. The service will
    always receive Accepts: application/json.
    """
    _logger = logging.getLogger(__name__)
    if isinstance(obj, str):
        obj = root.type_for_name(obj)
    if isinstance(obj, type) and issubclass(obj, root.DesktopObject):
        obj_ = obj
    else:
        raise TypeError('obj must be an HEAObject instance, an HEAObject type, or an HEAObject type name')
    headers_ = dict(headers) if headers else {}
    headers_[hdrs.ACCEPT] = nvpjson.MIME_TYPE

    session = app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Getting content at %s with headers %s', url, headers_)
    async with session.get(url, headers=headers_, raise_for_status=False) as response_:
        response_.raise_for_status()
        result = await response_.json()
        _logger.debug('Client returning %s', result)
        for r in result:
            obj__ = obj_()
            obj__.from_dict(r)
            yield obj__


async def post(app: web.Application, url: Union[URL, str], data: root.HEAObject, headers: Dict[str, str] = None) -> str:    # type: ignore[return]
    """
    Coroutine that posts a HEAObject to a HEA service.

    :param app: the aiohttp application context (required).
    :param url: the The URL (str or URL) of the resource (required).
    :param data: the HEAObject (required).
    :param headers: optional dict of headers.
    :return: the URL string in the response's Location header.
    """
    session = app[appproperty.HEA_CLIENT_SESSION]
    async with session.post(url, json=data, headers=headers) as response_:
        return response_.headers['Location']


async def put(app: web.Application, url: Union[URL, str], data: root.HEAObject, headers: Dict[str, str] = None) -> None:
    """
    Coroutine that updates a HEAObject.

    :param app: the aiohttp application context (required).
    :param url: the The URL (str or URL) of the resource (required).
    :param data: the HEAObject (required).
    :param headers: optional dict of headers.
    """
    session = app[appproperty.HEA_CLIENT_SESSION]
    async with session.put(url, json=data, headers=headers) as response_:
        pass


async def delete(app: web.Application, url: Union[URL, str], headers: Dict[str, str] = None) -> None:
    """
    Coroutine that deletes a HEAObject.

    :param app: the aiohttp application context (required).
    :param url: the URL (str or URL) of the resource (required).
    :param headers: optional dict of headers.
    """
    _logger = logging.getLogger(__name__)
    session = app[appproperty.HEA_CLIENT_SESSION]
    _logger.debug('Deleting %s', str(url))
    async with session.delete(url, headers=headers) as response_:
        pass


async def get_component_by_name(app: web.Application, name: str) -> Optional[Component]:
    """
    Gets the Component with the given name from the HEA registry service.
    :param app: the aiohttp app.
    :param name: the component's name.
    :return: a Component instance or None (if not found).
    """
    return await get(app, URL(app[appproperty.HEA_REGISTRY]) / 'components' / 'byname' / name, Component)


async def get_resource_url(app: web.Application, type_or_type_name: Union[str, Type[root.HEAObject]],
                           file_system_name: Optional[str] = DEFAULT_FILE_SYSTEM) -> Optional[str]:
    """
    Gets the resource URL corresponding to the HEA object type from the HEA registry service.
    :param app: the aiohttp app.
    :param type_or_type_name: the HEAObject type or type name of the resource.
    :param file_system_name: optional file system name. The default is heaobject.volume.FileSystem.DEFAULT_FILE_SYSTEM.
    :return: a URL string or None (if not found).
    """
    if file_system_name is None:
        file_system_name_ = DEFAULT_FILE_SYSTEM
    else:
        file_system_name_ = file_system_name
    type_ = _handle_type_or_type_name_arg(type_or_type_name)
    url = URL(app[appproperty.HEA_REGISTRY]) / 'components' / 'bytype' / type_ / 'byfilesystemname' / file_system_name_
    component: Optional[Component] = await get(app, url, Component)
    return component.get_resource_url(type_, file_system_name=file_system_name_) if component is not None else None


async def get_property(app: web.Application, name: str) -> Optional[Property]:
    """
    Gets the Property with the given name from the HEA registry service.
    :param app: the aiohttp app.
    :param name: the property's name.
    :return: a Property instance or None (if not found).
    """
    return await get(app, URL(app[appproperty.HEA_REGISTRY]) / 'properties' / 'byname' / name, Property)


def _handle_type_or_type_name_arg(type_or_type_name):
    if isinstance(type_or_type_name, str) and root.is_heaobject_type(type_or_type_name):
        return type_or_type_name
    elif isinstance(type_or_type_name, type) and issubclass(type_or_type_name, root.HEAObject):
        return type_or_type_name.get_type_name()
    else:
        raise TypeError('type_or_type_name must be an HEAObject type')
