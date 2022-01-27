from configparser import ConfigParser
import ast
from simses.commons.config.simulation.simulation_config import SimulationConfig, create_dict_from, create_list_from, \
    clean_split


class StorageSystemConfig(SimulationConfig):
    """
    Storage system specific configs
    """

    AC_SYSTEM_NAME: int = 0
    AC_SYSTEM_POWER: int = 1
    AC_SYSTEM_DC_VOLTAGE: int = 2
    AC_SYSTEM_CONVERTER: int = 3
    AC_SYSTEM_HOUSING: int = 4
    AC_SYSTEM_HVAC: int = 5

    DC_SYSTEM_NAME: int = 0
    DC_SYSTEM_CONVERTER: int = 1
    DC_SYSTEM_STORAGE: int = 2

    ACDC_CONVERTER_TYPE: int = 0
    ACDC_CONVERTER_NUMBERS: int = 1
    ACDC_CONVERTER_SWITCH: int = 2
    ACDC_CONVERTER_EFFICIENCY: int = 3

    DCDC_CONVERTER_TYPE: int = 0
    DCDC_CONVERTER_POWER: int = 1
    DCDC_CONVERTER_EFFICIENCY: int = 2

    DC_POWER_DISTRIBUTOR_TYPE: int = 0

    HOUSING_TYPE: int = 0
    HOUSING_HIGH_CUBE: int = 1  # Determines whether container to be created with high cube or standard dimensions
    HOUSING_AZIMUTH: int = 2
    HOUSING_ABSORPTIVITY = 3
    HOUSING_GROUND_ALBEDO = 4

    HVAC_TYPE: int = 0
    HVAC_POWER: int = 1
    HVAC_TEMPERATURE_SETPOINT: int = 2
    HVAC_KP_COEFFICIENT: int = 3
    HVAC_KI_COEFFICIENT: int = 4
    HVAC_KD_COEFFICIENT: int = 5

    AMBIENT_TEMPERATURE_TYPE: int = 0
    AMBIENT_TEMPERATURE_CONSTANT: int = 1

    SOLAR_IRRADIATION_TYPE: int = 0

    STORAGE_CAPACITY: int = 0
    STORAGE_TYPE: int = 1

    BATTERY_CELL: int = 2
    BATTERY_SOC: int = 3
    BATTERY_SOH: int = 4

    REDOX_FLOW_STACK: int = 2
    STACK_MODULE_POWER: int = 3
    REDOX_FLOW_PUMP_ALGORITHM: int = 4

    FUEL_CELL_TYPE: int = 2
    FUEL_CELL_POWER: int = 3
    ELECTROLYZER_TYPE: int = 4
    ELECTROLYZER_POWER: int = 5
    HYDROGEN_STORAGE: int = 6
    HYDROGEN_TANK_PRESSURE: int = 7

    SECTION: str = 'STORAGE_SYSTEM'

    STORAGE_SYSTEM_DC: str = 'STORAGE_SYSTEM_DC'
    STORAGE_SYSTEM_AC: str = 'STORAGE_SYSTEM_AC'
    ACDC_CONVERTER: str = 'ACDC_CONVERTER'
    DCDC_CONVERTER: str = 'DCDC_CONVERTER'
    HVAC: str = 'HVAC'
    HOUSING: str = 'HOUSING'
    STORAGE_TECHNOLOGY: str = 'STORAGE_TECHNOLOGY'
    AMBIENT_TEMPERATURE_MODEL: str = 'AMBIENT_TEMPERATURE_MODEL'
    SOLAR_IRRADIATION_MODEL: str = 'SOLAR_IRRADIATION_MODEL'
    THERMAL_SIMULATION: str = 'THERMAL_SIMULATION'
    CYCLE_DETECTOR: str = 'CYCLE_DETECTOR'
    POWER_DISTRIBUTOR_DC: str = 'POWER_DISTRIBUTOR_DC'
    POWER_DISTRIBUTOR_AC: str = 'POWER_DISTRIBUTOR_AC'
    LINEAR_DISTRIBUTION_Z_VALUE: str = 'LINEAR_DISTRIBUTION_Z_VALUE'
    LINEAR_OPTION: str = 'LINEAR_OPTION'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def storage_systems_dc(self) -> [[str]]:
        """Returns a list of dc storage systems"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.STORAGE_SYSTEM_DC))
        return create_list_from(props)

    @property
    def storage_systems_ac(self) -> [[str]]:
        """Returns a list of ac storage systems"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.STORAGE_SYSTEM_AC))
        return create_list_from(props)

    @property
    def acdc_converter(self) -> dict:
        """Returns a list of acdc converter"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.ACDC_CONVERTER))
        return create_dict_from(props)

    @property
    def dcdc_converter(self) -> dict:
        """Returns a list of acdc converter"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.DCDC_CONVERTER))
        return create_dict_from(props)

    @property
    def hvac(self) -> dict:
        """Returns a list of hvac systems"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.HVAC))
        return create_dict_from(props)

    @property
    def housing(self) -> dict:
        """Returns a list of housing objects"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.HOUSING))
        return create_dict_from(props)

    @property
    def storage_technologies(self) -> dict:
        """Returns a list of storage technologies"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.STORAGE_TECHNOLOGY))
        return create_dict_from(props)

    @property
    def ambient_temperature_model(self) -> list:
        """Returns name of ambient temperature model"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.AMBIENT_TEMPERATURE_MODEL), ',')
        return props

    @property
    def solar_irradiation_model(self) -> list:
        """Returns name of solar irradiation model"""
        props: [str] = clean_split(self.get_property(self.SECTION, self.SOLAR_IRRADIATION_MODEL), ',')
        return props

    @property
    def thermal_simulation(self) -> bool:
        """Returns user preference to enable/disable thermal simulation"""
        props: bool = ast.literal_eval(clean_split(self.get_property(self.SECTION, self.THERMAL_SIMULATION), ',')[0])
        return props

    @property
    def cycle_detector(self) -> str:
        """Returns name of cycle detector"""
        return self.get_property(self.SECTION, self.CYCLE_DETECTOR)

    @property
    def power_distributor_dc(self) -> [str]:
        """Returns name of cycle detector"""
        return clean_split(self.get_property(self.SECTION, self.POWER_DISTRIBUTOR_DC), ',')

    @property
    def power_distributor_ac(self) -> str:
        """Returns name of cycle detector"""
        return self.get_property(self.SECTION, self.POWER_DISTRIBUTOR_AC)

    @property
    def linear_distributor_z_value(self) -> str:
        """Returns name of cycle detector"""
        return self.get_property(self.SECTION, self.LINEAR_DISTRIBUTION_Z_VALUE)

    @property
    def linear_option(self) -> str:
        """Returns name of cycle detector"""
        return self.get_property(self.SECTION, self.LINEAR_OPTION)
