from abc import abstractmethod

from whizbang.domain.manager.az.az_manager_base import IAzManager, AzManagerBase
from whizbang.domain.models.rbac_policy import RBACPolicy
from whizbang.domain.repository.az.az_rbac_repository import IAzRbacRepository


class IAzRbacManager(IAzManager):
    """the AzRbacManager interface"""

    @abstractmethod
    def get_role(self, role_name: str):
        """"""

    @abstractmethod
    def assign_resource_roles(self, rbac_policies: 'list[RBACPolicy]') -> list:
        """"""

    @abstractmethod
    def assign_resource_group_role(self, assignee_object_id, role, resource_group_name):
        """"""

    @abstractmethod
    def assign_scoped_role(self, assignee_object_id, role, scope):
        """"""

    @abstractmethod
    def assign_subscription_role(self, assignee_object_id, role, subscription_id):
        """"""


class AzRbacManager(AzManagerBase, IAzRbacManager):
    def __init__(self, repository: IAzRbacRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: IAzRbacRepository

    def get_role(self, role_name: str):
        return self._repository.get_role(role_name)

    def assign_resource_roles(self, rbac_policies: 'list[RBACPolicy]') -> list:
        return self._repository.assign_resource_roles(rbac_policies)

    def assign_resource_group_role(self, assignee_object_id, role, resource_group_name):
        self._repository.assign_resource_group_role(assignee_object_id, role, resource_group_name)

    def assign_scoped_role(self, assignee_object_id, role, scope):
        return self._repository.assign_scoped_role(assignee_object_id, role, scope)

    def assign_subscription_role(self, assignee_object_id, role, subscription_id):
        self._repository.assign_subscription_role(assignee_object_id, role, subscription_id)
