class HTTPInterface:
    def __init__(self, name, base_url, default_authentication_methods):
        self._name = name
        self._base_url = base_url
        self._default_authentication_methods = default_authentication_methods
        self._sections = self._initialize_sections()

    def name(self):
        return self._name

    def url(self):
        return f'{self._base_url}/{self._route_prefix()}'

    def description(self):
        raise NotImplementedError("Subclass responsibility")

    def version(self):
        raise NotImplementedError("Subclass responsibility")

    def sections(self):
        return self._sections

    def endpoints(self):
        return self._concatenate_all_endpoints_for_all_sections()

    def default_authentications_methods(self):
        return self._default_authentication_methods

    def authentication_methods_for_endpoint_named(self, endpoint_name):
        security_methods = self._authentication_methods_for_excepted_endpoint_named(endpoint_name)
        if security_methods is None:
            security_methods = self.default_authentications_methods()
        return security_methods

    def route_for_endpoint_named(self, endpoint_name, kwargs=None):
        if kwargs is None:
            kwargs = {}

        return f"/{self._route_prefix()}/{self.endpoint_named(endpoint_name).route_with_variable_replacements(kwargs)}"

    def route_pattern_for_endpoint_named(self, endpoint_name):
        return f"{self._route_prefix()}/{self.relative_route_pattern_for_endpoint_named(endpoint_name)}"

    def relative_route_pattern_for_endpoint_named(self, endpoint_name):
        return f"{self.endpoint_named(endpoint_name).route()}"

    def endpoint_named(self, endpoint_name):
        endpoints_with_name = [endpoint for endpoint in self.endpoints() if endpoint.name() == endpoint_name]
        self._validate_endpoint_exists_and_is_unique(endpoints_with_name, endpoint_name)
        return endpoints_with_name[0]

    def _initialize_sections(self):
        raise NotImplementedError("Subclass responsibility")

    def _authentication_methods_for_excepted_endpoint_named(self, endpoint_name):
        return self._authentication_methods_exceptions().get(endpoint_name)

    def _authentication_methods_exceptions(self):
        return {}

    def _concatenate_all_endpoints_for_all_sections(self):
        return [endpoint for section in self.sections() for endpoint in section.endpoints()]

    def _validate_endpoint_exists_and_is_unique(self, endpoint_list, endpoint_name):
        if len(endpoint_list) == 0:
            raise Exception(f"Endpoint named {endpoint_name} not found in interface named {self.name()}")
        elif len(endpoint_list) > 1:
            raise Exception(f"Multiple endpoints named {endpoint_name} found in interface named {self.name()}")

    def _route_prefix(self):
        raise NotImplementedError("Subclass responsibility")
