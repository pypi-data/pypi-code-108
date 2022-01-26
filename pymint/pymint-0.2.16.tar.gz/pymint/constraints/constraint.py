from enum import Enum
from typing import List

from pymint.mintcomponent import MINTComponent
from pymint.mintconnection import MINTConnection


class OperationType(Enum):
    """Enum that represents all the differnt types of constraints"""

    EXPLICIT_OPERATION = 0
    OPTIONAL_OPERATION = 1
    ALIGNMENT_OPERATION = 2
    SYMMETRY_OPERATION = 4
    RELATIVE_OPERATIONS = 5
    PARAMETER_MATCH = 6


class LayoutConstraint:
    """Base layout constraint class over which all the other constriaint
    classes will be based upon

    """

    def __init__(self) -> None:
        """Creates a new instance of the LayoutConstraint"""
        self._components = []
        self._connections = []
        self._type: OperationType

    def add_component(self, component: MINTComponent):
        """Adds a component to be covered by the layout constraint

        Args:
            component (MINTComponent): Component to be constrained
        """
        self._components.append(component)

    def add_connection(self, connection: MINTConnection):
        """Adds a connection to be covered by the layout constraint

        Args:
            connection (MINTConnection): Connection to be constrained
        """
        self._connections.append(connection)

    def get_components(self) -> List[MINTComponent]:
        """Returns components covered by the constraint

        Returns:
            List[MINTComponent]: Constrained components
        """
        return self._components

    def get_connections(self) -> List[MINTConnection]:
        """Returns the connections covered byt he constraint

        Returns:
            List[MINTConnection]: Constrained connections
        """
        return self._connections

    def contains_component(self, component: MINTComponent) -> bool:
        """Checks if the constraint covers the component

        Args:
            component (MINTComponent): component to check

        Returns:
            bool: true if component is present
        """
        return component in self._components

    def contains_connection(self, connection: MINTConnection) -> bool:
        """Checks if the constraint covers the connection

        Args:
            connection (MINTConnection): connection to check

        Returns:
            bool: true if connection is present
        """
        return connection in self._connections
