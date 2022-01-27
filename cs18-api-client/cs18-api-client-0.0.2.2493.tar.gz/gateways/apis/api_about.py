from gateways.apis.api_base_class import ApiBase


class ApiAbout(ApiBase):
    def api_about(self) -> str:
        return self.build_route("about")
