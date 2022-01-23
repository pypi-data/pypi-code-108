from gateways.apis.api_base_class import ApiBase


class ApiBlueprintValidation(ApiBase):
    def blueprint_validation_by_space_name(self, space_name: str):
        return self.build_route(
            "spaces/{space_name}/validations/blueprints".format(**locals())
        )
