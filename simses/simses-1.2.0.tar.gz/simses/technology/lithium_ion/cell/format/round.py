import math

from simses.technology.lithium_ion.cell.format.abstract import CellFormat


class RoundCell(CellFormat):
    
    def __init__(self, diameter: float, length: float):
        super(RoundCell, self).__init__()
        self.__volume = math.pi * diameter ** 2.0 * length / 4.0 * 10 ** (-9)  # m3
        self.__surface_area = (2 * math.pi * diameter / 2.0 * length + 2 * math.pi * (diameter / 2.0) ** 2.0) * 10 ** (-6)  # m2

    def get_volume(self) -> float:
        return self.__volume

    def get_surface_area(self) -> float:
        return self.__surface_area
