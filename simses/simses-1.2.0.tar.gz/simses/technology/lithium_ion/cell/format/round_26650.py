from simses.technology.lithium_ion.cell.format.round import RoundCell


class RoundCell26650(RoundCell):

    __DIAMETER: float = 26  # mm
    __LENGTH: float = 65  # mm

    def __init__(self):
        super(RoundCell26650, self).__init__(diameter=self.__DIAMETER, length=self.__LENGTH)
