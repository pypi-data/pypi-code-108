from typing import List

from nehushtan.httpd.NehushtanHTTPRoute import NehushtanHTTPRoute
from nehushtan.httpd.exceptions.NehushtanNoRouteMatchedError import NehushtanNoRouteMatchedError
from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger


class NehushtanHTTPRouter:
    """
    Since 0.4.0
    """

    def __init__(self, logger: NehushtanFileLogger = None):
        self.__route_list: List[NehushtanHTTPRoute] = []
        self.__logger = logger

    def register_route(self, route: NehushtanHTTPRoute):
        self.__route_list.append(route)

        if self.__logger is not None:
            self.__logger.debug(f'NehushtanHTTPRouter::register_route {route}')

        return self

    def check_request_for_route(self, method: str, path: str) -> NehushtanHTTPRoute:
        for route in self.__route_list:
            matched = route.match_request(method, path)
            if self.__logger is not None:
                self.__logger.debug(f'NehushtanHTTPRouter::check_request_for_route',
                                    {'matched': matched, 'method': method, 'path': path, 'route': route})
            if matched:
                return route

        raise NehushtanNoRouteMatchedError(
            http_error_message=f'Request [{method} {path}] Matched No Rotue.',
            http_code=404
        )
