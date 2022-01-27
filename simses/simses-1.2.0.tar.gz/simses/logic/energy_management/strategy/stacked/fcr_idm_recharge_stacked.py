from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.logic.energy_management.strategy.basic.frequency_containment_reserve import \
    FrequencyContainmentReserve
from simses.logic.energy_management.strategy.basic.intraday_market_recharge import \
    IntradayMarketRecharge
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.stacked.stacked_operation_strategy import \
    StackedOperationStrategy


class FcrIdmRechargeStacked(StackedOperationStrategy):

    def __init__(self, general_config: GeneralSimulationConfig, ems_config: EnergyManagementConfig,
                 profile_config: ProfileConfig):
        super().__init__(OperationPriority.VERY_HIGH, [FrequencyContainmentReserve(general_config, ems_config, profile_config),
                                                       IntradayMarketRecharge(general_config, ems_config)])
