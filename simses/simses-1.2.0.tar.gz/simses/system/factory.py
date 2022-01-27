import copy
import os
from configparser import ConfigParser

from simses.commons.config.data.energy_management import EnergyManagementDataConfig
from simses.commons.config.data.power_electronics import PowerElectronicsConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.data.data_handler import DataHandler
from simses.commons.log import Logger
from simses.commons.state.system import SystemState
from simses.logic.power_distribution.efficient import EfficientPowerDistributor
from simses.logic.power_distribution.equal import EqualPowerDistributor
from simses.logic.power_distribution.power_distributor import PowerDistributor
from simses.logic.power_distribution.soc import SocBasedPowerDistributor
from simses.logic.power_distribution.technology import TechnologyBasedPowerDistributor
from simses.system.auxiliary.heating_ventilation_air_conditioning.fix_cop_hvac import \
    FixCOPHeatingVentilationAirConditioning
from simses.system.auxiliary.heating_ventilation_air_conditioning.fix_cop_hvac_pid_control import \
    FixCOPHeatingVentilationAirConditioningPIDControl
from simses.system.auxiliary.heating_ventilation_air_conditioning.hvac import HeatingVentilationAirConditioning
from simses.system.auxiliary.heating_ventilation_air_conditioning.no_hvac import NoHeatingVentilationAirConditioning
from simses.system.dc_coupling.bus_charging_dc_coupling import BusChargingDcCoupling
from simses.system.dc_coupling.bus_charging_profile import BusChargingProfileDcCoupling
from simses.system.dc_coupling.dc_coupler import DcCoupling
from simses.system.dc_coupling.no_dc_coupling import NoDcCoupling
from simses.system.dc_coupling.usp_dc_coupling import USPDCCoupling
from simses.system.housing.abstract_housing import Housing
from simses.system.housing.forty_ft_container import FortyFtContainer
from simses.system.housing.no_housing import NoHousing
from simses.system.housing.twenty_ft_container import TwentyFtContainer
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter
from simses.system.power_electronics.acdc_converter.bonfiglioli import BonfiglioliAcDcConverter
from simses.system.power_electronics.acdc_converter.fix_efficiency import FixEfficiencyAcDcConverter
from simses.system.power_electronics.acdc_converter.no_loss import NoLossAcDcConverter
from simses.system.power_electronics.acdc_converter.notton import NottonAcDcConverter
from simses.system.power_electronics.acdc_converter.notton_loss import NottonLossAcDcConverter
from simses.system.power_electronics.acdc_converter.sinamics import Sinamics120AcDcConverter
from simses.system.power_electronics.acdc_converter.stable import M2bAcDcConverter
from simses.system.power_electronics.acdc_converter.stacked import AcDcConverterIdenticalStacked
from simses.system.power_electronics.acdc_converter.sungrow import SungrowAcDcConverter
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter
from simses.system.power_electronics.dcdc_converter.fix_efficiency import FixEfficiencyDcDcConverter
from simses.system.power_electronics.dcdc_converter.no_dcdc import NoDcDcConverter
from simses.system.power_electronics.dcdc_converter.no_loss import NoLossDcDcConverter
from simses.system.power_electronics.electronics import PowerElectronics
from simses.system.storage_system_ac import StorageSystemAC
from simses.system.storage_system_dc import StorageSystemDC
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.system.thermal.ambient.constant_temperature import ConstantAmbientTemperature
from simses.system.thermal.ambient.location_temperature import LocationAmbientTemperature
from simses.system.thermal.model.no_system_thermal_model import NoSystemThermalModel
from simses.system.thermal.model.system_thermal_model import SystemThermalModel
from simses.system.thermal.model.zero_d_room_thermal_model import ZeroDRoomThermalModel
from simses.system.thermal.model.zero_d_system_thermal_model import ZeroDSystemThermalModel
from simses.system.thermal.solar_irradiation.location import LocationSolarIrradiationModel
from simses.system.thermal.solar_irradiation.no_solar_irradiation import NoSolarIrradiationModel
from simses.system.thermal.solar_irradiation.solar_irradiation_model import SolarIrradiationModel
from simses.technology import hydrogen
from simses.technology import lithium_ion, redox_flow
from simses.technology.hydrogen.system import Hydrogen
from simses.technology.lithium_ion.battery import LithiumIonBattery
from simses.technology.lithium_ion.circuit import BatteryCircuit
from simses.technology.redox_flow.system import RedoxFlow
from simses.technology.storage import StorageTechnology


