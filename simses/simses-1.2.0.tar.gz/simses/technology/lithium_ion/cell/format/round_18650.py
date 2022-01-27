from simses.technology.lithium_ion.cell.format.round import RoundCell


class RoundCell18650(RoundCell):

    __DIAMETER: float = 18  # mm
    __LENGTH: float = 65  # mm

    def __init__(self):
        super(RoundCell18650, self).__init__(diameter=self.__DIAMETER, length=self.__LENGTH)
