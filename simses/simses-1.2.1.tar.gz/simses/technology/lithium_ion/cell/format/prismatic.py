from simses.technology.lithium_ion.cell.format.abstract import CellFormat


class PrismaticCell(CellFormat):

    def __init__(self, height: float, width: float, length: float):
        super(PrismaticCell, self).__init__()
        self.__volume = height * width * length * 10 ** (-9)  # m3
        self.__surface_area = 2.0 * (length * height + length * width + width * height) * 10 ** (-6)  # m2

    def get_volume(self) -> float:
        return self.__volume

    def get_surface_area(self) -> float:
        return self.__surface_area
