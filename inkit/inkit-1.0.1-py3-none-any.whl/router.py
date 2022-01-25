import json

from collections import namedtuple
from pkg_resources import resource_stream

from inkit.exceptions import InkitRouterException


Route = namedtuple('Route', ['path', 'http_method', 'sdk_method_name', 'doc'])


class Router:

    config_map = json.load(resource_stream('inkit', 'data/routing-config-map.json'))

    @classmethod
    def get_routes(cls, product_name):
        routes = [
            Route(path=route['path'],
                  sdk_method_name=route['sdk_method_name'],
                  http_method=route['http_method'],
                  doc=route['doc'])
            for route in cls.config_map[product_name]['routes']
        ]
        if not routes:
            raise InkitRouterException(
                message=f'Routes not found for product {product_name}'
            )

        return routes
