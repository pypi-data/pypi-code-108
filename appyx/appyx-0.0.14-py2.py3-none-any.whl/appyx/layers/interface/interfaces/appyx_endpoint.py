import re


class AppyxEndpoint:
    def __init__(self, handler, route, name, interface) -> None:
        super().__init__()
        self._route = route
        self._handler = handler
        self._name = name
        self._interface = interface

    def interface(self):
        return self._interface

    def get_authentication_methods(self):
        return self.interface().authentication_methods_for_endpoint_named(self.name())

    def route(self):
        return self._route

    def route_with_variable_replacements(self, kwargs=None):
        if kwargs is None:
            kwargs = {}

        def replace(m):
            variable_name = m.group(1)
            return str(kwargs[variable_name])

        pattern = self._pattern_for_variables_in_url()
        replaced_route = re.sub(pattern, replace, self._route)
        return replaced_route

    def handler(self):
        return self._handler

    def http_method_to_handler(self):
        http_method_name = self.http_method().lower()
        return {http_method_name: self.handler()}

    def name(self):
        return self._name

    def http_method(self):
        # This is coupled with Django :(
        return self.handler().allowed_methods[0]

    def _pattern_for_variables_in_url(self):
        return r"<[a-z]+:(?P<variable_name>[\_\-a-zA-Z0-9]+)>"
