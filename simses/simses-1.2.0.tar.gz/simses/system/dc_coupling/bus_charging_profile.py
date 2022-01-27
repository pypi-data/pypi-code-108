from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.system.dc_coupling.dc_coupler import DcCoupling
from simses.system.dc_coupling.generation.no_dc_generation import NoDcGeneration
from simses.system.dc_coupling.load.dc_bus_charging_profile import DcBusChargingProfile


class BusChargingProfileDcCoupling(DcCoupling):

    def __init__(self, config: GeneralSimulationConfig, capacity: float, file_name: str):
        super().__init__(DcBusChargingProfile(config, capacity, file_name), NoDcGeneration())
