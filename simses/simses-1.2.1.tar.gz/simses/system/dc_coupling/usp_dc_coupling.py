from simses.system.dc_coupling.dc_coupler import DcCoupling
from simses.system.dc_coupling.generation.pv_dc_generation import PvDcGeneration
from simses.system.dc_coupling.load.dc_radio_ups_load import DCRadioUPSLoad


class USPDCCoupling(DcCoupling):

    def __init__(self, charging_power: float, generation_power: float):
        super().__init__(DCRadioUPSLoad(charging_power), PvDcGeneration(generation_power))


# if RadioUPSLoad is a profile this will be important

'''
class UPSDCCoupling(DcCoupling):

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig, file_name: str):
        super(UPSDCCoupling, self).__init__(RadioUPSLoad(config, profile_config, file_name), NoDcGeneration())
'''