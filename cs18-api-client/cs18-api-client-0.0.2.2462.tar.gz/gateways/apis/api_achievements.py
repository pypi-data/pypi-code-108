from gateways.apis.api_base_class import ApiBase


class ApiAchievements(ApiBase):
    def achievements(self, space_name: str):
        return self.build_route("spaces/{space_name}/achievements".format(**locals()))
