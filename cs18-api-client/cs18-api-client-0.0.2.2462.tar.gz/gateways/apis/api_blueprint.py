from gateways.apis.api_base_class import ApiBase


class ApiBlueprint(ApiBase):
    def blueprints_by_space_name(self, space_name: str):
        return self.build_route("spaces/{space_name}/blueprints".format(**locals()))

    def blueprint_files(self, space_name: str, blueprint_name: str, branch: str):
        return self.build_route(
            "spaces/{space_name}/blueprints/{blueprint_name}/{branch}/files".format(
                **locals()
            )
        )
