from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.models.bicep_deployment import BicepDeployment
from whizbang.domain.workflow.bicep.bicep_tasks import BicepTaskNames
from whizbang.domain.workflow.bicep.deploy_bicep_workflow import DeployBicepWorkflow
from whizbang.domain.models.template_deployment_result import TemplateDeploymentResult
from whizbang.util import path_defaults
from whizbang.util.json_helpers import export_json_dict
from whizbang.util.path_defaults import get_output_path


class IBicepHandler(IHandler):
    """"""

    def deploy_bicep_template(self, solution_name: str, parameters, environment_config: EnvironmentConfig):
        """"""


class BicepHandler(HandlerBase, IBicepHandler):
    def __init__(self, app_config: AppConfig, deploy_bicep_workflow: DeployBicepWorkflow):
        HandlerBase.__init__(self, app_config=app_config)
        self.__deploy_bicep_workflow = deploy_bicep_workflow

    def deploy_bicep_template(self, solution_name: str, parameters,
                              environment_config: EnvironmentConfig, deployment_name: str = None) -> TemplateDeploymentResult:
        template_path = path_defaults.get_bicep_template_path(app_config=self._app_config, solution_name=solution_name)
        parameters_path = path_defaults.get_bicep_parameters_path(app_config=self._app_config,
                                                                  solution_name=solution_name)

        deployment_name = deployment_name or solution_name

        deployment = BicepDeployment(
            parameters=parameters,
            solution_name=solution_name,
            template_path=template_path,
            parameters_path=parameters_path,
            resource_group_name=environment_config.resource_group_name,
            resource_group_location=environment_config.resource_group_location,
            deployment_name=deployment_name
        )

        result = self.__deploy_bicep_workflow.run(deployment)
        deployment_result: TemplateDeploymentResult = result[BicepTaskNames.deploy_bicep_template]
        self.__write_bicep_output(deployment_result, deployment_name)
        return deployment_result

    def __write_bicep_output(self, deployment_result: TemplateDeploymentResult, deployment_name):
        output_path = f'{get_output_path(self._app_config)}/{deployment_name}_bicep_output.json'
        export_json_dict(output_path, deployment_result.outputs)


