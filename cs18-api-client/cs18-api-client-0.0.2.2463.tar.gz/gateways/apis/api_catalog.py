from gateways.apis.api_base_class import ApiBase


class ApiCatalog(ApiBase):
    def catalog(self, space_name: str):
        return self.build_route("spaces/{space_name}/catalog".format(**locals()))

    def blueprint_in_catalog(self, space_name: str, blueprint_name: str):
        return self.build_route(
            "spaces/{space_name}/catalog/{blueprint_name}".format(**locals())
        )
