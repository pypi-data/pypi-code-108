from gateways.apis.api_base_class import ApiBase


class ApiPolicy(ApiBase):
    def blueprint_policy(self, space_name: str, blueprint_name: str):
        return self.build_route(f"spaces/{space_name}/blueprints/{blueprint_name}/policies")
