from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties


class DefaultElectricalCellProperties(ElectricalCellProperties):

    __CELL_VOLTAGE = 3.5  # V
    __CELL_CAPACITY = 2.5  # Ah
    __MAX_VOLTAGE: float = 4.0  # V
    __MIN_VOLTAGE: float = 3.0  # V
    __MAX_CHARGE_RATE: float = 2.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 2.0  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __COULOMB_EFFICIENCY: float = 1.0  # p.u.

    def __init__(self):
        super(DefaultElectricalCellProperties, self).__init__(self.__CELL_VOLTAGE, self.__CELL_CAPACITY,
                                                              self.__MIN_VOLTAGE, self.__MAX_VOLTAGE,
                                                              self.__MAX_CHARGE_RATE, self.__MAX_DISCHARGE_RATE,
                                                              self.__SELF_DISCHARGE_RATE, self.__COULOMB_EFFICIENCY)