class StorageSystemFactory:
    """
    The StorageSystemFactory instantiates all necessary and configured objects for AC and DC storage systems.
    """

    __lithium_ion_name: str = lithium_ion.__name__.split('.')[-1]
    __hydrogen_name: str = hydrogen.__name__.split('.')[-1]
    __redox_flow_name: str = redox_flow.__name__.split('.')[-1]

    def __init__(self, config: ConfigParser):
        self.__log: Logger = Logger(type(self).__name__)
        self.__simulation_config: ConfigParser = config
        self.__system_config: StorageSystemConfig = StorageSystemConfig(config)
        self.__general_config: GeneralSimulationConfig = GeneralSimulationConfig(config)
        self.__power_electronics_data_config: PowerElectronicsConfig = PowerElectronicsConfig()
        self.__profile_config: ProfileConfig = ProfileConfig(config)
        self.__config_battery: BatteryConfig = BatteryConfig(config)
        self.__energy_management_data_config = EnergyManagementDataConfig()

    def create_acdc_converter(self, converter: str, max_power: float,
                              intermediate_cicuit_voltage: float) -> AcDcConverter:
        converter_configuration: dict = self.__system_config.acdc_converter
        converter_type = converter_configuration[converter][StorageSystemConfig.ACDC_CONVERTER_TYPE]
        acdc_converter: AcDcConverter = None
        if converter_type == NoLossAcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            acdc_converter = NoLossAcDcConverter(max_power)
        elif converter_type == NottonAcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            acdc_converter = NottonAcDcConverter(max_power)
        elif converter_type == FixEfficiencyAcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            try:
                efficiency: float = float(converter_configuration[converter][StorageSystemConfig.ACDC_CONVERTER_EFFICIENCY])
            except (TypeError, IndexError):
                efficiency: float = 0.95
            acdc_converter = FixEfficiencyAcDcConverter(max_power, efficiency)
        elif converter_type == M2bAcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            acdc_converter = M2bAcDcConverter(max_power)
        elif converter_type == NottonLossAcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            acdc_converter = NottonLossAcDcConverter(max_power)
        elif converter_type == Sinamics120AcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            acdc_converter = Sinamics120AcDcConverter(max_power, self.__power_electronics_data_config)
        elif converter_type == SungrowAcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            acdc_converter = SungrowAcDcConverter(max_power)
        elif converter_type == BonfiglioliAcDcConverter.__name__:
            self.__log.debug('Creating acdc converter as ' + converter_type)
            acdc_converter = BonfiglioliAcDcConverter(max_power)
        else:
            options: [str] = list()
            options.append(NoLossAcDcConverter.__name__)
            options.append(NottonAcDcConverter.__name__)
            options.append(NottonLossAcDcConverter.__name__)
            options.append(FixEfficiencyAcDcConverter.__name__)
            options.append(Sinamics120AcDcConverter.__name__)
            options.append(M2bAcDcConverter.__name__)
            options.append(SungrowAcDcConverter.__name__)
            options.append(BonfiglioliAcDcConverter.__name__)
            raise Exception('ACDC converter ' + converter_type + ' is unknown. '
                                                                 'Following options are available: ' + str(options))
        return self.create_stacked_acdc_converter(converter, acdc_converter)

    def create_stacked_acdc_converter(self, converter: str, acdc_converter: AcDcConverter) -> AcDcConverter:
        try:
            converter_configuration: dict = self.__system_config.acdc_converter
            number_converters: int = int(converter_configuration[converter][StorageSystemConfig.ACDC_CONVERTER_NUMBERS])
            if number_converters > 1:
                try:
                    switch_value: float = float(
                        converter_configuration[converter][StorageSystemConfig.ACDC_CONVERTER_SWITCH])
                except IndexError:
                    switch_value: float = 1.0
                return AcDcConverterIdenticalStacked(number_converters, switch_value,
                                                     acdc_converter, self.__power_electronics_data_config)
        except (TypeError, IndexError):
            pass
        return acdc_converter

    def create_dcdc_converter(self, converter: str, intermediate_circuit_voltage: float) -> DcDcConverter:
        converter_configuration: dict = self.__system_config.dcdc_converter
        converter_type = converter_configuration[converter][StorageSystemConfig.DCDC_CONVERTER_TYPE]
        if converter_type == NoLossDcDcConverter.__name__:
            self.__log.debug('Creating dcdc converter as ' + converter_type)
            return NoLossDcDcConverter(intermediate_circuit_voltage)
        elif converter_type == NoDcDcConverter.__name__:
            self.__log.debug('Creating dcdc converter as ' + converter_type)
            return NoDcDcConverter(intermediate_circuit_voltage)
        elif converter_type == FixEfficiencyDcDcConverter.__name__:
            self.__log.debug('Creating dcdc converter as ' + converter_type)
            try:
                efficiency: float = float(converter_configuration[converter][StorageSystemConfig.DCDC_CONVERTER_EFFICIENCY])
                return FixEfficiencyDcDcConverter(intermediate_circuit_voltage, efficiency)
            except IndexError:
                return FixEfficiencyDcDcConverter(intermediate_circuit_voltage)
        else:
            options: [str] = list()
            options.append(NoLossDcDcConverter.__name__)
            raise Exception('DCDC converter ' + converter_type + ' is unknown. '
                                                                 'Following options are available: ' + str(options))

    def create_ambient_temperature_model(self) -> AmbientThermalModel:
        if self.__system_config.thermal_simulation:
            ambient_temperature_model: str = str(self.__system_config.ambient_temperature_model[StorageSystemConfig.AMBIENT_TEMPERATURE_TYPE])
            if ambient_temperature_model == ConstantAmbientTemperature.__name__:
                self.__log.debug('Creating ambient temperature model as ' + ambient_temperature_model)
                try:
                    constant_ambient_temperature: float = float(self.__system_config.ambient_temperature_model[StorageSystemConfig.AMBIENT_TEMPERATURE_CONSTANT])
                    return ConstantAmbientTemperature(constant_ambient_temperature)
                except IndexError:
                    self.__log.debug(
                        'Creating ambient temperature model as ' + ambient_temperature_model + 'with default value of constant ambient temperature = 25°C.')
                    return ConstantAmbientTemperature()
            elif ambient_temperature_model == LocationAmbientTemperature.__name__:
                self.__log.debug('Creating ambient temperature model as ' + ambient_temperature_model)
                return LocationAmbientTemperature(self.__profile_config, self.__general_config)
            else:
                options: [str] = list()
                options.append(ConstantAmbientTemperature.__name__)
                options.append(LocationAmbientTemperature.__name__)
                raise Exception('Ambient temperature model ' + ambient_temperature_model + ' is unknown. '
                                                                                           'Following options are available: ' + str(
                    options))
        else:
            self.__log.debug('Creating ambient temperature model as ' + ConstantAmbientTemperature.__name__ + ' with default value of constant ambient temperature = 25°C.')
            return ConstantAmbientTemperature()

    def create_solar_irradiation_model(self, housing: Housing) -> SolarIrradiationModel:
        if self.__system_config.thermal_simulation:
            solar_irradiation_model: str = str(
                self.__system_config.solar_irradiation_model[StorageSystemConfig.SOLAR_IRRADIATION_TYPE])
            if solar_irradiation_model == NoSolarIrradiationModel.__name__:
                self.__log.debug('Creating solar irradiation model as ' + solar_irradiation_model)
                return NoSolarIrradiationModel()
            elif solar_irradiation_model == LocationSolarIrradiationModel.__name__:
                if isinstance(housing, NoHousing):
                    raise Exception('Solar irradiation model ' + solar_irradiation_model + ' is incompatible with '
                                    + NoHousing.__name__ + '. Please select another housing model, or select '
                                    + NoSolarIrradiationModel.__name__ + '.')
                self.__log.debug('Creating solar irradiation model as ' + solar_irradiation_model)
                return LocationSolarIrradiationModel(self.__profile_config, self.__general_config, housing)
            else:
                options: [str] = list()
                options.append(NoSolarIrradiationModel.__name__)
                options.append(LocationSolarIrradiationModel.__name__)
                raise Exception('Solar irradiation model ' + solar_irradiation_model + ' is unknown. '
                                                                                       'Following options are available: ' + str(
                    options))
        else:
            self.__log.debug('Creating solar irradiation model as ' + NoSolarIrradiationModel.__name__)
            return NoSolarIrradiationModel()

    def create_thermal_model_from(self, hvac: HeatingVentilationAirConditioning,
                                  ambient_thermal_model: AmbientThermalModel, housing: Housing,
                                  dc_systems: [StorageSystemDC], ac_dc_converter: AcDcConverter,
                                  solar_irradiation_model: SolarIrradiationModel) -> SystemThermalModel:

        supported_housing = (TwentyFtContainer, FortyFtContainer)

        if self.__system_config.thermal_simulation:
            if isinstance(housing, NoHousing):
                if isinstance(hvac, NoHeatingVentilationAirConditioning):
                    self.__log.debug('Creating thermal model for cell type ' + ZeroDRoomThermalModel.__class__.__name__)
                    return ZeroDRoomThermalModel(ambient_thermal_model, self.__general_config, dc_systems, ac_dc_converter)
                else:
                    raise Exception('Housing type' + NoHousing.__name__ + ' is only compatible with HVAC type ' + NoHeatingVentilationAirConditioning.__name__ + '.')
            elif isinstance(housing, supported_housing):
                self.__log.debug('Creating thermal model for cell type ' + ZeroDSystemThermalModel.__class__.__name__)
                return ZeroDSystemThermalModel(ambient_thermal_model, housing, hvac, self.__general_config,
                                               dc_systems, ac_dc_converter, solar_irradiation_model)
            else:
                raise Exception('Check if selected housing model is currently supported for thermal simulation, '
                                'or contact the SimSES Development Team.')
        else:
            self.__log.debug('Creating thermal model for cell type ' + NoSystemThermalModel.__class__.__name__)
            return NoSystemThermalModel(ambient_thermal_model, self.__general_config)

    def create_housing_from(self, housing_name: str, ambient_thermal_model: AmbientThermalModel) -> Housing:
        if self.__system_config.thermal_simulation:
            housing_configuration: dict = self.__system_config.housing
            housing_type = housing_configuration[housing_name][StorageSystemConfig.HOUSING_TYPE]
            if housing_type == NoHousing.__name__:
                self.__log.debug('Creating Housing model ' + NoHousing.__class__.__name__)
                return NoHousing()
            elif housing_type == TwentyFtContainer.__name__:
                self.__log.debug('Creating Housing model ' + TwentyFtContainer.__class__.__name__)
                return TwentyFtContainer(housing_configuration[housing_name],
                                         ambient_thermal_model.get_initial_temperature())
            elif housing_type == FortyFtContainer.__name__:
                self.__log.debug('Creating Housing model ' + FortyFtContainer.__class__.__name__)
                return FortyFtContainer(housing_configuration[housing_name],
                                        ambient_thermal_model.get_initial_temperature())
            else:
                options: [str] = list()
                options.append(NoHousing.__name__)
                options.append(TwentyFtContainer.__name__)
                options.append(FortyFtContainer.__name__)
                raise Exception('Housing model ' + housing_type + ' is unknown. '
                                                                  'Following options are available: ' + str(options))
        else:
            self.__log.debug('Creating Housing model ' + NoHousing.__class__.__name__)
            return NoHousing()

    def create_hvac_from(self, hvac: str, housing: Housing) -> HeatingVentilationAirConditioning:
        if self.__system_config.thermal_simulation:
            hvac_configuration: dict = self.__system_config.hvac
            hvac_type = hvac_configuration[hvac][StorageSystemConfig.HVAC_TYPE]

            supported_housing = (TwentyFtContainer, FortyFtContainer)
            supported_housing_names = [model.__name__ for model in supported_housing]

            if hvac_type == NoHeatingVentilationAirConditioning.__name__:
                self.__log.debug('Creating HVAC model ' + NoHeatingVentilationAirConditioning.__class__.__name__)
                return NoHeatingVentilationAirConditioning()
            elif hvac_type == FixCOPHeatingVentilationAirConditioning.__name__:
                if not isinstance(housing, supported_housing):
                    raise Exception('HVAC model ' + hvac_type + ' is incompatible with ' + housing.__class__.__name__
                                    + '. Please select ' + NoHeatingVentilationAirConditioning.__name__
                                    + ', or select a supported housing model: ' + str(supported_housing_names))
                self.__log.debug('Creating HVAC model ' + FixCOPHeatingVentilationAirConditioning.__class__.__name__)
                return FixCOPHeatingVentilationAirConditioning(hvac_configuration[hvac])
            elif hvac_type == FixCOPHeatingVentilationAirConditioningPIDControl.__name__:
                if not isinstance(housing, supported_housing):
                    raise Exception('HVAC model ' + hvac_type + ' is incompatible with ' + housing.__class__.__name__
                                    + '. Please select ' + NoHeatingVentilationAirConditioning.__name__
                                    + ', or select a supported housing model: ' + str(supported_housing_names))
                self.__log.debug('Creating HVAC model ' + FixCOPHeatingVentilationAirConditioningPIDControl.__class__.__name__)
                return FixCOPHeatingVentilationAirConditioningPIDControl(hvac_configuration[hvac])
            else:
                options: [str] = list()
                options.append(NoHeatingVentilationAirConditioning.__name__)
                options.append(FixCOPHeatingVentilationAirConditioning.__name__)
                raise Exception('HVAC model ' + hvac_type + ' is unknown. '
                                                            'Following options are available: ' + str(options))
        else:
            self.__log.debug('Creating HVAC model ' + NoHeatingVentilationAirConditioning.__class__.__name__)
            return NoHeatingVentilationAirConditioning()

    def create_system_state_from(self, system_id, storage_id) -> SystemState:
        state = SystemState(system_id, storage_id)
        state.set(SystemState.TIME, self.__general_config.start)
        state.set(SystemState.FULFILLMENT, 1.0)
        return state

    def create_power_distributor_ac(self) -> PowerDistributor:
        power_distributor_type: str = self.__system_config.power_distributor_ac
        if power_distributor_type == EqualPowerDistributor.__name__:
            return EqualPowerDistributor()
        elif power_distributor_type == SocBasedPowerDistributor.__name__:
            return SocBasedPowerDistributor()
        else:
            options: [str] = list()
            options.append(EqualPowerDistributor.__name__)
            options.append(SocBasedPowerDistributor.__name__)
            raise Exception('AC power distributor ' + power_distributor_type + ' is unknown. '
                                                                               'Following options are available: ' + str(
                options))

    def create_power_distributor_dc(self, dc_systems: [StorageSystemDC],
                                    power_electronics: PowerElectronics) -> PowerDistributor:
        power_distributor_dc: [str] = self.__system_config.power_distributor_dc
        power_distributor_type: str = power_distributor_dc[StorageSystemConfig.DC_POWER_DISTRIBUTOR_TYPE]
        if power_distributor_type == EqualPowerDistributor.__name__:
            return EqualPowerDistributor()
        elif power_distributor_type == SocBasedPowerDistributor.__name__:
            return SocBasedPowerDistributor()
        elif power_distributor_type == EfficientPowerDistributor.__name__:
            return EfficientPowerDistributor(power_electronics.max_power)
        elif power_distributor_type == TechnologyBasedPowerDistributor.__name__:
            systems: dict = dict()
            for dc_system in dc_systems:
                system_id: int = dc_system.state.get(SystemState.SYSTEM_DC_ID)
                technology: str = type(dc_system.get_storage_technology()).__name__
                systems[system_id] = technology
            priorities: [str] = copy.deepcopy(power_distributor_dc)
            del priorities[StorageSystemConfig.DC_POWER_DISTRIBUTOR_TYPE]
            found: bool = True
            for system in systems.values():
                system_found = False
                for priority in priorities:
                    if priority == system:
                        system_found = True
                        break
                found &= system_found
            if not priorities or not found:
                options: [str] = list()
                options.append(LithiumIonBattery.__name__)
                options.append(RedoxFlow.__name__)
                options.append(Hydrogen.__name__)
                raise Exception('No priorities for technologies are given or not all technologies are considered. '
                                'Following options are available: ' + str(options))
            return TechnologyBasedPowerDistributor(priorities, systems)
        else:
            options: [str] = list()
            options.append(EqualPowerDistributor.__name__)
            options.append(SocBasedPowerDistributor.__name__)
            options.append(TechnologyBasedPowerDistributor.__name__)
            raise Exception('DC power distributor ' + power_distributor_type + ' is unknown. '
                                                                               'Following options are available: ' + str(
                options))

    def create_storage_systems_ac(self, data_export: DataHandler) -> [StorageSystemAC]:
        ambient_thermal_model: AmbientThermalModel = self.create_ambient_temperature_model()
        ac_systems: [[str]] = self.__system_config.storage_systems_ac
        res: [StorageSystemAC] = list()
        names: [str] = list()
        id_number: int = 0
        for system in ac_systems:
            id_number += 1
            name = system[StorageSystemConfig.AC_SYSTEM_NAME]
            if name in names:
                raise Exception('Storage system name ' + name + ' is not unique.')
            names.append(name)
            power: float = float(system[StorageSystemConfig.AC_SYSTEM_POWER])
            intermediate_circuit_voltage: float = float(system[StorageSystemConfig.AC_SYSTEM_DC_VOLTAGE])
            converter: str = system[StorageSystemConfig.AC_SYSTEM_CONVERTER]
            housing: str = system[StorageSystemConfig.AC_SYSTEM_HOUSING]
            hvac: str = system[StorageSystemConfig.AC_SYSTEM_HVAC]
            acdc_converter: AcDcConverter = self.create_acdc_converter(converter, power, intermediate_circuit_voltage)
            housing_model: Housing = self.create_housing_from(housing, ambient_thermal_model)
            solar_irradiation_model: SolarIrradiationModel = self.create_solar_irradiation_model(housing_model)
            heating_cooling: HeatingVentilationAirConditioning = self.create_hvac_from(hvac, housing_model)
            hvac_set_point: float = heating_cooling.get_set_point_temperature()
            power_electronics: PowerElectronics = PowerElectronics(acdc_converter)
            dc_systems: [StorageSystemDC] = self.create_storage_systems_dc(name, data_export, hvac_set_point, ambient_thermal_model,
                                                                           intermediate_circuit_voltage, id_number)
            system_thermal_model: SystemThermalModel = self.create_thermal_model_from(heating_cooling,
                                                                                      ambient_thermal_model,
                                                                                      housing_model, dc_systems,
                                                                                      acdc_converter,
                                                                                      solar_irradiation_model)
            power_distributor: PowerDistributor = self.create_power_distributor_dc(dc_systems, power_electronics)
            state = self.create_system_state_from(id_number, 0)
            dc_couplings: [DcCoupling] = self.create_dc_couplings(name)
            res.append(StorageSystemAC(state, data_export, system_thermal_model, power_electronics, dc_systems,
                                       dc_couplings, housing_model, power_distributor))
        return res

    def create_dc_couplings(self, name: str) -> [DcCoupling]:
        dc_systems: [[str]] = self.__system_config.storage_systems_dc
        res: [DcCoupling] = list()
        for dc_system in dc_systems:
            system = dc_system[0]
            dc_type: str = dc_system[1]
            if system == name and DcCoupling.__name__ in dc_type:
                if dc_type == NoDcCoupling.__name__:
                    res.append(NoDcCoupling())
                elif dc_type == BusChargingDcCoupling.__name__:
                    charging_power: float = float(dc_system[2])
                    generation_power: float = float(dc_system[3])
                    res.append(BusChargingDcCoupling(charging_power, generation_power))
                elif dc_type == BusChargingProfileDcCoupling.__name__:
                    capacity: float = float(dc_system[2])
                    file_name: str = dc_system[3]
                    file: str = os.path.join(self.__profile_config.technical_profile_dir, file_name)
                    res.append(BusChargingProfileDcCoupling(self.__general_config, capacity, file))
                elif dc_type == USPDCCoupling.__name__:
                    file_name: str = dc_system[2]
                    res.append(USPDCCoupling(self.__general_config, self.__profile_config, file_name))
                else:
                    options: [str] = list()
                    options.append(NoDcCoupling.__name__)
                    options.append(BusChargingDcCoupling.__name__)
                    raise Exception('DcCoupling ' + dc_type + ' is unknown. '
                                                              'Following options are available: ' + str(options))
        return res

    def create_storage_systems_dc(self, name: str, data_export: DataHandler,
                                  hvac_set_point: float, ambient_thermal_model: AmbientThermalModel,
                                  intermediate_circuit_voltage: float, system_id: int) -> [StorageSystemDC]:
        dc_systems: [[str]] = self.__system_config.storage_systems_dc
        res: [StorageSystemDC] = list()
        storage_id = 0
        for dc_system in dc_systems:
            try:
                system = dc_system[StorageSystemConfig.DC_SYSTEM_NAME]
                dc_type: str = dc_system[StorageSystemConfig.DC_SYSTEM_CONVERTER]
                converter_configuration: dict = self.__system_config.dcdc_converter
                dc_converter: str = converter_configuration[dc_type][StorageSystemConfig.DCDC_CONVERTER_TYPE]
                if system == name and DcDcConverter.__name__ in dc_converter:
                    storage_id += 1
                    dcdc_converter: DcDcConverter = self.create_dcdc_converter(dc_type, intermediate_circuit_voltage)
                    technologies: [str] = copy.deepcopy(dc_system)
                    del technologies[StorageSystemConfig.DC_SYSTEM_CONVERTER]
                    del technologies[StorageSystemConfig.DC_SYSTEM_NAME]
                    storage_technology: StorageTechnology = self.create_storage_technology(technologies, data_export,
                                                                                           hvac_set_point, ambient_thermal_model,
                                                                                           storage_id, system_id,
                                                                                           intermediate_circuit_voltage)
                    res.append(StorageSystemDC(system_id, storage_id, data_export, dcdc_converter, storage_technology))
                    storage_id += max(0, len(technologies) - 1)
            except IndexError as err:
                raise Exception(str(err) + ' could not be found')
            except KeyError as err:
                raise Exception(str(err) + ' could not be found')
        if not res:
            raise Exception('Storage system ' + name + ' has no storage data. Please specify your storage system.')
        return res

    def create_storage_technology(self, technologies: [str], data_export: DataHandler,
                                  hvac_set_point: float, ambient_thermal_model: AmbientThermalModel,
                                  storage_id: int, system_id: int, voltage: float) -> StorageTechnology:
        technology_configuration: dict = self.__system_config.storage_technologies
        storage_configuration: dict = dict()
        for technology in technologies:
            technology_set: list = technology_configuration[technology]
            storage_type: str = technology_set[StorageSystemConfig.STORAGE_TYPE]
            if storage_type not in storage_configuration.keys():
                storage_configuration[storage_type] = list()
            storage_configuration[storage_type].append(technology_set)
        if self.__lithium_ion_name in storage_configuration.keys():
            batteries: [LithiumIonBattery] = list()
            for technology_set in storage_configuration[self.__lithium_ion_name]:
                capacity: float = float(technology_set[StorageSystemConfig.STORAGE_CAPACITY])
                cell: str = technology_set[StorageSystemConfig.BATTERY_CELL]
                try:
                    soc: float = float(technology_set[StorageSystemConfig.BATTERY_SOC])
                except (IndexError, ValueError):
                    soc: float = self.__config_battery.soc
                try:
                    soh: float = float(technology_set[StorageSystemConfig.BATTERY_SOH])
                except (IndexError, ValueError):
                    soh: float = self.__config_battery.start_soh
                batteries.append(LithiumIonBattery(cell, voltage, capacity, soc, soh, data_export,
                                                   hvac_set_point, storage_id,
                                                   system_id, self.__simulation_config))
                storage_id += 1
            if len(batteries) > 1:
                return BatteryCircuit(batteries)
            else:
                return batteries[0]
        elif self.__redox_flow_name in storage_configuration.keys():
            for technology_set in storage_configuration[self.__redox_flow_name]:
                capacity: float = float(technology_set[StorageSystemConfig.STORAGE_CAPACITY])
                stack_type = technology_set[StorageSystemConfig.REDOX_FLOW_STACK]
                stack_module_power: float = float(technology_set[StorageSystemConfig.STACK_MODULE_POWER])
                try:
                    pump_algorithm = technology_set[StorageSystemConfig.REDOX_FLOW_PUMP_ALGORITHM]
                except IndexError:
                    pump_algorithm = 'Default'
                return RedoxFlow(stack_type, stack_module_power, voltage, capacity, pump_algorithm,
                                 hvac_set_point, data_export,
                                 storage_id, system_id, self.__simulation_config)
        elif self.__hydrogen_name in storage_configuration.keys():
            if type(ambient_thermal_model).__name__ not in [ConstantAmbientTemperature.__name__]:
                raise Exception('Hydrogen models work currently only with ' + ConstantAmbientTemperature.__name__ + '. '
                                'Please adapt your config.')
            for technology_set in storage_configuration[self.__hydrogen_name]:
                capacity: float = float(technology_set[StorageSystemConfig.STORAGE_CAPACITY])
                fuel_cell = technology_set[StorageSystemConfig.FUEL_CELL_TYPE]
                fuel_cell_nominal_power = float(technology_set[StorageSystemConfig.FUEL_CELL_POWER])
                electrolyzer = technology_set[StorageSystemConfig.ELECTROLYZER_TYPE]
                electrolyzer_nominal_power = float(technology_set[StorageSystemConfig.ELECTROLYZER_POWER])
                storage = technology_set[StorageSystemConfig.HYDROGEN_STORAGE]
                max_pressure = float(technology_set[StorageSystemConfig.HYDROGEN_TANK_PRESSURE])
                return Hydrogen(data_export, fuel_cell, fuel_cell_nominal_power, electrolyzer,
                                electrolyzer_nominal_power, storage, capacity, max_pressure,
                                ambient_thermal_model.get_initial_temperature(), system_id, storage_id,
                                self.__simulation_config)
        else:
            options: [str] = list()
            options.append(self.__lithium_ion_name)
            options.append(self.__redox_flow_name)
            options.append(self.__hydrogen_name)
            raise Exception('Storage technology ' + str(technologies) + ' is unknown. '
                                                                        'Following options are available: ' + str(
                options))

    def close(self):
        self.__log.close()
