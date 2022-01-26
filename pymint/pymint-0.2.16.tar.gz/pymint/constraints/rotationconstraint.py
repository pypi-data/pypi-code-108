from pymint import MINTComponent
from pymint.constraints.constraint import LayoutConstraint


class RotationConstraint(LayoutConstraint):
    """Layout constraint that fixed the absolute rotation
    of the component

    """

    def __init__(self, component: MINTComponent, rotation: float) -> None:
        """Creates a Rotation constraint

        Args:
            component (MINTComponent): Component to be covered by the constraint
            rotation (float): rotation fixed by the constraint
        """
        super().__init__()
        self._components.append(component)
        self.__rotation = rotation

    @property
    def component(self) -> MINTComponent:
        """Returns the component covered by the constraint

        Returns:
            MINTComponent: constrianed component
        """
        return self._components[0]

    @property
    def rotation(self) -> float:
        """Returns the rotation fixed by the rotation

        Returns:
            float: rotation value
        """
        return self.__rotation
