from abc import abstractmethod

from whizbang.core.workflow_task import WorkflowTask, IWorkflowTask
from whizbang.domain.manager.bicep.bicep_deployment_manager import BicepDeploymentManager
from whizbang.domain.models.bicep_deployment import BicepDeployment
from whizbang.domain.models.template_deployment_result import TemplateDeploymentResult
from whizbang.domain.models.template_parameters_wrapper import TemplateParametersWrapper
from whizbang.util.json_helpers import export_local_json


class BicepTaskNames:
    deploy_bicep_template: str = 'deploy_bicep_template'
    write_bicep_parameters_file: str = 'write_bicep_parameters_file'


class IBicepDeploymentTask(IWorkflowTask):
    """"""

    @abstractmethod
    def run(self, deployment: BicepDeployment):
        """"""


class WriteBicepParametersFileTask(WorkflowTask, IBicepDeploymentTask):
    @property
    def task_name(self) -> str: return BicepTaskNames.write_bicep_parameters_file

    def run(self, deployment: BicepDeployment):
        parameters_path = deployment.parameters_path
        parameters = deployment.parameters

        parameters_wrapper: TemplateParametersWrapper = TemplateParametersWrapper(parameters)
        export_local_json(parameters_path, parameters_wrapper)


class DeployBicepTemplateTask(WorkflowTask, IBicepDeploymentTask):
    @property
    def task_name(self) -> str: return BicepTaskNames.deploy_bicep_template

    def __init__(self, bicep_deployment_manager: BicepDeploymentManager):
        WorkflowTask.__init__(self)
        self.bicep_deployment_manager = bicep_deployment_manager

    def run(self, deployment: BicepDeployment) -> TemplateDeploymentResult:
        return self.bicep_deployment_manager.deploy(deployment)
