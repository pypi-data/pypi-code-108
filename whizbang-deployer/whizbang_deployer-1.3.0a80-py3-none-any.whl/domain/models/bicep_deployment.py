from whizbang.domain.models.template_parameters_base import TemplateParametersBase


class BicepDeployment:
    def __init__(
            self,
            deployment_name: str,
            solution_name: str,
            parameters: TemplateParametersBase,
            resource_group_name: str,
            resource_group_location: str,
            template_path: str,
            parameters_path: str
    ):
        self.template_path = template_path
        self.parameters_path = parameters_path
        self.deployment_name = deployment_name
        self.resource_group_location = resource_group_location
        self.resource_group_name = resource_group_name
        self.solution_name = solution_name
        self.parameters = parameters
