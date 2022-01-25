from abc import abstractmethod

from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.models.bicep_deployment import BicepDeployment
from whizbang.domain.models.template_deployment_result import TemplateDeploymentResult
from whizbang.domain.repository.az.az_repository_base import IAzRepository, AzRepositoryBase
from whizbang.domain.repository.az.az_resource_group_repository import AzResourceGroupRepository
from whizbang.util import deployment_helpers

import logging
_log = logging.getLogger(__name__) 


class IAzDeploymentRepository(IAzRepository):
    """the AzDeploymentRepository interface """

    @abstractmethod
    def create(self, deployment: BicepDeployment) -> TemplateDeploymentResult:
        """"""


class AzDeploymentRepository(AzRepositoryBase, IAzDeploymentRepository):
    def __init__(self, context: AzCliContext, az_resource_group_repository: AzResourceGroupRepository):
        AzRepositoryBase.__init__(self, context)
        self.__az_resource_group_repository = az_resource_group_repository

    @property
    def _resource_provider(self) -> str: return 'deployment'

    def create(self, deployment: BicepDeployment) -> TemplateDeploymentResult:
        timestamp = deployment_helpers.timestamp
        _log.info(timestamp(f'begin {deployment.solution_name} bicep template deployment'))

        self.__az_resource_group_repository.create(AzResourceGroup(
            resource_group_name=deployment.resource_group_name,
            location=deployment.resource_group_location
        ))

        result = self._execute(f'group create'
                               f' --name {deployment.deployment_name}'
                               f' --resource-group {deployment.resource_group_name}'
                               f' --template-file {deployment.template_path}'
                               f' --parameters @{deployment.parameters_path}').results

        deployment_result = TemplateDeploymentResult(result)

        return deployment_result
