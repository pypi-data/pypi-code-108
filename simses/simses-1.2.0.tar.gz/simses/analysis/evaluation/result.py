import numpy as np

from simses.commons.utils.utilities import format_float


class Description:

    class Technical:
        ROUND_TRIP_EFFICIENCY: str = 'Efficiency round trip'
        MEAN_SOC: str = 'SOC mean'
        MAX_SOC: str = 'SOC max'
        MIN_SOC: str = 'SOC min'
        NUMBER_CHANGES_SIGNS: str = 'Number of changes of signs per day'
        RESTING_TIME_AVG: str = 'Avg. length of resting times'
        ENERGY_CHANGES_SIGN: str = 'Pos. energy between changes of sign'
        FULFILLMENT_AVG: str = 'Avg. Fulfillment Factor'
        EQUIVALENT_FULL_CYCLES: str = 'Equivalent full cycles'
        DEPTH_OF_DISCHARGE: str = 'Avg. depth of cycle for discharge'
        REMAINING_CAPACITY: str = 'Remaining capacity'
        SELF_CONSUMPTION_RATE: str = 'Self-consumption rate'
        SELF_SUFFICIENCY: str = 'Self-sufficiency'
        ENERGY_THROUGHPUT: str = 'Energy throughput'
        COULOMB_EFFICIENCY: str = 'Coulomb efficiency'
        MAX_GRID_POWER: str = 'Max. grid power'
        POWER_ABOVE_PEAK_MAX: str = 'Max. grid power above peak'
        POWER_ABOVE_PEAK_AVG: str = 'Average power above peak'
        ENERGY_ABOVE_PEAK_MAX: str = 'Max. energy event above peak'
        ENERGY_ABOVE_PEAK_AVG: str = 'Average energy event above peak'
        NUMBER_ENERGY_EVENTS: str = 'Number of energy events above peak'
        MAX_LOAD_DC_POWER_ADDITIONAL: str = 'Max. load of additional dc power'
        MAX_GENERATION_DC_POWER_ADDITIONAL: str = 'Max. generation of additional dc power'
        ACDC_EFFICIENCY_DISCHARGE: str = 'AC_DC efficiency discharge'
        ACDC_EFFICIENCY_CHARGE: str = 'AC_DC efficiency charge'
        ACDC_EFFICIENCY: str = 'AC_DC efficiency total'
        DCDC_EFFICIENCY_DISCHARGE: str = 'DC_DC efficiency discharge'
        DCDC_EFFICIENCY_CHARGE: str = 'DC_DC efficiency charge'
        DCDC_EFFICIENCY: str = 'DC_DC efficiency total'
        PE_EFFICIENCY: str = 'Power electronics efficiency total'
        H2_PRODUCTION_EFFICIENCY_LHV: str = 'Hydrogen production efficiency relative to LHV'
        TOTAL_H2_PRODUCTION_KG: str = 'Total mass of hydrogen'
        TOTAL_H2_PRODUCTION_NM: str = 'Total volume hydrogen'
        ENERGY_H2_LHV: str = 'Energy of Hydrogen relative to LHV'
        ENERGY_H2_DRYING: str = 'Energy for Drying of Hydrogen'
        ENERGY_H2_COMPRESSION: str = 'Energy for compression of hydrogen'
        ENERGY_H2_REACTION: str = 'Energy for chemical reaction'
        ENERGY_WATER_HEATING: str = 'Energy for heating of water'
        ENERGY_WATER_CIRCULATION: str = 'Energy for water circulation'
        SOH: str = 'Sate of Health'
        ENERGY_IDM_BOUGHT: str = 'Energy bought on intraday market'
        ENERGY_IDM_SOLD: str = 'Energy sold on intraday market'

    class Economical:
        CASHFLOW: str = 'Cashflow each year'
        NET_PRESENT_VALUE: str = 'NPV'
        INTERNAL_RATE_OF_RETURN: str = 'IRR'
        PROFITABILITY_INDEX: str = 'Profitability Index'
        RETURN_ON_INVEST: str = 'ROI'
        LEVELIZED_COST_OF_STORAGE: str = 'Levelized Cost of Storage'
        INVESTMENT_COSTS: str = 'Investment Costs'
        DISCOUNT_RATE: str = 'Discount Rate'

        class FCR:
            PRICE_AVERAGE: str = 'Average FCR Price Each Year'
            REVENUE_YEARLY: str = 'FCR Revenue Each Year'
            POWER_BID_AVERAGE: str = 'Average FCR Power Bid Each Year'

        class Intraday:
            PRICE_AVERAGE: str = 'Average Intraday Revenue Price Each Year'
            REVENUE_YEARLY: str = 'Intraday Revenue Each Year'
            POWER_AVERAGE: str = 'Average Intraday Power Each Year'

        class SCI:
            COST_WITHOUT_STORAGE: str = 'Electricity cost each year without storage system'
            COST_WITH_STORAGE: str = 'Electricity cost each year with storage system'
            COST_ELECTRICITY: str = 'Electricity Costs'
            PV_FEED_IN_TARIFF: str = 'PV Feed In Tariff'

        class DemandCharges:
            COST_WITHOUT_STORAGE: str = 'Demand charges each year without storage system'
            COST_WITH_STORAGE: str = 'Demand charges each year with storage system'
            CYCLE: str = 'Demand Charge Billing Cycle'
            PRICE: str = 'Demand Charge Price'
            INTERVAL: str = 'Demand Charge Average Interval'

        class OperationAndMaintenance:
            ANNUAl_O_AND_M_COST: str = 'Annual Op. and Maint. Cost '
            O_AND_M_COST: str = 'Op. and Maint. Cost each year'

        class ElectricityConsumption:
            ELECTRICITY_COST_RENEWABLE: str = 'Electricity cost renewable'
            ELECTRICITY_COST_GRID: str = 'Electricity cost grid'
            TOTAL_ELECTRICITY_COST: str = 'Total electricity Cost'
            ELECTRICITY_PRICE: str = 'Electricity price'


