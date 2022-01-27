from configparser import ConfigParser
from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.cycle_detection.cycle_detector import CycleDetector
from simses.commons.cycle_detection.half_cycle_detector import HalfCycleDetector
from simses.commons.cycle_detection.no_cycle_detector import NoCycleDetector
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.battery_management_system.management_system import BatteryManagementSystem
from simses.technology.lithium_ion.cell.NREL_dummy_cell import NRELDummyCell
from simses.technology.lithium_ion.cell.NREL_dummy_cell_2 import NRELDummyCell2
from simses.technology.lithium_ion.cell.generic import GenericCell
from simses.technology.lithium_ion.cell.isea import IseaCellType
from simses.technology.lithium_ion.cell.lfp_sony import SonyLFP
from simses.technology.lithium_ion.cell.lfp_sony_generic import SonyLFPGeneric
from simses.technology.lithium_ion.cell.lmo_daimler import DaimlerLMO
from simses.technology.lithium_ion.cell.lto_lmo import LTOLMO
from simses.technology.lithium_ion.cell.lto_nmc import LTONMC
from simses.technology.lithium_ion.cell.nca_panasonic_generic import PanasonicNCAGeneric
from simses.technology.lithium_ion.cell.nca_panasonic_ncr import PanasonicNCA
from simses.technology.lithium_ion.cell.nmc_molicel import MolicelNMC
from simses.technology.lithium_ion.cell.nmc_molicel_generic import MolicelNMCGeneric
from simses.technology.lithium_ion.cell.nmc_samsung78Ah import Samsung78AhNMC
from simses.technology.lithium_ion.cell.nmc_samsung94Ah import Samsung94AhNMC
from simses.technology.lithium_ion.cell.nmc_samsung94Ah_hybrid import Samsung94AhNMCHybrid
from simses.technology.lithium_ion.cell.nmc_sanyo_ur18650e import SanyoNMC
from simses.technology.lithium_ion.cell.nmc_lgmj1 import LGMJ1_NMC
from simses.technology.lithium_ion.cell.sodium_ion.sodium_ion_green_rock import SodiumIonGreenRock
from simses.technology.lithium_ion.cell.type import CellType
from simses.technology.lithium_ion.degradation.degradation_model import DegradationModel
from simses.technology.lithium_ion.degradation.generic_cell import GenericCellDegradationModel
from simses.technology.lithium_ion.degradation.lfp_generic import LFPGenericDegradationModel
from simses.technology.lithium_ion.degradation.lfp_sony import SonyLFPDegradationModel
from simses.technology.lithium_ion.degradation.lmo_daimler import DaimlerLMODegradationModel
from simses.technology.lithium_ion.degradation.lto_lmo import LTOLMODegradationModel
from simses.technology.lithium_ion.degradation.lto_nmc import LTONMCDegradationModel
from simses.technology.lithium_ion.degradation.nca_generic import NCAGenericDegradationModel
from simses.technology.lithium_ion.degradation.nca_panasonicNCR import \
    PanasonicNCADegradationModel
from simses.technology.lithium_ion.degradation.nmc_generic import NMCGenericDegradationModel
from simses.technology.lithium_ion.degradation.nmc_molicel import MolicelNMCDegradationModel
from simses.technology.lithium_ion.degradation.nmc_samsung94Ah import \
    Samsung94AhNMCDegradationModel
from simses.technology.lithium_ion.degradation.nmc_sanyo_ur18650e import \
    SanyoNMCDegradationModel
from simses.technology.lithium_ion.degradation.nmc_lgmj1 import LGMJ1_NMCDegradationModel
from simses.technology.lithium_ion.degradation.no_degradation import NoDegradationModel
from simses.technology.lithium_ion.equivalent_circuit_model.equivalent_circuit import EquivalentCircuitModel
from simses.technology.lithium_ion.equivalent_circuit_model.rint_model import RintModel


