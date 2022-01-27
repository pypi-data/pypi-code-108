from configparser import ConfigParser

from simses.analysis.data.abstract_data import Data
from simses.analysis.data.electrolyzer import ElectrolyzerData
from simses.analysis.data.energy_management import EnergyManagementData
from simses.analysis.data.fuel_cell import FuelCellData
from simses.analysis.data.lithium_ion import LithiumIonData
from simses.analysis.data.redox_flow import RedoxFlowData
from simses.analysis.data.system import SystemData
from simses.analysis.evaluation.abstract_evaluation import Evaluation
from simses.analysis.evaluation.economic.economic_evaluation import EconomicEvaluation
from simses.analysis.evaluation.economic.revenue_stream.abstract_revenue_stream import RevenueStream
from simses.analysis.evaluation.economic.revenue_stream.demand_charge_reduction import DemandChargeReduction
from simses.analysis.evaluation.economic.revenue_stream.electricity_consumption import \
    ElectricityConsumptionRevenueStream
from simses.analysis.evaluation.economic.revenue_stream.energy_cost_reduction import EnergyCostReduction
from simses.analysis.evaluation.economic.revenue_stream.fcr_revenue_stream import FCRRevenue
from simses.analysis.evaluation.economic.revenue_stream.intraday_recharge import IntradayRechargeRevenue
from simses.analysis.evaluation.economic.revenue_stream.operation_and_maintenance import \
    OperationAndMaintenanceRevenue
from simses.analysis.evaluation.merger import EvaluationMerger
from simses.analysis.evaluation.technical.electrolyzer import ElectrolyzerTechnicalEvaluation
from simses.analysis.evaluation.technical.fuel_cell import FuelCellTechnicalEvaluation
from simses.analysis.evaluation.technical.lithium_ion import LithiumIonTechnicalEvaluation
from simses.analysis.evaluation.technical.redox_flow import RedoxFlowTechnicalEvaluation
from simses.analysis.evaluation.technical.site_level import SiteLevelEvaluation
from simses.analysis.evaluation.technical.system import SystemTechnicalEvaluation
from simses.commons.config.analysis.economic import EconomicAnalysisConfig
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.config.analysis.market import MarketProfileConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.log import Logger
from simses.logic.energy_management.strategy.basic.frequency_containment_reserve import \
    FrequencyContainmentReserve
from simses.logic.energy_management.strategy.basic.intraday_market_recharge import \
    IntradayMarketRecharge
from simses.logic.energy_management.strategy.basic.peak_shaving_perfect_foresight import \
    PeakShavingPerfectForesight
from simses.logic.energy_management.strategy.basic.peak_shaving_simple import \
    SimplePeakShaving
from simses.logic.energy_management.strategy.basic.residential_pv_feed_in_damp import \
    ResidentialPvFeedInDamp
from simses.logic.energy_management.strategy.basic.residential_pv_greedy import \
    ResidentialPvGreedy
from simses.logic.energy_management.strategy.basic.use_all_renewable_energy import \
    UseAllRenewableEnergy
from simses.logic.energy_management.strategy.stacked.fcr_idm_recharge_stacked import \
    FcrIdmRechargeStacked


