# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from typing import Optional, Union, Mapping, Tuple, Sequence
from enum import Enum

from sympathy.platform.parameter_helper import ParameterRoot
from sympathy.utils.parameters import update_parameters

from packaging.version import Version


PortId = Tuple[Optional[str], int]


epoch_version = Version('0.0')
updated_version = Version('3.0.0')


class MigrationNotAvailableError(Exception):
    pass


class MigrationStatus(Enum):
    Perfect = 0
    Imperfect = 1
    NotAvailable = 2

    def is_available(self):
        return self != MigrationStatus.NotAvailable

    def __str__(self):
        return self.name


# Re-export status values for easier imports in migrations
Perfect = MigrationStatus.Perfect
Imperfect = MigrationStatus.Imperfect
NotAvailable = MigrationStatus.NotAvailable


class Migration:
    """
    Class representing a migration which updates ports and parameters.

    For migrations that replace the node with a new one, see NodeMigration.
    """
    def __init__(self, migration_ctx):
        self.__migration_ctx = migration_ctx

    def get_parameters(self):
        """Return a copy of the node's old parameters."""
        return self.__migration_ctx.get_parameters()

    def forward_status(
            self
    ) -> Union[MigrationStatus, Tuple[MigrationStatus, str]]:
        """
        Reimplement this to return the status of the migration.

        The status should be one of the values of MigrationStatus.

        It is ok to return different things depending on the current
        parameters, ports and connections.
        """
        raise NotImplementedError()

    def forward_parameters(
            self,
            old_parameters: ParameterRoot,
    ) -> ParameterRoot:
        """
        Override this method to return the node's new parameters.

        Note:: This node should return a new ParameterRoot for the target node.
               Any changes to old_parameters are ignored.
        """
        return old_parameters


class NodeMigration(Migration):
    def forward_node(self) -> Mapping:
        """
        Override this method to replace the old node with a new one or with
        a subflow.

        Return the definition for the new node. It is ok to return different
        nodes depending on the current parameters, ports and connections.

        Note:: This node should only return a definition of the target node at
               target version. The parameters should be migrated by the
               forward_parameters method instead.
        """
        raise NotImplementedError()

    def forward_ports(
            self,
            input_port_ids: Sequence[PortId],
            output_port_ids: Sequence[PortId],
    ) -> Tuple[Sequence[PortId], Sequence[PortId]]:
        """
        Override to map port ids on the old node to port ids on the new node.

        Connections to/from the old node will automatically be replace with
        connections to the new node according to this mapping.

        Each port id is a tuple with a name (or None if port has no name) and
        an index within the group of ports the same name.
        """
        raise NotImplementedError()


class UpdateParametersMigration(Migration):
    """
    Convenience class for migrating a node which relies on update_parameters
    into the migration system.
    """

    from_version = epoch_version
    to_version = updated_version

    def forward_status(self):
        return MigrationStatus.Perfect

    def forward_parameters(self, old_parameters):
        # Custom parameter updates
        self.update_parameters(old_parameters)

        # And then the old default parameter updates based on the node
        # definition.
        definition_params = self.updated_definition()
        update_parameters(old_parameters, definition_params)
        return old_parameters

    def updated_definition(self):
        """Override to return the current parameter definition of the node."""
        raise NotImplementedError()

    def update_parameters(self, old_params):
        """Override with the custom update_parameters behavior of the node."""
        pass
