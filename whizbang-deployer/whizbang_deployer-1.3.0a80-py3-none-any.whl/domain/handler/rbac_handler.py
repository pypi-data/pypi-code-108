from abc import abstractmethod

from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_base import IHandler, HandlerBase
from whizbang.domain.manager.az.az_rbac_manager import IAzRbacManager
from whizbang.domain.models.rbac_policy import RBACPolicy


class IRbacHandler(IHandler):
    """"""

    @abstractmethod
    def set_rbac(self, resource_ids: dict):
        """"""


class RbacHandler(HandlerBase, IRbacHandler):
    def __init__(self, app_config: AppConfig,  environment_config: EnvironmentConfig, rbac_manager: IAzRbacManager):
        HandlerBase.__init__(self, app_config=app_config)
        self.environment_config = environment_config
        self.__rbac_manager = rbac_manager
        self.rbac_policies_from_config = self.environment_config.rbac_policies

    def set_rbac(self, resource_ids: dict):
        rbac_policies: 'list[RBACPolicy]' = []
        
        for policy in self.rbac_policies_from_config:
            scope_name = policy.scope
            scope = resource_ids[scope_name]

            if policy.assignee in resource_ids:
                assignee = resource_ids[policy.assignee].split('/')[-1]
            else:
                assignee = policy.assignee

            role = policy.role
            assignee_type = policy.assignee_type

            rbac_policy = RBACPolicy(scope=scope, assignee=assignee, role=role, assignee_type=assignee_type)
            rbac_policies.append(rbac_policy)

        result = self.__rbac_manager.assign_resource_roles(rbac_policies)

    def assign_scoped_role(self, assignee_object_id, role, scope):
        return self.__rbac_manager.assign_scoped_role(assignee_object_id, role, scope)
