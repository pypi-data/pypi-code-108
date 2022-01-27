from configparser import ConfigParser

from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.simulation_config import clean_split
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.config.data.energy_management import EnergyManagementDataConfig
from simses.commons.log import Logger
from simses.commons.profile.power.alternating import AlternatePowerProfile
from simses.commons.profile.power.constant import ConstantPowerProfile
from simses.commons.profile.power.generation import GenerationProfile
from simses.commons.profile.power.load import LoadProfile
from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.profile.technical.binary import BinaryProfile
from simses.commons.profile.power.random import RandomPowerProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.logic.energy_management.strategy.basic.ev_charger_with_buffer import EvChargerWithBuffer
from simses.logic.energy_management.strategy.basic.electric_vehicle import ElectricVehicle
from simses.logic.energy_management.strategy.basic.frequency_containment_reserve import FrequencyContainmentReserve
from simses.logic.energy_management.strategy.basic.intraday_market_recharge import IntradayMarketRecharge
from simses.logic.energy_management.strategy.basic.peak_shaving_perfect_foresight import PeakShavingPerfectForesight
from simses.logic.energy_management.strategy.basic.peak_shaving_simple import SimplePeakShaving
from simses.logic.energy_management.strategy.basic.power_follower import PowerFollower
from simses.logic.energy_management.strategy.basic.residential_pv_feed_in_damp import ResidentialPvFeedInDamp
from simses.logic.energy_management.strategy.basic.residential_pv_greedy import ResidentialPvGreedy
from simses.logic.energy_management.strategy.basic.soc_follower import SocFollower
from simses.logic.energy_management.strategy.basic.electric_vehicle_soc import ElectricVehicleSOC
from simses.logic.energy_management.strategy.basic.use_all_renewable_energy import UseAllRenewableEnergy
from simses.logic.energy_management.strategy.stacked.fcr_idm_recharge_stacked import FcrIdmRechargeStacked


class EnergyManagementFactory:
    """
    Energy Management Factory to create the operation strategy of the ESS.
    """

    def __init__(self, config: ConfigParser, path: str = None):
        self.__log: Logger = Logger(type(self).__name__)
        self.__config_general: GeneralSimulationConfig = GeneralSimulationConfig(config, path)
        self.__config_ems: EnergyManagementConfig = EnergyManagementConfig(config, path)
        self.__config_profile: ProfileConfig = ProfileConfig(config, path)
        self.__config_system: StorageSystemConfig = StorageSystemConfig(config, path)
        self.__config_battery: BatteryConfig = BatteryConfig(config, path)
        self.__config_ems_data: EnergyManagementDataConfig = EnergyManagementDataConfig()

    def create_operation_strategy(self):
        """
        Energy Management Factory to create the operation strategy of the ESS based on the __analysis_config file_name.
        """
        os = self.__config_ems.operation_strategy
        timestep = self.__config_general.timestep

        if os == FrequencyContainmentReserve.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return FrequencyContainmentReserve(self.__config_general, self.__config_ems, self.__config_profile)

        elif os == IntradayMarketRecharge.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return IntradayMarketRecharge(self.__config_general, self.__config_ems)

        elif os == SimplePeakShaving.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return SimplePeakShaving(self.load_profile(), self.__config_ems)

        elif os == PeakShavingPerfectForesight.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return PeakShavingPerfectForesight(self.__config_general, self.load_profile(), self.load_profile(),
                                               self.__config_ems, self.__config_system, self.__config_profile)

        elif os == PowerFollower.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return PowerFollower(self.load_profile())

        elif os == SocFollower.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return SocFollower(self.__config_general, self.__config_profile)

        elif os == FcrIdmRechargeStacked.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return FcrIdmRechargeStacked(self.__config_general, self.__config_ems, self.__config_profile)

        elif os == ResidentialPvGreedy.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return ResidentialPvGreedy(self.load_profile(), self.generation_profile())

        elif os == ResidentialPvFeedInDamp.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return ResidentialPvFeedInDamp(self.load_profile(), self.__config_general, self.generation_profile())

        elif os == UseAllRenewableEnergy.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return UseAllRenewableEnergy(self.generation_profile())

        elif os == EvChargerWithBuffer.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return EvChargerWithBuffer(self.load_profile(), self.__config_ems)

        elif os == ElectricVehicle.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return ElectricVehicle(self.load_profile(), self.binary_profile(), self.__config_ems)

        elif os == ElectricVehicleSOC.__name__:
            self.__log.debug('Creating operation strategy as ' + os)
            return ElectricVehicleSOC(self.__config_general, self.__config_profile, self.__config_ems)

        else:
            options: [str] = list()
            options.append(FrequencyContainmentReserve.__name__)
            options.append(IntradayMarketRecharge.__name__)
            options.append(SimplePeakShaving.__name__)
            options.append(PeakShavingPerfectForesight.__name__)
            options.append(PowerFollower.__name__)
            options.append(SocFollower.__name__)
            options.append(FcrIdmRechargeStacked.__name__)
            options.append(ResidentialPvGreedy.__name__)
            options.append(ResidentialPvFeedInDamp.__name__)
            options.append(FcrIdmPeakShavingSerial.__name__)
            options.append(EvChargerWithBuffer.__name__)
            options.append(ElectricVehicle.__name__)
            options.append(ElectricVehicleSOC.__name__)
            raise Exception('Operation strategy ' + os + ' is unknown. '
                                                         'Following options are available: ' + str(options))

    def generation_profile(self) -> GenerationProfile:
        return GenerationProfile(self.__config_profile, self.__config_general)

    def binary_profile(self) -> BinaryProfile:
        return BinaryProfile(self.__config_general, self.__config_profile)

    def load_profile(self) -> PowerProfile:
        """
        Returns the load profile for the EnergyManagementSystem
        """
        power_profile = self.__config_profile.load_profile
        profile: [str] = clean_split(power_profile, ',')
        try:
            power: float = float(profile[1])
        except IndexError:
            power = None
        if RandomPowerProfile.__name__ in power_profile:
            try:
                power_offset: float = float(profile[2])
            except IndexError:
                power_offset: float = 0.0
            start: float = self.__config_general.start
            return RandomPowerProfile(start, max_power=1500.0 if power is None else power, power_offset=power_offset)
        elif ConstantPowerProfile.__name__ in power_profile:
            return ConstantPowerProfile(power=0.0 if power is None else power, scaling_factor=1)
        elif AlternatePowerProfile.__name__ in power_profile:
            try:
                power_off: float = float(profile[2])
                time_on: float = float(profile[3])
                time_off: float = float(profile[4])
            except IndexError:
                power_off = 0
                time_on = 6
                time_off = 6
            return AlternatePowerProfile(power_on=1500.0 if power is None else power, power_off=power_off,
                                         scaling_factor=-1, time_on=time_on, time_off=time_off)
        else:
            return LoadProfile(self.__config_profile, self.__config_general)

    def create_energy_management_state(self) -> EnergyManagementState:
        state: EnergyManagementState = EnergyManagementState()
        state.time = self.__config_general.start
        return state

    def close(self):
        self.__log.close()
