from simses.system.dc_coupling.dc_coupler import DcCoupling
from simses.system.dc_coupling.generation.pv_dc_generation import PvDcGeneration
from simses.system.dc_coupling.load.dc_bus_charging_random import DcBusChargingRandom


class BusChargingDcCoupling(DcCoupling):

    def __init__(self, charging_power: float, generation_power: float):
        super().__init__(DcBusChargingRandom(charging_power), PvDcGeneration(generation_power))
