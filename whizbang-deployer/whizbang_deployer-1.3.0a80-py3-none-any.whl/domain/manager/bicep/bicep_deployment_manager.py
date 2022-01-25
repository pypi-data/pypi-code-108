from abc import abstractmethod

from whizbang.config.app_config import AppConfig
from whizbang.domain.manager.az.az_manager_base import IAzManager, AzManagerBase
from whizbang.domain.manager.az.az_resource_group_manager import IAzResourceGroupManager
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.models.bicep_deployment import BicepDeployment
from whizbang.domain.models.template_deployment_result import TemplateDeploymentResult
from whizbang.domain.repository.az.az_deployment_respository import IAzDeploymentRepository
from whizbang.util import deployment_helpers

import logging

_log = logging.getLogger(__name__) 


class IBicepDeploymentManager(IAzManager):
    """"""

    @abstractmethod
    def deploy(self, deployment: BicepDeployment) -> TemplateDeploymentResult:
        """"""


class BicepDeploymentManager(AzManagerBase, IBicepDeploymentManager):
    def __init__(
            self,
            app_config: AppConfig,
            repository: IAzDeploymentRepository,
            resource_group_manager: IAzResourceGroupManager
    ):
        AzManagerBase.__init__(self, repository)
        self._repository: IAzDeploymentRepository
        self.__resource_group_manager = resource_group_manager
        self.__app_config = app_config

    def deploy(self, deployment: BicepDeployment) -> TemplateDeploymentResult:
        timestamp = deployment_helpers.timestamp
        _log.info(timestamp(f'begin {deployment.solution_name} bicep template deployment'))

        self.__resource_group_manager.create(AzResourceGroup(
            resource_group_name=deployment.resource_group_name,
            location=deployment.resource_group_location
        ))

        _log.info(f'file to deploy: {deployment.template_path}')
        return self._repository.create(deployment)
