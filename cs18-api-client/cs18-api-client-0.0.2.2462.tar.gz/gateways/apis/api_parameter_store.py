from gateways.apis.api_base_class import ApiBase


class ParameterStore(ApiBase):
    def parameters(self):
        return self.build_route("settings/parameters/")

    def parameter(self, parameter_name: str):
        return self.build_route(
            "settings/parameters/{parameter_name}".format(**locals()))
