from datetime import datetime
from simses.commons.config.generation.generator import ConfigGenerator
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.simulation_config import SimulationConfig
from simses.commons.config.simulation.system import StorageSystemConfig


class SimulationConfigGenerator(ConfigGenerator):

    """
    The SimulationConfigGenerator is a convenience class for generating a config for a SimSES simulation. Prior knowledge
    of the options and structure of SimSES is recommended. Before using SimSES within another application it is very
    helpful to get to know the concepts of SimSES by using it as a standalone tool.

    This config generator allows the user to focus only on the options to generate as well as the systems to instantiate
    without needing to worry about the config structure and naming. However, names of possible classes to instantiate
    are necessary. Basic implementations like "No"-implementations are provided as convenience methods, other types
    need to be named directly.

    First, you generate options for different kind of components like housing, hvac, acdc / dcdc converter, etc.. For
    all of these methods you get a return key for this kind of component. This key is needed for the instantiation methods.
    Second, you define the AC and DC systems with the keys defined and some other values like max. AC power, capacity and
    intermediate circuit voltage.

    You are able to load configs (defaults, local, or your own config file). Please consider that maybe AC and DC systems
    are already defined which will be instantiated. You can clear these options with the provided clear functions.
    """

    __AC_SYSTEM: str = 'ac_system'
    __HVAC: str = 'hvac'
    __HOUSING: str = 'housing'
    __DCDC_CONVERTER: str = 'dcdc'
    __ACDC_CONVERTER: str = 'acdc'
    __TECHNOLOGY: str = 'technology'

    def __init__(self):
        super(SimulationConfigGenerator, self).__init__()

    def load_default_config(self) -> None:
        """
        Loads defaults config

        Returns
        -------

        """
        path: str = SimulationConfig.CONFIG_PATH
        path += SimulationConfig.CONFIG_NAME
        path += SimulationConfig.DEFAULTS
        self.load_config_from(path)

    def load_local_config(self) -> None:
        """
        Loads local config

        Returns
        -------

        """
        path: str = SimulationConfig.CONFIG_PATH
        path += SimulationConfig.CONFIG_NAME
        path += SimulationConfig.LOCAL
        self.load_config_from(path)

    def __check_time_format(self, time: str) -> None:
        if time is None:
            return
        try:
            datetime.strptime(time, GeneralSimulationConfig.TIME_FORMAT)
        except ValueError:
            raise ValueError('Incorrect time format. Expected time format: ' + GeneralSimulationConfig.TIME_FORMAT)

    def get_time_format(self) -> str:
        """

        Returns
        -------
        str:
            expected time format for simulation start and end
        """
        return GeneralSimulationConfig.TIME_FORMAT

    def set_simulation_time(self, start: str = None, end: str = None, time_step: float = 60.0, loop: int = 1) -> None:
        """
        Setting simulation time parameters

        Parameters
        ----------
        start :
            simulation start in expected format
        end :
            simulation start in expected format
        time_step :
            simulation time step in seconds
        loop :
            looping the given simulation time period

        Returns
        -------

        """
        self.__check_time_format(start)
        self.__check_time_format(end)
        self._set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.START, start)
        self._set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.END, end)
        self._set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.TIME_STEP, str(time_step))
        self._set(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.LOOP, str(loop))

    def set_linear_config(self, option: str = None, z_value: str = None) -> None:
        """
        Setting simulation time parameters

        Parameters
        ----------
        option :
            examples for current implementations: linear_optimization_efficiency_costs,
             linear_optimization_calendaric_aging, linear_optimization_and_calendaric_aging
        z_value :
            Z-Value determines the maximum distance between the highest and lowest charged battery storage
            0.25 recommendet. Possible values [0 - 1].

        Returns
        -------

        """
        self._set(StorageSystemConfig.SECTION, StorageSystemConfig.LINEAR_OPTION, option)
        self._set(StorageSystemConfig.SECTION, StorageSystemConfig.LINEAR_DISTRIBUTION_Z_VALUE, z_value)

    def no_data_export(self) -> None:
        """
        No simulation results will be written to files

        Returns
        -------

        """
        self._set_bool(GeneralSimulationConfig.SECTION, GeneralSimulationConfig.EXPORT_DATA, False)

    def set_operation_strategy(self, strategy: str, min_soc: float = 0.0, max_soc: float = 1.0) -> None:
        """
        Setting the operation strategy

        Parameters
        ----------
        strategy :
            examples for current implementations: PowerFollower, SocFollower, ResidentialPvGreedy, ResidentialPvFeedInDamp, etc.
        min_soc :
            minimum allowed soc of storage technologies considered by the operation strategy
        max_soc :
            maximum allowed soc of storage technologies considered by the operation strategy

        Returns
        -------

        """
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.STRATEGY, strategy)
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.MIN_SOC, str(min_soc))
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.MAX_SOC, str(max_soc))

    def set_fcr_operation_strategy(self, fcr_power: float, idm_power: float, fcr_reserve: float = 0.25,
                                   soc_set: float = 0.52) -> None:
        """
        Setting Frequency Containment Reserve (FCR) including a Intraday Recharge Strategy (IDM) as the operation strategy

        Parameters
        ----------
        fcr_power :
            power to reserve for FCR
        idm_power :
            power to participate in IDM
        fcr_reserve :
            defining the lower and upper bounds for the energy capacity as an equivalent for time with full power in h
        soc_set :
            target value of the SOC considering system losses

        Returns
        -------

        """
        self.set_operation_strategy('FcrIdmRechargeStacked')
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.POWER_FCR, str(fcr_power))
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.POWER_IDM, str(idm_power))
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.FCR_RESERVE, str(fcr_reserve))
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.SOC_SET, str(soc_set))

    def set_peak_shaving_strategy(self, strategy: str, max_power: float):
        """
        Setting peak shaving as the operation strategy

        Parameters
        ----------
        strategy :
            examples for current implementations: SimplePeakShaving, PeakShavingPerfectForesight, etc.
        max_power :
            maximum allowed profile power, operations strategy tries to reduce peak power to this value

        Returns
        -------

        """
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.STRATEGY, strategy)
        self._set(EnergyManagementConfig.SECTION, EnergyManagementConfig.MAX_POWER, str(max_power))

    def add_storage_system_ac(self, ac_power: float, intermediate_circuit_voltage: float,
                              acdc_converter: str, housing: str, hvac: str) -> str:
        """
        Adding an AC storage system to the config with the given parameters. All configured system will be instantiated.

        Parameters
        ----------
        ac_power :
            maximum AC power of storage system in W
        intermediate_circuit_voltage :
            voltage of the intermediate circuit in V
        acdc_converter :
            key from generated options for ACDC converter
        housing :
            key from generated options for housing
        hvac :
            key from generated options for hvac

        Returns
        -------
        str:
            key for AC storage system
        """
        key: str = self._get_id_from(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_SYSTEM_AC)
        name: str = self.__AC_SYSTEM + key
        value: str = name + ','
        value += str(ac_power) + ','
        value += str(intermediate_circuit_voltage) + ','
        value += acdc_converter + ','
        value += housing + ','
        value += hvac
        self._add(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_SYSTEM_AC, value)
        return name

    def clear_storage_system_ac(self) -> None:
        """
        Deleting all configured AC storage systems

        Returns
        -------

        """
        self._clear(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_SYSTEM_AC)

    def add_storage_system_dc(self, ac_system_name: str, dcdc_converter: str, storage_name: str) -> None:
        """
        Adding an DC storage system to the config with the given parameters. Every DC systems needs to be connected to
        an AC storage system (via the given key). All configured system will be instantiated.

        Parameters
        ----------
        ac_system_name :
            key from generated options for AC storage systems
        dcdc_converter :
            key from generated options for DCDC converter
        storage_name :
            key from generated options for storage technologies

        Returns
        -------

        """
        value: str = ac_system_name + ','
        value += dcdc_converter + ','
        value += storage_name
        self._add(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_SYSTEM_DC, value)

    def clear_storage_system_dc(self) -> None:
        """
        Deleting all configured DC storage systems

        Returns
        -------

        """
        self._clear(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_SYSTEM_DC)

    def __add_storage_technology(self, capacity: float, storage_type: str, storage_characteristics: str) -> str:
        key: str = self._get_id_from(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_TECHNOLOGY)
        name: str = self.__TECHNOLOGY + key
        value: str = name + ','
        value += str(capacity) + ','
        value += storage_type + ','
        value += storage_characteristics
        self._add(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_TECHNOLOGY, value)
        return name

    def add_lithium_ion_battery(self, capacity: float, cell_type: str, start_soc: float = 0.5,
                                start_soh: float = 1.0) -> str:
        """
        Adding a lithium-ion battery to storage technology options with given parameters.

        Parameters
        ----------
        capacity :
            capacity of battery in Wh
        cell_type :
            examples for possible cell types: GenericCell, SonyLFP, PanasonicNCA, MolicelNMC, SanyoNMC
        start_soc :
            state of charge at start of simulation in p.u.
        start_soh :
            state of health at start of simulation in p.u. (Note: not all cell types are supported)

        Returns
        -------
        str:
            key for storage technology
        """
        value: str = cell_type + ','
        value += str(start_soc) + ','
        value += str(start_soh)
        return self.__add_storage_technology(capacity, 'lithium_ion', value)

    def add_generic_cell(self, capacity: float) -> str:
        """
        Convenience method for constructing a lithium-ion battery with a GenericCell

        Parameters
        ----------
        capacity :
            capacity of battery in Wh

        Returns
        -------
        str:
            key for storage technology
        """
        return self.add_lithium_ion_battery(capacity, 'GenericCell')

    def add_redox_flow_battery(self, capacity: float, stack_type: str, stack_power: float,
                               pump_algorithm: str = 'StoichFlowRate') -> str:
        """
        Adding a redox flow battery to storage technology options with given parameters.

        Parameters
        ----------
        capacity :
            capacity of battery in Wh
        stack_type :
            examples for possible stack types: CellDataStack5500W, DummyStack3000W, IndustrialStack1500W, etc.
        stack_power :
            maximum power of stack in W
        pump_algorithm :
            control algorithm for selected pump, default: StoichFlowRate

        Returns
        -------
        str:
            key for storage technology
        """
        value: str = stack_type + ','
        value += str(stack_power) + ','
        value += pump_algorithm
        return self.__add_storage_technology(capacity, 'redox_flow', value)

    def add_hydrogen_technology(self, capacity: float, fuel_cell: str, fuel_cell_power: float, electrolyzer: str,
                                electrolyzer_power: float, storage_type: str, pressure: float) -> str:
        """
        Adding a hydrogen energy chain to storage technology options with given parameters.

        Parameters
        ----------
        capacity :
            capacity of battery in Wh
        fuel_cell :
            examples for possible fuel cells: PemFuelCell, JupiterFuelCell
        fuel_cell_power :
            maximum power for fuel cell in W
        electrolyzer :
            examples for possible electrolyzers: PemElectrolyzer, AlkalineElectrolyzer, etc.
        electrolyzer_power :
            maximum power for electrolyzer in W
        storage_type :
            examples for possible storage types: PressureTank, SimplePipeline
        pressure :
            pressure for storage type in bar

        Returns
        -------
        str:
            key for storage technology
        """
        value: str = fuel_cell + ','
        value += str(fuel_cell_power) + ','
        value += electrolyzer + ','
        value += str(electrolyzer_power) + ','
        value += storage_type + ','
        value += str(pressure)
        return self.__add_storage_technology(capacity, 'hydrogen', value)

    def clear_storage_technology(self) -> None:
        """
        Deleting all configured storage technology options

        Returns
        -------

        """
        self._clear(StorageSystemConfig.SECTION, StorageSystemConfig.STORAGE_TECHNOLOGY)

    def add_dcdc_converter(self, converter_type: str, max_power: float, efficiency: float = None) -> str:
        """
        Adding a dcdc converter option to config

        Parameters
        ----------
        efficiency :
            efficiency of converter in p.u., only used for FixEfficiencyDcDcConverter
        converter_type :
            examples for DCDC converters: NoLossDcDcConverter, FixEfficiencyDcDcConverter, etc.
        max_power :
            maximum power of DCDC converter in W

        Returns
        -------
        str:
            key for dcdc converter
        """
        key: str = self._get_id_from(StorageSystemConfig.SECTION, StorageSystemConfig.DCDC_CONVERTER)
        name: str = self.__DCDC_CONVERTER + key
        value: str = name + ','
        value += converter_type + ','
        value += str(max_power)
        if efficiency:
            value += ',' + str(efficiency)
        self._add(StorageSystemConfig.SECTION, StorageSystemConfig.DCDC_CONVERTER, value)
        return name

    def add_no_loss_dcdc(self) -> str:
        """
        Convenience method to add a config option of a no loss converter

        Returns
        -------
        str:
            key for dcdc converter

        """
        return self.add_dcdc_converter('NoLossDcDcConverter', 0.0, 1.0)

    def add_fix_efficiency_dcdc(self, efficiency: float = 0.98) -> str:
        """
        Convenience method to add a config option of a fix efficiency converter

        Parameters
        ----------
        efficiency :
            efficiency of dcdc converter in p.u.

        Returns
        -------
        str:
            key for dcdc converter

        """
        return self.add_dcdc_converter('FixEfficiencyDcDcConverter', 0.0, efficiency)

    def clear_dcdc_converter(self) -> None:
        """
        Deleting all config options for DCDC converter

        Returns
        -------

        """
        self._clear(StorageSystemConfig.SECTION, StorageSystemConfig.DCDC_CONVERTER)

    def add_acdc_converter(self, converter_type: str, number_of_converters: int = 1, switch_value: float = 1.0) -> str:
        """
        Adding an acdc converter option to config

        Parameters
        ----------
        converter_type :
            examples for ACDC converters: NoLossAcDcConverter, FixEfficiencyAcDcConverter, BonfiglioliAcDcConverter, etc.
        number_of_converters :
            possibility to cascade converters with the given number, default: 1
        switch_value :
            if converters are cascaded, the switch value in p.u. defines the point of the power to nominal power ratio
            when the next converter will be activated, default: 1.0

        Returns
        -------
        str:
            key for acdc converter
        """
        key: str = self._get_id_from(StorageSystemConfig.SECTION, StorageSystemConfig.ACDC_CONVERTER)
        name: str = self.__ACDC_CONVERTER + key
        value: str = name + ','
        value += converter_type + ','
        value += str(number_of_converters) + ','
        value += str(switch_value)
        self._add(StorageSystemConfig.SECTION, StorageSystemConfig.ACDC_CONVERTER, value)
        return name

    def add_no_loss_acdc(self) -> str:
        """
        Convenience method to add a config option of a no loss converter

        Returns
        -------
        str:
            key for acdc converter
        """
        return self.add_acdc_converter('NoLossAcDcConverter')

    def add_fix_efficiency_acdc(self) -> str:
        """
        Convenience method to add a config option of a fix efficiency converter

        Returns
        -------
        str:
            key for acdc converter
        """
        return self.add_acdc_converter('FixEfficiencyAcDcConverter')

    def clear_acdc_converter(self) -> None:
        """
        Deleting all config options for ACDC converter

        Returns
        -------

        """
        self._clear(StorageSystemConfig.SECTION, StorageSystemConfig.ACDC_CONVERTER)

    def add_housing(self, housing_type: str, high_cube: bool = False, azimuth: float = 0.0,
                    absorptivity: float = 0.15, ground_albedo: float = 0.2) -> str:
        """
        Adding an housing option to config

        Parameters
        ----------
        housing_type :
            examples for housing: NoHousing, TwentyFtContainer, etc.
        high_cube :
            high cube container are taller than usual containers, default: False
        azimuth :
            azimuth angle
        absorptivity :
            absorptivity of container
        ground_albedo :
            reflection value of ground

        Returns
        -------
        str:
            key for housing
        """
        key: str = self._get_id_from(StorageSystemConfig.SECTION, StorageSystemConfig.HOUSING)
        name: str = self.__HOUSING + key
        value: str = name + ','
        value += housing_type + ','
        value += str(high_cube) + ','
        value += str(azimuth) + ','
        value += str(absorptivity) + ','
        value += str(ground_albedo)
        self._add(StorageSystemConfig.SECTION, StorageSystemConfig.HOUSING, value)
        return name

    def add_no_housing(self) -> str:
        """
        Convenience method to add a config option of a no housing

        Returns
        -------
        str:
            key for housing
        """
        return self.add_housing('NoHousing')

    def add_twenty_foot_container(self) -> str:
        """
        Convenience method to add a config option of a twenty foot container

        Returns
        -------
        str:
            key for housing
        """
        return self.add_housing('TwentyFtContainer')

    def clear_housing(self) -> None:
        """
        Deleting all config options for housing

        Returns
        -------

        """
        self._clear(StorageSystemConfig.SECTION, StorageSystemConfig.HOUSING)

    def add_hvac(self, hvac_type: str, power: float, temperature: float = 25.0) -> str:
        """
        Adding an HVAC option to config

        Parameters
        ----------
        hvac_type :
            examples for HVAC: NoHeatingVentilationAirConditioning, FixCOPHeatingVentilationAirConditioning, etc.
        power :
            maximum electrical heating/cooling power in W
        temperature :
            set point temperature in centigrade, default: 25.0

        Returns
        -------
        str:
            key for hvac system
        """
        key: str = self._get_id_from(StorageSystemConfig.SECTION, StorageSystemConfig.HVAC)
        name: str = self.__HVAC + key
        value: str = name + ','
        value += hvac_type + ','
        value += str(power) + ','
        value += str(temperature)
        self._add(StorageSystemConfig.SECTION, StorageSystemConfig.HVAC, value)
        return name

    def add_no_hvac(self) -> str:
        """
        Convenience method to add a config option of a no HVAC system

        Returns
        -------
        str:
            key for hvac system
        """
        return self.add_hvac('NoHeatingVentilationAirConditioning', 0.0)

    def add_constant_hvac(self, power: float, temperature: float) -> str:
        """
        Convenience method to add a config option of a constant HVAC system

        Parameters
        ----------
        power :
            maximum electrical heating/cooling power in W
        temperature :
            set point temperature in centigrade

        Returns
        -------
        str:
            key for hvac system
        """
        return self.add_hvac('FixCOPHeatingVentilationAirConditioning', power, temperature)

    def clear_hvac(self) -> None:
        """
        Deleting all config options for HVAC systems

        Returns
        -------

        """
        self._clear(StorageSystemConfig.SECTION, StorageSystemConfig.HVAC)

    def set_power_distribution_strategy_ac(self, strategy: str) -> None:
        """
        Defines the power distribution strategy for AC storage systems

        Parameters
        ----------
        strategy :
            examples: EqualPowerDistributor, SocBasedPowerDistributor, etc.

        Returns
        -------

        """
        self._set(StorageSystemConfig.SECTION, StorageSystemConfig.POWER_DISTRIBUTOR_AC, strategy)

    def set_power_distribution_strategy_dc(self, strategy: str) -> None:
        """
        Defines the power distribution strategy for DC storage systems

        Parameters
        ----------
        strategy :
            examples: EqualPowerDistributor, SocBasedPowerDistributor, etc.

        Returns
        -------

        """
        self._set(StorageSystemConfig.SECTION, StorageSystemConfig.POWER_DISTRIBUTOR_DC, strategy)

    def set_battery(self, start_soc: str = None, min_soc: str = None, max_soc: str = None,
                    eol: str = None, start_soh: str = None, exact_size: str = 'False') -> None:
        """
        Sets parameters for the battery section of the simulation.ini file
        :param start_soc: SOC at start of simulation
        :param min_soc: minimum permissible SOC
        :param max_soc: maximum permissible SOC
        :param eol: value of SOH at End-of-Life
        :param start_soh: SOH at start of simulation
        :param exact_size: Enable or disable rounding of number of cells in parallel/series to reach integer values
        :return:
        """
        self._set(BatteryConfig.SECTION, BatteryConfig.START_SOC, start_soc)
        self._set(BatteryConfig.SECTION, BatteryConfig.MIN_SOC, min_soc)
        self._set(BatteryConfig.SECTION, BatteryConfig.MAX_SOC, max_soc)
        self._set(BatteryConfig.SECTION, BatteryConfig.EOL, eol)
        self._set(BatteryConfig.SECTION, BatteryConfig.START_SOH, start_soh)
        self._set(BatteryConfig.SECTION, BatteryConfig.EXACT_SIZE, exact_size)

    def set_ambient_temperature_model(self, model: str, constant_temperature: float = None) -> None:
        """
        Set the type of ambient temperature model to be used
        :param constant_temperature: optional parameter for ConstantAmbientTemperature
        :param model: name of the ambient temperature model
        :return:
        """
        value = model
        if constant_temperature:
            value += ',' + str(constant_temperature)
        self._set(StorageSystemConfig.SECTION, StorageSystemConfig.AMBIENT_TEMPERATURE_MODEL, value)

    def set_ambient_temperature_profile_file(self, filename: str) -> None:
        """
        Set the filename for the location ambient temperature profile
        :param filename: name of specified file as str
        :return: None
        """
        self._set(ProfileConfig.SECTION, ProfileConfig.AMBIENT_TEMPERATURE_PROFILE, filename)

    def set_ghi_profile_file(self, filename: str) -> None:
        """
        Set the filename for the location Global Horizontal Irradiance profile
        :param filename: name of specified file as str
        :return: None
        """
        self._set(ProfileConfig.SECTION, ProfileConfig.GLOBAL_HORIZONTAL_IRRADIATION_PROFILE, filename)

    def set_solar_irradiation_model(self, model: str) -> None:
        """
        Set the type of solar irradiation model
        :param model: name of the ambient temperature model
        :return: None
        """
        self._set(StorageSystemConfig.SECTION, StorageSystemConfig.SOLAR_IRRADIATION_MODEL, model)

    def set_enable_thermal_simulation(self, value: str) -> None:
        """
        Enable/disable thermal simulation
        :param value: True/False as str
        :return: None
        """
        self._set(StorageSystemConfig.SECTION, StorageSystemConfig.THERMAL_SIMULATION, value)

    def set_load_scaling_factor(self, load_scaling_factor: str) -> None:
        """
        Sets the load scaling factor for the area under the load profile (energy)
        Parameters
        ----------
        load_scaling_factor : desired load scaling factor as str
            examples: 5e6, 5e7, etc.

        Returns
        -------

        """
        self._set(ProfileConfig.SECTION, ProfileConfig.LOAD_SCALING_FACTOR, load_scaling_factor)

    def set_load_generation_scaling_factor(self, load_generation_scaling_factor: str) -> None:
        """
        Sets the generation load scaling factor for the area under the load profile (energy)
        Parameters
        ----------
        load_generation_scaling_factor : desired load scaling factor as str
            examples: 5e6, 5e7, etc.

        Returns
        -------

        """
        self._set(ProfileConfig.SECTION, ProfileConfig.GENERATION_SCALING_FACTOR, load_generation_scaling_factor)

    def set_profile_config(self, load_profile: str = None) -> None:
        """
        Set the filename for the load profile
        :param load_profile: name of specified file as str
        :return: None
        """
        self._set(ProfileConfig.SECTION, ProfileConfig.LOAD_PROFILE, load_profile)

    def set_generation_profile_config(self, generation_profile: str = None) -> None:
        """
        Set the filename for the generation profile
        :param generation_profile: name of specified file as str
        :return: None
        """
        self._set(ProfileConfig.SECTION, ProfileConfig.GENERATION_PROFILE, generation_profile)