class LithiumIonFactory:
    
    def __init__(self, config: ConfigParser):
        self.__log: Logger = Logger(type(self).__name__)
        self.__config_factory: StorageSystemConfig = StorageSystemConfig(config)
        self.__config_general: GeneralSimulationConfig = GeneralSimulationConfig(config)
        self.__config_battery: BatteryConfig = BatteryConfig(config)
        self.__config_battery_data: BatteryDataConfig = BatteryDataConfig()

    def create_battery_state_from(self, system_id: int, storage_id: int, cell_type: CellType,
                                  temperature: float, soc: float) -> LithiumIonState:
        time: float = self.__config_general.start
        bs = LithiumIonState(system_id, storage_id)
        bs.time = time
        bs.soc = soc
        bs.temperature = temperature
        bs.voltage = cell_type.get_open_circuit_voltage(bs)
        bs.voltage_open_circuit = cell_type.get_open_circuit_voltage(bs)
        bs.nominal_voltage = cell_type.get_nominal_voltage()

        bs.resistance_increase = cell_type.get_resistance_increase_start()
        bs.internal_resistance = cell_type.get_internal_resistance(bs) * (1 + bs.resistance_increase)
        bs.capacity = cell_type.get_capacity(bs) * cell_type.get_nominal_voltage() * cell_type.get_soh_start()
        bs.soh = cell_type.get_soh_start()
        bs.soe = bs.soc * bs.capacity
        bs.fulfillment = 1.0
        bs.max_charge_power = cell_type.get_max_current(bs) * bs.voltage
        bs.max_discharge_power = cell_type.get_min_current(bs) * bs.voltage
        return bs

    def create_cell_type(self, cell_type: str, voltage: float, capacity: float, soh: float) -> CellType:
        if cell_type.startswith(SonyLFPGeneric.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return SonyLFPGeneric(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(SonyLFP.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return SonyLFP(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(PanasonicNCAGeneric.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return PanasonicNCAGeneric(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(PanasonicNCA.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return PanasonicNCA(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(MolicelNMCGeneric.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return MolicelNMCGeneric(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(MolicelNMC.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return MolicelNMC(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(SanyoNMC.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return SanyoNMC(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(GenericCell.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return GenericCell(voltage, capacity, soh, self.__config_battery)
        elif cell_type.startswith(LTOLMO.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return LTOLMO(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(LTONMC.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return LTONMC(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(NRELDummyCell2.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return NRELDummyCell2(voltage, capacity, soh, self.__config_battery)
        elif cell_type.startswith(NRELDummyCell.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return NRELDummyCell(voltage, capacity, soh, self.__config_battery)
        elif cell_type.startswith(Samsung78AhNMC.__name__):
            self.__log.debug('Creating cell type as ' + cell_type)
            return Samsung78AhNMC(voltage, capacity, soh, self.__config_battery)
        elif cell_type.startswith(DaimlerLMO.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return DaimlerLMO(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(Samsung94AhNMCHybrid.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return Samsung94AhNMCHybrid(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(Samsung94AhNMC.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return Samsung94AhNMC(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(IseaCellType.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            file_name: str = cell_type.split(';')[1]
            return IseaCellType(voltage, capacity, soh, self.__config_battery, self.__config_battery_data, file_name)
        elif cell_type.startswith(SodiumIonGreenRock.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return SodiumIonGreenRock(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        elif cell_type.startswith(LGMJ1_NMC.__name__):
            self.__log.debug('Creating cell type as' + cell_type)
            return LGMJ1_NMC(voltage, capacity, soh, self.__config_battery, self.__config_battery_data)
        else:
            options: [str] = list()
            options.append(SonyLFP.__name__)
            options.append(LTOLMO.__name__)
            options.append(LTONMC.__name__)
            options.append(PanasonicNCA.__name__)
            options.append(MolicelNMC.__name__)
            options.append(SanyoNMC.__name__)
            options.append(GenericCell.__name__)
            options.append(Samsung78AhNMC.__name__)
            options.append(DaimlerLMO.__name__)
            options.append(Samsung94AhNMC.__name__)
            options.append(Samsung94AhNMCHybrid.__name__)
            options.append(LGMJ1_NMC.__name__)
            raise Exception('Specified cell type ' + cell_type + ' is unknown. '
                            'Following options are available: ' + str(options))

    def create_cycle_detector(self, start_soc: float) -> CycleDetector:
        cycle_detector = self.__config_factory.cycle_detector
        if cycle_detector == HalfCycleDetector.__name__:
            self.__log.debug('Creating cycle detector as ' + cycle_detector)
            return HalfCycleDetector(start_soc, self.__config_general)
        elif cycle_detector == NoCycleDetector.__name__:
            self.__log.debug('Creating cycle detector as ' + cycle_detector)
            return NoCycleDetector()
        else:
            self.__log.warn(
                'Specified cycle detector ' + str(cycle_detector) + ' not found, creating ' + NoCycleDetector.__name__)
            return NoCycleDetector()

    def create_degradation_model_from(self, cell_type: CellType, battery_state: LithiumIonState) -> DegradationModel:
        cycle_detector: CycleDetector = self.create_cycle_detector(battery_state.soc)
        if isinstance(cycle_detector, NoCycleDetector):
            self.__log.debug('Creating NoDegradationModel for cell type ' + cell_type.__class__.__name__)
            return NoDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, SonyLFPGeneric):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return LFPGenericDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, SonyLFP):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return SonyLFPDegradationModel(cell_type, cycle_detector, self.__config_battery, self.__config_battery_data)
        elif isinstance(cell_type, PanasonicNCAGeneric):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return NCAGenericDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, PanasonicNCA):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return PanasonicNCADegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, MolicelNMCGeneric):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return NMCGenericDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, MolicelNMC):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return MolicelNMCDegradationModel(cell_type, cycle_detector, self.__config_battery, self.__config_battery_data)
        elif isinstance(cell_type, SanyoNMC):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return SanyoNMCDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, DaimlerLMO):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return DaimlerLMODegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, Samsung94AhNMCHybrid):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return SonyLFPDegradationModel(cell_type, cycle_detector, self.__config_battery, self.__config_battery_data)
        elif isinstance(cell_type, Samsung94AhNMC):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return Samsung94AhNMCDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, GenericCell):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return GenericCellDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, LTOLMO):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return LTOLMODegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, LTONMC):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return LTONMCDegradationModel(cell_type, cycle_detector, self.__config_battery)
        elif isinstance(cell_type, LGMJ1_NMC):
            self.__log.debug('Creating degradation model for cell type ' + cell_type.__class__.__name__)
            return LGMJ1_NMCDegradationModel(cell_type, cycle_detector, self.__config_battery)
        else:
            self.__log.warn('No degradation model found for cell type ' + cell_type.__class__.__name__)
            return NoDegradationModel(cell_type, cycle_detector, self.__config_battery)

    def create_battery_management_system_from(self, cell_type: CellType,
                                              battery_management_system: BatteryManagementSystem = None) -> BatteryManagementSystem:
        if battery_management_system is None:
            self.__log.debug('Creating lithium_ion management system for cell type ' + cell_type.__class__.__name__)
            return BatteryManagementSystem(cell_type, self.__config_battery)
        else:
            return battery_management_system

    def create_battery_model_from(self, cell_type: CellType,
                                  battery_model: EquivalentCircuitModel = None) -> EquivalentCircuitModel:
        if battery_model is None:
            self.__log.debug('Creating lithium_ion model for cell type ' + cell_type.__class__.__name__)
            return RintModel(cell_type)
        else:
            return battery_model

    def close(self):
        self.__log.close()
