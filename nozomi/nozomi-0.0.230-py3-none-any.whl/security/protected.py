"""
Nozomi
Protected Protocol
Copyright Amatino Pty Ltd
"""
from nozomi.security.agent import Agent
from nozomi.security.permission_record import PermissionRecord
from nozomi.security.read_protected import ReadProtected


class Protected(ReadProtected):
    """
    Abstract protocol defining an interface for objects to whom access is
    limited.
    """

    permission_record: PermissionRecord = NotImplemented

    def grants_read_to(self, agent: Agent) -> bool:
        return self.permission_record.records_read_permissions_for(agent)

    def grants_write_to(self, agent: Agent) -> bool:
        return self.permission_record.records_write_permissions_for(agent)

    def grants_admin_to(self, agent: Agent) -> bool:
        return self.permission_record.records_administration_rights_for(agent)

    def grants_management_to(self, agent: Agent) -> bool:
        return self.permission_record.records_management_rights_for(agent)

    def is_owned_by(self, agent: Agent) -> bool:
        return self.permission_record.records_ownership_by(agent)

