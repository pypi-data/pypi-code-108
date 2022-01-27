from configparser import ConfigParser

from simses.commons.config.analysis.analysis_config import AnalysisConfig


class EconomicAnalysisConfig(AnalysisConfig):

    """
    Provides
    """

    SECTION: str = 'ECONOMIC_ANALYSIS'

    INVESTMENT_COSTS: str = 'INVESTMENT_COSTS'
    SPECIFIC_INVESTMENT_COSTS_ENERGY: str = 'SPECIFIC_INVESTMENT_COSTS_ENERGY'
    SPECIFIC_INVESTMENT_COSTS_POWER: str = 'SPECIFIC_INVESTMENT_COSTS_POWER'
    USE_SPECIFIC_COSTS: str = 'USE_SPECIFIC_COSTS'
    DISCOUNT_RATE: str = 'DISCOUNT_RATE'
    ELECTRICITY_PRICE: str = 'ELECTRICITY_PRICE'
    PV_FEED_IN_TARIFF: str = 'PV_FEED_IN_TARIFF'
    DEMAND_CHARGE_BILLING_PERIOD: str = 'DEMAND_CHARGE_BILLING_PERIOD'
    DEMAND_CHARGE_PRICE: str = 'DEMAND_CHARGE_PRICE'
    DEMAND_CHARGE_AVERAGE_INTERVAL: str = 'DEMAND_CHARGE_AVERAGE_INTERVAL'
    FCR_PRICE: str = 'FCR_PRICE'
    FCR_USE_PRICE_TIMESERIES: str = 'FCR_USE_PRICE_TIMESERIES'
    IDM_PRICE: str = 'IDM_PRICE'
    IDM_USE_PRICE_TIMESERIES: str = 'IDM_USE_PRICE_TIMESERIES'
    ADD_OPERATION_AND_MAINTENANCE_REVENUE_STREAM: str = 'ADD_OPERATION_AND_MAINTENANCE_REVENUE_STREAM'
    ANNUAL_RELATIVE_OPERATION_AND_MAINTENANCE_COSTS: str = 'ANNUAL_RELATIVE_OPERATION_AND_MAINTENANCE_COSTS'
    RENEWABLE_ELECTRICITY_PRICE: str = 'RENEWABLE_ELECTRICITY_PRICE'

    def __init__(self, config: ConfigParser, path: str = None):
        super().__init__(path, config)

    @property
    def investment_costs(self) -> float:
        """Defines initial investment costs for the energy storage system"""
        return float(self.get_property(self.SECTION, self.INVESTMENT_COSTS))

    @property
    def specific_investment_costs_energy(self) -> float:
        """Defines specific investment costs for the energy storage system in Euro/kWh"""
        return float(self.get_property(self.SECTION, self.SPECIFIC_INVESTMENT_COSTS_ENERGY))

    @property
    def specific_investment_costs_power(self) -> float:
        """Defines additional specific investment costs for the energy storage system in Euro/kW"""
        return float(self.get_property(self.SECTION, self.SPECIFIC_INVESTMENT_COSTS_POWER))

    @property
    def use_specific_costs(self) -> bool:
        """Determine if specific costs or absolute costs are used to determine the investment costs"""
        return self.get_property(self.SECTION, self.USE_SPECIFIC_COSTS) in ['True']

    @property
    def discount_rate(self) -> float:
        """Defines the discount rate in p.u."""
        return float(self.get_property(self.SECTION, self.DISCOUNT_RATE))

    @property
    def electricity_price(self) -> float:
        """Defines the electricity price in Euro/kWh"""
        return float(self.get_property(self.SECTION, self.ELECTRICITY_PRICE))

    @property
    def pv_feed_in_tariff(self) -> float:
        """Defines the feed in tariff in Euro/kWh"""
        return float(self.get_property(self.SECTION, self.PV_FEED_IN_TARIFF))

    @property
    def demand_charge_billing_period(self) -> str:
        """Defines the billing period. Choose 'yearly' or 'monthly'"""
        return self.get_property(self.SECTION, self.DEMAND_CHARGE_BILLING_PERIOD)

    @property
    def demand_charge_price(self) -> float:
        """Defines the demand charge price in Euro/kW"""
        return float(self.get_property(self.SECTION, self.DEMAND_CHARGE_PRICE))

    @property
    def demand_charge_average_interval(self) -> float:
        """Interval length for determining power average in seconds"""
        return float(self.get_property(self.SECTION, self.DEMAND_CHARGE_AVERAGE_INTERVAL))

    @property
    def fcr_price(self) -> float:
        """FCR price in Euro per kW per day"""
        return float(self.get_property(self.SECTION, self.FCR_PRICE))

    @property
    def fcr_use_price_timeseries(self) -> bool:
        """Determine if constant FCR price or prices from FCR_PRICE_PROFILE are used."""
        return self.get_property(self.SECTION, self.FCR_USE_PRICE_TIMESERIES) in ['True']

    @property
    def idm_price(self) -> float:
        """IDM price in Euro per kWh"""
        return float(self.get_property(self.SECTION, self.IDM_PRICE))

    @property
    def idm_use_price_timeseries(self) -> bool:
        """Determine if constant IDM price or prices from IDM_PRICE_PROFILE are used."""
        return self.get_property(self.SECTION, self.IDM_USE_PRICE_TIMESERIES) in ['True']

    @property
    def add_o_and_m_revenue_stream(self) -> bool:
        """ Defines if operation and maintenance revenue stream is used """
        return self.get_property(self.SECTION, self.ADD_OPERATION_AND_MAINTENANCE_REVENUE_STREAM) in ['True']

    @property
    def annual_realative_o_and_m_costs(self) -> float:
        """Relative annual costs for operation and maintenance related to investment costs in p.u."""
        return float(self.get_property(self.SECTION, self.ANNUAL_RELATIVE_OPERATION_AND_MAINTENANCE_COSTS))

    @property
    def renewable_electricity_price(self) -> float:
        """ price for electricity out of renewable source in Euro per kWh """
        return float(self.get_property(self.SECTION, self.RENEWABLE_ELECTRICITY_PRICE))
