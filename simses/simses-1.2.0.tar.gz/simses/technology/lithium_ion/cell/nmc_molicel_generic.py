from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.technology.lithium_ion.cell.nmc_molicel import MolicelNMC


class MolicelNMCGeneric(MolicelNMC):

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super(MolicelNMCGeneric, self).__init__(voltage, capacity, soh, battery_config, battery_data_config)
