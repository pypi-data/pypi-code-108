"""
Convenience functions for handling HEAObjects.
"""

from . import client
from .representor import factory as representor_factory
from .representor.error import ParseException
from heaobject import root
from heaobject.root import DesktopObjectTypeVar
from heaobject.volume import DEFAULT_FILE_SYSTEM
from heaobject.error import DeserializeException
from heaobject.root import DesktopObject, desktop_object_type_for_name
from aiohttp import web
import logging
from typing import Union, Callable, Optional, Type


async def new_heaobject_from_type_name(request: web.Request, type_name: str) -> DesktopObject:
    """
    Creates a new HEA desktop object from the body of a HTTP request.
    :param request: the HTTP request.
    :param type_name: the type name of DesktopObject.
    :return: an instance of the given DesktopObject type.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    obj = desktop_object_type_for_name(type_name)()
    return await populate_heaobject(request, obj)


async def new_heaobject_from_type(request: web.Request, type_: Callable[[], DesktopObjectTypeVar]) -> DesktopObjectTypeVar:
    """
    Creates a new HEA desktop object from the body of a HTTP request.
    :param request: the HTTP request.
    :param type_: A DesktopObject type, or a callable that returns a DesktopObject. This is compared to the type
    of the HEA desktop object in the request body, and a DeserializeException is raised if the type of the HEA
    object is not an instance of this type. If the desktop object in the body has no type attribute, the type is
    assumed to be the provided type_.
    :return: an instance of the given DesktopObject type.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    try:
        representor = representor_factory.from_content_type_header(request.headers['Content-Type'])
        _logger.debug('Using %s input parser', representor)
        result = await representor.parse(request)
        _logger.debug('Got dict %s', result)
        actual_type = desktop_object_type_for_name(result['type']) if 'type' in result else type_
        if not issubclass(actual_type, type_):
            raise TypeError(f'Type of object in request body must be type {type_} but was {actual_type}')
        obj = actual_type()
        obj.from_dict(result)
        return obj
    except ParseException as e:
        _logger.exception('Failed to parse %s%s', request, e)
        raise DeserializeException from e
    except (ValueError, TypeError) as e:
        _logger.exception('Error', None, e)
        _logger.exception('Failed to parse %s%s', result, e)
        raise DeserializeException from e
    except Exception as e:
        _logger.exception('Got exception %s', e)
        raise DeserializeException from e


async def populate_heaobject(request: web.Request, obj: DesktopObjectTypeVar) -> DesktopObjectTypeVar:
    """
    Populate an HEA desktop object from a POST or PUT HTTP request.

    :param request: the HTTP request. Required.
    :param obj: the HEAObject instance. Required.
    :return: the populated object.
    :raises DeserializeException: if creating a HEA object from the request body's contents failed.
    """
    _logger = logging.getLogger(__name__)
    try:
        representor = representor_factory.from_content_type_header(request.headers['Content-Type'])
        _logger.debug('Using %s input parser', representor)
        result = await representor.parse(request)
        _logger.debug('Got dict %s', result)
        obj.from_dict(result)
        return obj
    except (ParseException, ValueError) as e:
        _logger.exception('Failed to parse %s%s', obj, e)
        raise DeserializeException from e
    except Exception as e:
        _logger.exception('Got exception %s', e)
        raise DeserializeException from e


async def type_to_resource_url(request: web.Request, type_or_type_name: Union[str, Type[DesktopObject]],
                               file_system_name: Optional[str] = DEFAULT_FILE_SYSTEM) -> Optional[str]:
    """
    Use the HEA registry service to get the resource URL for accessing HEA objects of the given type.

    :param request: the HTTP request. Required.
    :param type_or_type_name: the type name of HEAObject. Required.
    :param file_system_name: the name of a file system. The default is filesystems.DEFAULT.
    :return: the URL string, or None if no resource URL was found.
    """
    return await client.get_resource_url(request.app, type_or_type_name, file_system_name)
