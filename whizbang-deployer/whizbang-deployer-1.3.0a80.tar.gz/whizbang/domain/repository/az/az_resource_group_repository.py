from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.az_resource_base import AzResourceGroup
from whizbang.domain.repository.az.az_resource_repository_base import IAzResourceRepository, AzResourceRepositoryBase

import logging
_log = logging.getLogger(__name__) 


class IAzResourceGroupRepository(IAzResourceRepository):
    """the AzResourceGroupRepository interface"""

class AzResourceGroupRepository(AzResourceRepositoryBase, IAzResourceGroupRepository):
    def __init__(self, context: AzCliContext):
        AzResourceRepositoryBase.__init__(self, context)

    @property
    def _resource_provider(self) -> str: return 'group'

    def create(self, resource: AzResourceGroup):
        if resource.location is None or resource.location == '':
            raise TypeError('Specify a location to use for the Resource Group (i.e. eastus2)')

        resource_group = self._execute(f'show --name {resource.resource_group_name}').results

        if resource_group is None:
            self._execute(f'create --name {resource.resource_group_name} --location {resource.location}')
        else:
            _log.info(f'resource group: {resource.resource_group_name} already exists')