class AnalysisFactory:

    # TODO Is the dependence of simulation pkg acceptable? --> MM
    __ENERGY_COST_REDUCTION: [str] = [ResidentialPvGreedy.__name__, ResidentialPvFeedInDamp.__name__,
                                      SimplePeakShaving.__name__, PeakShavingPerfectForesight.__name__]
    __DEMAND_CHARGE_REDUCTION: [str] = [SimplePeakShaving.__name__, PeakShavingPerfectForesight.__name__]
    __FREQUENCY_CONTAINMENT_RESERVE: [str] = [FrequencyContainmentReserve.__name__, FcrIdmRechargeStacked.__name__]
    __INTRADAY_MARKET: [str] = [FcrIdmRechargeStacked.__name__, IntradayMarketRecharge.__name__]
    __ELECTRICITY_CONSUMPTION_REVENUE_STREAM: [str] = [UseAllRenewableEnergy.__name__]

    def __init__(self, path: str, config: ConfigParser, version: str):
        self.__log: Logger = Logger(type(self).__name__)
        self.__result_path: str = path
        self.__version: str = version
        self.__analysis_config: GeneralAnalysisConfig = GeneralAnalysisConfig(config)
        self.__economic_analysis_config: EconomicAnalysisConfig = EconomicAnalysisConfig(config)
        self.__market_profile_config: MarketProfileConfig = MarketProfileConfig(config)
        self.__simulation_config: GeneralSimulationConfig = GeneralSimulationConfig(config=None, path=self.__result_path)
        self.__battery_config: BatteryConfig = BatteryConfig(config=None, path=self.__result_path)
        self.__energy_management_config: EnergyManagementConfig = EnergyManagementConfig(config=None, path=self.__result_path)
        self.__storage_system_config: StorageSystemConfig = StorageSystemConfig(config=None, path=self.__result_path)
        self.__do_plotting: bool = self.__analysis_config.plotting
        self.__do_system_analysis: bool = self.__analysis_config.system_analysis
        self.__do_lithium_ion_analysis: bool = self.__analysis_config.lithium_ion_analysis
        self.__do_redox_flow_analysis: bool = self.__analysis_config.redox_flow_analysis
        self.__do_hydrogen_analysis: bool = self.__analysis_config.hydrogen_analysis
        self.__do_site_level_analysis: bool = self.__analysis_config.site_level_analysis
        self.__do_economic_analysis: bool = self.__analysis_config.economical_analysis
        try:
            self.__energy_management_data: EnergyManagementData = EnergyManagementData.get_system_data(self.__result_path, self.__simulation_config)[0]
        except IndexError:
            self.__log.warn('No energy management data found!')
            self.__energy_management_data = None

    def __create_data_list(self) -> [Data]:
        config = self.__simulation_config
        path = self.__result_path
        data_list: [Data] = list()
        data_list.extend(SystemData.get_system_data(path, config))
        data_list.extend(LithiumIonData.get_system_data(path, config))
        data_list.extend(RedoxFlowData.get_system_data(path, config))
        #  data_list.extend(HydrogenData.get_system_data(path, config))
        data_list.extend(ElectrolyzerData.get_system_data(path, config))
        data_list.extend(FuelCellData.get_system_data(path, config))
        for data in data_list:
            self.__log.info('Created ' + type(data).__name__)
        return data_list

    def __create_revenue_streams(self, system_data) -> [RevenueStream]:
        revenue_streams: [RevenueStream] = list()
        economic_config: EconomicAnalysisConfig = self.__economic_analysis_config
        energy_management_strategy: str = self.__energy_management_config.operation_strategy
        if self.__energy_management_data is None:
            self.__log.warn('No energy management data available ----> No economic evaluation possible!')
            return revenue_streams
        if energy_management_strategy in self.__ENERGY_COST_REDUCTION:
            revenue_streams.append(EnergyCostReduction(self.__energy_management_data, system_data, economic_config))
            self.__log.info('Adding ' + EnergyCostReduction.__name__ + ' to revenue streams')
        if energy_management_strategy in self.__DEMAND_CHARGE_REDUCTION:
            revenue_streams.append(DemandChargeReduction(self.__energy_management_data, system_data, economic_config))
            self.__log.info('Adding ' + DemandChargeReduction.__name__ + ' to revenue streams')
        if energy_management_strategy in self.__FREQUENCY_CONTAINMENT_RESERVE:
            revenue_streams.append(FCRRevenue(self.__energy_management_data, system_data, economic_config,
                                              self.__simulation_config, self.__market_profile_config))
            self.__log.info('Adding ' + FCRRevenue.__name__ + ' to revenue streams')
        if energy_management_strategy in self.__INTRADAY_MARKET:
            revenue_streams.append(IntradayRechargeRevenue(self.__energy_management_data, system_data, economic_config,
                                                           self.__simulation_config, self.__market_profile_config))
            self.__log.info('Adding ' + IntradayRechargeRevenue.__name__ + ' to revenue streams')
        if energy_management_strategy in self.__ELECTRICITY_CONSUMPTION_REVENUE_STREAM:
            revenue_streams.append(ElectricityConsumptionRevenueStream(self.__energy_management_data, system_data, economic_config))
            self.__log.info('Adding ' + ElectricityConsumptionRevenueStream.__name__ + ' to revenue streams')
        if not revenue_streams:
            self.__log.warn('No revenue streams are defined for chosen Energy Management Strategy: ' + energy_management_strategy)
        revenue_streams.append(OperationAndMaintenanceRevenue(self.__energy_management_data, system_data, economic_config))
        self.__log.info('Adding ' + OperationAndMaintenanceRevenue.__name__ + ' to revenue streams')
        return revenue_streams

    def create_evaluations(self) -> [Evaluation]:
        data_list: [Data] = self.__create_data_list()
        evaluations: [Evaluation] = list()
        config: GeneralAnalysisConfig = self.__analysis_config
        ems_config: EnergyManagementConfig = self.__energy_management_config
        path: str = self.__result_path
        for data in data_list:
            if isinstance(data, SystemData):
                if self.__do_system_analysis:
                    evaluations.append(SystemTechnicalEvaluation(data, config, path))
                if data.is_top_level_system and self.__energy_management_data is not None:
                    if self.__do_site_level_analysis:
                        evaluations.append(SiteLevelEvaluation(data, self.__energy_management_data, config, ems_config,
                                                               path))
                    if self.__do_economic_analysis:
                        revenue_streams = self.__create_revenue_streams(data)
                        evaluations.append(EconomicEvaluation(data, self.__economic_analysis_config, revenue_streams,
                                                              config, self.__storage_system_config))
            elif isinstance(data, LithiumIonData) and self.__do_lithium_ion_analysis:
                evaluations.append(LithiumIonTechnicalEvaluation(data, config, self.__battery_config, path))
            elif isinstance(data, RedoxFlowData) and self.__do_redox_flow_analysis:
                evaluations.append(RedoxFlowTechnicalEvaluation(data, config, path))
            #  elif isinstance(data, HydrogenData) and self.__do_hydrogen_analysis:
            #     evaluations.append(HydrogenTechnicalEvaluation(data, config, path))
            elif isinstance(data, ElectrolyzerData) and self.__do_hydrogen_analysis:
                evaluations.append(ElectrolyzerTechnicalEvaluation(data, config, path))
            elif isinstance(data, FuelCellData) and self.__do_hydrogen_analysis:
                evaluations.append(FuelCellTechnicalEvaluation(data, config, path))
        return evaluations

    def create_evaluation_merger(self) -> EvaluationMerger:
        return EvaluationMerger(self.__result_path, self.__analysis_config, self.__version)

    def close(self):
        self.__log.close()
        # TODO close Data but not for all instances
        # Data.close()
