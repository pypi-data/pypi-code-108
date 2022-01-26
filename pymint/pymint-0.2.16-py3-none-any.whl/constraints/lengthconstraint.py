from typing import List

from pymint.constraints.constraint import LayoutConstraint
from pymint.mintconnection import MINTConnection


class LengthConstraint(LayoutConstraint):
    """Layout Constriant that will be used for specifying a fixed length
    for a connection

    """

    def __init__(self, connection: MINTConnection, length: float) -> None:
        """Creates a length constraint

        Args:
            component (MINTComponent): component covered by the constraint
            length (float): length of the connection that needs to be fixed
        """
        super().__init__()
        self._connections = []
        self._connections.append(connection)
        self.__length = length

    @property
    def connections(self) -> List[MINTConnection]:
        """Returns the component covered by the constraint

        Returns:
            MINTComponent: constrained component
        """
        return self._connections

    @property
    def length(self) -> float:
        """Returns the length fixed by the constraint

        Returns:
            float: length constrained
        """
        return self.__length
