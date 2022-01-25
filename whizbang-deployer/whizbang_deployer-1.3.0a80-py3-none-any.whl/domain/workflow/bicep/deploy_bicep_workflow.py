from abc import abstractmethod

from whizbang.core.workflow import Workflow, IWorkflow
from whizbang.domain.models.bicep_deployment import BicepDeployment
from whizbang.domain.workflow.bicep.bicep_tasks import IBicepDeploymentTask


class IDeployBicepWorkflow(IWorkflow):
    """"""
    @abstractmethod
    def run(self, deployment: BicepDeployment):
        pass


class DeployBicepWorkflow(Workflow, IDeployBicepWorkflow):
    def __init__(
        self,
        write_bicep_parameters_file_task: IBicepDeploymentTask,
        deploy_bicep_template_task: IBicepDeploymentTask
    ):
        self.__deploy_bicep_template_task = deploy_bicep_template_task
        self.__write_bicep_parameters_file_task = write_bicep_parameters_file_task

    def _get_workflow_tasks(self) -> 'list[IBicepDeploymentTask]':
        return [
            self.__write_bicep_parameters_file_task,
            self.__deploy_bicep_template_task
        ]
