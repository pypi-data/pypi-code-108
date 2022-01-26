from typing import List

from pymint.constraints.constraint import LayoutConstraint
from pymint.mintcomponent import MINTComponent


class ArrayConstraint(LayoutConstraint):
    """Array Constraint represents a 1D / 2D array with fixed spacings
    in both dimensions
    """

    def __init__(
        self,
        components: List[MINTComponent],
        xdim: int = 1,
        ydim: int = 1,
        horizontal_spacing: float = None,
        vertical_spacing: float = None,
    ) -> None:
        """Creates an instance of the array Constraints

        Args:
            components (List[MINTComponent]): List of components that need be covered
            by the constraint
            xdim (int, optional): X dimension of the array. Defaults to 1.
            ydim (int, optional): Y dimension of the array. Defaults to 1.
            horizontal_spacing (float, optional): horizontal spacing between the
            components (x-dimension). Defaults to None.
            vertical_spacing (float, optional): vertical spacing between the components
            (y-dimension). Defaults to None.
        """
        super().__init__()
        self._components.extend(components)
        self.__is1D = False
        self._horizontal_spacing = horizontal_spacing
        self._vertical_spacing = vertical_spacing

        if xdim is None:
            self.__xdim = len(self._components)
        else:
            self.__xdim = xdim

        if ydim is None:
            self.__is1D = True
            self.__ydim = 1
        else:
            self.__ydim = ydim

    @property
    def is1D(self) -> bool:
        """Returns true if 1D (BANK)

        Returns:
            bool: true if BANK
        """
        return self.__is1D

    @property
    def xdim(self) -> int:
        """Returns the x size of the array

        Returns:
            int: size
        """
        return self.__xdim

    @property
    def ydim(self) -> int:
        """Returns the y size of the array

        Returns:
            int: size
        """
        return self.__ydim

    @property
    def dim(self) -> int:
        """Returns the size of the array

        Returns:
            int: size
        """
        return self.__xdim
