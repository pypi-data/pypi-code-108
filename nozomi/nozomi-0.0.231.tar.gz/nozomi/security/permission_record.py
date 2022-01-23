"""
Nozomi
Permission Record Module
Copyright Amatino Pty Ltd
"""
from nozomi.data.codable import Codable
from nozomi.security.agent import Agent
from typing import Union, TypeVar, Any, Type, List, Optional
from nozomi.security.machine_agent import MACHINE_AGENT

T = TypeVar('T', bound='PermissionRecord')


class PermissionRecord(Codable):
    """A record of ownership and read / write permissions for an object"""

    def __init__(
        self,
        owned_by: Union[str, int],
        readable_by: Optional[List[Union[str, int]]],
        writable_by: Optional[List[Union[str, int]]],
        managed_by: Optional[List[Union[str, int]]],
        administered_by: Optional[List[Union[str, int]]]
    ) -> None:

        self._owned_by = owned_by
        self._readable_by = readable_by or []
        self._writable_by = writable_by or []
        self._managed_by = managed_by or []
        self._administered_by = administered_by or []

        return

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:
        return cls(
            owned_by=data['owned_by'],
            readable_by=data['readable_by'] if 'readable_by' in data else None,
            writable_by=data['writable_by'] if 'writable_by' in data else None,
            managed_by=data['managed_by'] if 'managed_by' in data else None,
            administered_by=(
                data['administered_by'] if 'administered_by' in data else None
            )
        )

    def encode(self) -> Any:
        return {
            'owned_by': self._owned_by,
            'readable_by': self._readable_by,
            'writable_by': self._writable_by,
            'managed_by': self._managed_by,
            'administered_by': self._administered_by
        }

    def records_read_permissions_for(self, agent: Agent) -> bool:
        """Return True of read permissions are recorded for an Agent"""
        return (
            self.records_ownership_by(agent)
            or self.records_management_rights_for(agent)
            or self.records_administration_rights_for(agent)
            or agent.agent_id in self._readable_by
        )

    def records_write_permissions_for(self, agent: Agent) -> bool:
        """Return True if write permissions are recorded for an Agent"""
        return (
            self.records_ownership_by(agent)
            or self.records_management_rights_for(agent)
            or self.records_administration_rights_for(agent)
            or agent.agent_id in self._writable_by
        )

    def records_management_rights_for(self, agent: Agent) -> bool:
        """Return True if management permissions are recorded for an Agent"""
        return (
            self.records_ownership_by(agent)
            or self.records_administration_rights_for(agent)
            or agent.agent_id in self._managed_by
        )

    def records_ownership_by(self, agent: Agent) -> bool:
        """Return True if ownership is recorded for an Agent"""
        return agent.agent_id == self._owned_by

    def records_administration_rights_for(self, agent: Agent) -> bool:
        """Return True if administrative rights are recorded for an Agent"""
        return (
            agent.agent_id in self._administered_by
            or agent == MACHINE_AGENT
        )
