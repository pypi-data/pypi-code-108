from typing import Optional

from pymint.constraints.constraint import LayoutConstraint
from pymint.mintcomponent import MINTComponent


class PositionConstraint(LayoutConstraint):
    """Layout constraint that fixes the location"""

    def __init__(
        self,
        component: MINTComponent,
        xpos: Optional[int],
        ypos: Optional[int],
        zpos: Optional[int],
    ) -> None:
        """Returns the position constrinant

        Args:
            component (MINTComponent): component covered by the constraint
            xpos (Optional[int]): x position value
            ypos (Optional[int]): y position value
            zpos (Optional[int]): z position value
        """
        super().__init__()
        self.add_component(component)
        self.__xpos = xpos
        self.__ypos = ypos
        self.__zpos = zpos

    def get_component(self) -> MINTComponent:
        """Returns the component constrained by the component

        Raises:
            Exception: if the component is not covered by the constraint

        Returns:
            MINTComponent: returns the component covered by the constraint
        """
        ret = self._components[0]
        if ret is None:
            raise Exception("No component set for PositionConstraint")

        return ret

    @property
    def xpos(self) -> Optional[int]:
        """Returns the x position of the component

        Returns:
            Optional[int]: x coordinate of the component if set else returns None
        """
        return self.__xpos

    @property
    def ypos(self) -> Optional[int]:
        """Returns the y position of the component

        Returns:
            Optional[int]: y coordinate of the component if set else returns None
        """
        return self.__ypos

    @property
    def zpos(self) -> Optional[int]:
        """Returns the z position of the component

        Returns:
            Optional[int]: z coordinate of the component if set else returns None
        """
        return self.__zpos
