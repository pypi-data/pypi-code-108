from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties


class DefaultThermalCellProperties(ThermalCellProperties):

    __MIN_TEMPERATURE: float = 273.15  # K
    __MAX_TEMPERATURE: float = 333.15  # K
    __MASS: float = 0.05  # kg per cell
    __SPECIFIC_HEAT: float = 700  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K

    def __init__(self):
        super(DefaultThermalCellProperties, self).__init__(self.__MIN_TEMPERATURE, self.__MAX_TEMPERATURE, self.__MASS,
                                                           self.__SPECIFIC_HEAT, self.__CONVECTION_COEFFICIENT)
