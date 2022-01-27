from __future__ import unicode_literals

import django

from tcell_agent.tcell_logger import get_module_logger

try:
    DJANGO_VERSION = tuple([int("".join(i for i in x if i.isnumeric())) for x in django.get_version().split(".")])

    if DJANGO_VERSION[0] >= 2:
        from django.urls import Resolver404, get_resolver  # pylint: disable=no-name-in-module
    elif DJANGO_VERSION[:2] >= (1, 10):
        from django.urls.resolvers import Resolver404, get_resolver  # pylint: disable=no-name-in-module
    else:
        from django.core.urlresolvers import Resolver404, get_resolver
except Exception as e:
    DJANGO_VERSION = (0, 0, 0)
    get_module_logger(__name__).warn("Could not determine Django version {e}: ".format(e=e))


def get_route_handler(path_info):
    try:
        resolver = get_resolver(None)
        return resolver.resolve(path_info)
    except Resolver404:
        pass
    except Exception as route_ex:
        LOGGER = get_module_logger(__name__)
        LOGGER.error("Unknown resolver error {e}".format(e=route_ex))
        LOGGER.exception(route_ex)

    return None


def get_url_patterns():
    resolver = get_resolver(None)
    return resolver.url_patterns
