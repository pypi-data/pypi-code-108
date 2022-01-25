from whizbang.domain.manager.az.az_resource_manager_base import IAzResourceManager, AzResourceManagerBase
from whizbang.domain.repository.az.az_resource_group_repository import IAzResourceGroupRepository


class IAzResourceGroupManager(IAzResourceManager):
    """the AzResourceGroupManager interface"""


class AzResourceGroupManager(AzResourceManagerBase, IAzResourceGroupManager):
    def __init__(self, repository: IAzResourceGroupRepository):
        AzResourceManagerBase.__init__(self, repository)
