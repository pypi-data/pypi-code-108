import logging
from abc import abstractmethod

from whizbang.domain.exceptions import AzCliResourceDoesNotExist
from whizbang.domain.manager.az.az_manager_base import AzManagerBase, IAzManager
from whizbang.domain.models.firewall_rule import FirewallRule
from whizbang.domain.models.sql.sql_server_resource import SqlServerResource
from whizbang.domain.repository.az.az_sql_server_firewall_repository import IAzSqlServerFirewallRepository

_log = logging.getLogger(__name__)

class IAzSqlServerFirewallManager(IAzManager):
    """"""

    @abstractmethod
    def save(self, sql_server: SqlServerResource,
             firewall_rule: FirewallRule):
        """"""

    @abstractmethod
    def remove(self, sql_server: SqlServerResource,
               firewall_rule_name: str):
        """"""


class AzSqlServerFirewallManager(AzManagerBase, IAzSqlServerFirewallManager):
    def __init__(self, repository: IAzSqlServerFirewallRepository):
        AzManagerBase.__init__(self, repository)
        self._repository: IAzSqlServerFirewallRepository

    def save(self, sql_server: SqlServerResource, firewall_rule: FirewallRule):
        try:
            if self._repository.show(sql_server, firewall_rule.name):
                self._repository.delete(sql_server, firewall_rule.name)
        except AzCliResourceDoesNotExist as dne:
            # catch potential 'DoesNotExist' exception from the 'self._repository.show' method
            pass
        result = self._repository.create(sql_server, firewall_rule)
        return result


    def remove(self, sql_server: SqlServerResource, firewall_rule_name: str) -> None:
        try:
            result = self._repository.delete(sql_server, firewall_rule_name=firewall_rule_name)
        except AzCliResourceDoesNotExist as dne:
            _log.warning(f'sql server firewall-rule {firewall_rule_name} on server {sql_server.resource_name} could not be deleted because it does not exist')


