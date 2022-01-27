from abc import ABC, abstractmethod


class CellFormat(ABC):

    """
    CellFormat inherits the dimensions of the cell and provides volume and surface area for each cell.
    """

    def __init__(self):
        self.__name: str = type(self).__name__

    @abstractmethod
    def get_volume(self) -> float:
        """

        Returns
        -------
        float:
            volume of one cell in m3
        """
        pass

    @abstractmethod
    def get_surface_area(self) -> float:
        """

        Returns
        -------
        float:
            surface area of one cell in m2
        """
        pass

    def get_name(self) -> str:
        """

        Returns
        -------
        str:
            name of the cell format
        """
        return self.__name
