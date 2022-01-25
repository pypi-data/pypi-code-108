from abc import abstractmethod

from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.rbac_policy import RBACPolicy
from whizbang.domain.repository.az.az_active_directory_repository import AzActiveDirectoryRepository
from whizbang.domain.repository.az.az_repository_base import IAzRepository, AzRepositoryBase


class IAzRbacRepository(IAzRepository):
    """The AzRbacRepository interface"""

    @abstractmethod
    def get_role(self, role_name):
        """the get_role interface"""

    @abstractmethod
    def assign_resource_role(self, rbac_policy: RBACPolicy):
        """the assign_resource_role interface"""

    @abstractmethod
    def assign_resource_roles(self, rbac_policies: 'list[RBACPolicy]') -> list:
        """the assign_resource_roles interface"""

    @abstractmethod
    def assign_resource_group_role(self, assignee_object_id, role, resource_group_name):
        """"""

    @abstractmethod
    def assign_scoped_role(self, assignee_object_id, role, scope):
        """"""

    @abstractmethod
    def assign_subscription_role(self, assignee_object_id, role, subscription_id):
        """"""


class AzRbacRepository(AzRepositoryBase, IAzRbacRepository):
    def __init__(self, context: AzCliContext, active_directory_repository: AzActiveDirectoryRepository):
        AzRepositoryBase.__init__(self, context)
        self.az_active_directory_repository = active_directory_repository

    @property
    def _resource_provider(self) -> str:
        return 'role'

    def get_role(self, role_name):
        response = self._execute(f'definition list --name "{role_name}"')

        return response.results

    
    def assign_resource_role(self, rbac_policy: RBACPolicy) -> object:
        assignee_object_id = self.az_active_directory_repository.get_object_id(
            lookup_type=rbac_policy.assignee_type,
            lookup_value=rbac_policy.assignee
        )
        response = self._execute(f'assignment create --assignee {assignee_object_id} --role "{rbac_policy.role}" --scope {rbac_policy.scope}')
        
        return response.results

    def assign_resource_roles(self, rbac_policies: 'list[RBACPolicy]') -> list:
        policies_saved = []
        for policy in rbac_policies:
            result = self.assign_resource_role(policy)
            policies_saved.append(result)

        return policies_saved

    # resource group: you need name of resource group
    def assign_resource_group_role(self, assignee_object_id, role, resource_group_name):
        response = self._execute(f'assignment create'
                             f' --assignee {assignee_object_id}'
                             f' --role "{role}"'
                             f' --resource_group {resource_group_name}')
        return response.results 

    def assign_scoped_role(self, assignee_object_id, role, scope):
        response = self._execute(f'assignment create'
                                 f' --assignee {assignee_object_id}'
                                 f' --role "{role}"'
                                 f' --scope {scope}')
        return response.results
            
    # subscription: you need subscription id
    def assign_subscription_role(self, assignee_object_id, role, subscription_id):
        response = self._execute(f'assignment create'
                             f' --assignee {assignee_object_id}'
                             f' --role "{role}"'
                             f' --subscription {subscription_id}')
        
        return response.results

    # management group: you need managment group name