class Unit:
    NONE: str = ''
    PERCENTAGE: str = '%'
    MINUTES: str = 'min'
    EURO: str = 'EUR'
    WATT: str = 'W'
    KILOWATT: str = 'kW'
    KWH: str = 'kWh'
    EURO_PER_KW: str = 'EUR / kW'
    EURO_PER_MWH: str = 'EUR / MWh'
    EURO_PER_KWH: str = 'EUR / kWh'
    EURO_PER_KW_DAY: str = 'EUR / kW / d'
    NCM : str = 'Nm^3'
    KG: str = 'kg'


class EvaluationResult:
    """Provides a structure for evaluation results in order to organize data management for printing to
    the console, exporting to csv files, etc.."""

    def __init__(self, description: str, unit: str, value):
        self.__description: str = description
        self.__unit: str = unit
        self.__value = value

    @property
    def description(self) -> str:
        """Description of the result"""
        return self.__description

    @property
    def unit(self) -> str:
        """Unit of the result"""
        return self.__unit

    @property
    def value(self) -> str:
        """Value of the result"""
        if isinstance(self.__value, (int, float, complex)) and not np.isnan(self.__value):
            return format_float(self.__value, decimals=2)
        elif isinstance(self.__value, (list, np.ndarray)):
            return str([round(value, 2) for value in self.__value])
        else:
            return str(self.__value)

    def to_csv(self) -> [str]:
        """Returns EvaluationResult as a list of strings."""
        res = list()
        res.append(self.description)
        res.append(self.value)
        res.append(self.unit)
        return res

    def to_console(self) -> str:
        """Returns EvaluationResult as a string in a format that is suitable for printing to the console."""
        res = ''
        res += '{:<50}'.format(self.description)
        res += self.value + ' '
        res += self.unit
        return res

    @classmethod
    def get_header(cls) -> [str]:
        """Returns the header of EvaluationResult as a list of strings."""
        return [str(Description.__name__), 'Value', str(Unit.__name__)]

    def __str__(self):
        return self.to_csv()

    def __repr__(self):
        return self.to_csv()
