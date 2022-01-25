from gateways.apis.api_base_class import ApiBase


class ApiProduction(ApiBase):
    def __init__(self, api_address: str, space_name: str, version: str = None):
        super().__init__(api_address, version)
        self._space = space_name

    def productions(self):
        return self.build_route('spaces/{self._space}/production'.format(**locals()))
    
    def production_by_id(self, production_id: str):
        url = 'spaces/{self._space}/production/{production_id}'.format(**locals())
        return self.build_route(url)

    def green_by_id(self, production_id: str, env_type: str = None):
        url = 'spaces/{self._space}/production/{production_id}/green'.format(**locals())
        return self.build_route(url)

    def expose_green(self, production_id: str, exposure_value: str):
        url = 'spaces/{self._space}/production/{production_id}/green/exposure?value={exposure_value}'.format(**locals())
        return self.build_route(url)

    def promote_green(self, production_id: str):
        url = 'spaces/{self._space}/production/{production_id}/green/promote'.format(**locals())
        return self.build_route(url)

    def blue_debugging_service(self, production_id: str):
        url = 'spaces/{self._space}/production/{production_id}/debuggingservice'.format(**locals())
        return self.build_route(url)

    def green_debugging_service(self, production_id: str):
        url = 'spaces/{self._space}/production/{production_id}/green/debuggingservice'.format(**locals())
        return self.build_route(url)

    def delete_green(self, production_id: str):
        url = 'spaces/{self._space}/production/{production_id}/green'.format(**locals())
        return self.build_route(url)
