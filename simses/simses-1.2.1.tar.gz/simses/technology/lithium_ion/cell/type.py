import math
from abc import ABC, abstractmethod
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.commons.utils.utilities import format_float
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties


class CellType(ABC):
    """A CellType describes a generic lithium_ion cell type. Abstract
    methods have to be completed in inherited classes, e.g. LFP."""

    __RANGE: float = 0.1  # range for parameter search in p.u.
    __LARGE_NUMBER: float = 1e100

    def __init__(self, voltage: float, capacity: float, soh: float, electrical_props: ElectricalCellProperties,
                 thermal_props: ThermalCellProperties, cell_format: CellFormat, battery_config: BatteryConfig):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__exact_size: bool = battery_config.exact_size  # True if serial / parallel connection can be floats
        if capacity == 0.0:
            serial, parallel = battery_config.serial_scale, battery_config.parallel_scale
        else:
            serial, parallel = self.__nearest_neighbor(voltage, capacity, electrical_props.get_nominal_voltage(),
                                                       electrical_props.get_nominal_capacity())
        self.__SERIAL_SCALE: float = serial
        self.__PARALLEL_SCALE: float = parallel
        self.__consider_voltage_limit: bool = battery_config.consider_voltage_limit
        self.__soh_start: float = soh  # p.u.
        start_soh_share: float = battery_config.start_soh_share
        self.__calendar_capacity_loss_start = (1.0 - self.__soh_start) * start_soh_share  # p.u.
        self.__cyclic_capacity_loss_start = (1.0 - self.__soh_start) * (1.0 - start_soh_share)  # p.u.

        self.__calendar_resistance_increase_start = (1.0 - self.__soh_start) * start_soh_share * 5  # p.u.
        self.__cyclic_resistance_increase_start = (1.0 - self.__soh_start) * (1.0 - start_soh_share) * 5  # p.u.
        self.__resistance_increase_start = self.__calendar_resistance_increase_start + \
                                           self.__cyclic_resistance_increase_start

        self.__thermal_props: ThermalCellProperties = thermal_props
        self.__electrical_props: ElectricalCellProperties = electrical_props
        self.__cell_format: CellFormat = cell_format
        self.__log.debug('serial: ' + str(serial) + ', parallel: ' + str(parallel))

    def __nearest_neighbor(self, voltage: float, capacity: float, cell_voltage: float, cell_capacity: float):
        if self.__exact_size:
            serial: float = voltage / cell_voltage
            parallel: float = capacity / voltage / cell_capacity
            return serial, parallel
        elif voltage == 0 or capacity == 0:
            self.__log.debug('Target cell voltage or capacity are 0. Serial and parallel scale are set to '
                             'single cell (1,1)')
            return 1, 1
        # define search range
        min_serial: int = max(1, math.floor(voltage / cell_voltage * (1 - self.__RANGE)))
        max_serial: int = max(1, math.ceil(voltage / cell_voltage * (1 + self.__RANGE)))
        min_capacity: float = capacity * (1 - self.__RANGE)
        max_capacity: float = capacity * (1 + self.__RANGE)
        # set start parameters
        serial: int = max(1, round(voltage / cell_voltage))
        parallel: int = max(1, round(capacity / voltage / cell_capacity))
        res: float = cell_voltage * serial * cell_capacity * parallel
        # begin search
        for s in range(min_serial, max_serial, 1):
            voltage_tmp = cell_voltage * s
            parallel_min = math.floor(capacity / voltage_tmp / cell_capacity)
            parallel_max = math.ceil(capacity / voltage_tmp / cell_capacity)
            for p in range(parallel_min, parallel_max, 1):
                capacity_tmp = cell_capacity * p
                res_tmp = voltage_tmp * capacity_tmp
                if min_capacity < res_tmp < max_capacity and abs(res_tmp - capacity) < abs(res - capacity):
                    serial, parallel, res = s, p, res_tmp
                    self.__log.debug('Found better fit: ' + format_float(res) + ' Wh, ' + str(serial) + ', ' + str(parallel))
        # log results
        self.__log.debug('Difference:  ' + format_float(cell_voltage * serial - voltage) + 'V, '
                         + format_float((cell_voltage * serial - voltage) / voltage * 100.0) + '%')
        self.__log.debug('Difference: ' + format_float(cell_capacity * parallel - capacity/voltage) + 'Ah, '
                         + format_float((cell_capacity * parallel * voltage - capacity) / capacity * 100.0) + '%')
        self.__log.debug('Difference: ' + format_float(res - capacity) + 'Wh, '
                         + format_float((res - capacity) / capacity * 100.0) + '%')
        if res < min_capacity or res > max_capacity:
            self.__log.warn('System capacity is not in range of ' + format_float(self.__RANGE * 100.0) + '%')
        return serial, parallel

    def get_calendar_capacity_loss_start(self) -> float:
        return self.__calendar_capacity_loss_start

    def get_cyclic_capacity_loss_start(self) -> float:
        return self.__cyclic_capacity_loss_start

    def get_calendar_resistance_increase_start(self) -> float:
        return self.__calendar_resistance_increase_start

    def get_cyclic_resistance_increase_start(self) -> float:
        return self.__cyclic_resistance_increase_start

    def get_resistance_increase_start(self) -> float:
        return self.__resistance_increase_start

    def get_soh_start(self) -> float:
        return self.__soh_start

    def check_soc_range(self, soc: float) -> float:
        if soc < 0.0 or soc > 1.0:
            self.__log.warn(str(soc) + ' is out of interpolation range')
            soc = min(1.0, max(0.0, soc))
        return soc

    @abstractmethod
    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        """
        Determines the open circuit voltage based on the current BatteryState and a lookup table for every cell type.

        Parameters
        ----------
        battery_state : LithiumIonState
            Current state of the lithium_ion.

        Returns
        -------
        float:
            Open circuit voltage of the cell in V

        """
        pass

    @abstractmethod
    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        """
        Determines the internal resistance based on the current BatteryState and a lookup table for every cell type.

        Parameters
        ----------
        battery_state : LithiumIonState
            Current state of the lithium_ion.

        Returns
        -------
        float:
            Internal resistance of the cell in Ohm

        """
        pass

    def get_coulomb_efficiency(self, battery_state: LithiumIonState) -> float:
        """
        Determines the coulomb efficiency based on if the lithium_ion is charging or discharging.

        Default: 1.0 -> losses are calculated via internal resistance

        Parameters
        ----------
        battery_state : LithiumIonState
            Current BatteryState of the lithium_ion. Used to determine if the lithium_ion is charging or discharging.

        Returns
        -------
        float:
            Coulomb efficiency value.
        """
        efficiency: float = self.__electrical_props.get_coulomb_efficiency()
        return efficiency if battery_state.is_charge else 1.0 / efficiency

    def get_nominal_voltage(self) -> float:
        """
        determines the nominal voltage of the given cell type.

        Returns
        -------
        float:
            Nominal voltage in V
        """
        return self.__electrical_props.get_nominal_voltage() * self.get_serial_scale()

    def get_min_temp(self) -> float:
        """
        determines the minimal allowed operation temperature of a given cell type

        Returns
        -------
        float:
            minimal operation temperature in  K
        """
        return self.__thermal_props.get_min_temperature()

    def get_max_temp(self) -> float:
        """
        determines the maximum allowed operation temperature of a given cell type

        Returns
        -------
        float:
            maximum operation temperature in K
        """
        return self.__thermal_props.get_max_temperature()

    def get_min_voltage(self) -> float:
        """
        determines the recommended minimal operation voltage of a battery cell according to data sheet

        Returns
        -------
        float:
            minimal operation voltage in V
        """
        return self.__electrical_props.get_min_voltage() * self.get_serial_scale()

    def get_max_voltage(self) -> float:
        """
        determines the recommended maximal operation voltage of a battery cell according to data sheet

        Returns
        -------
        float:
            maximum operation voltage in V
        """
        return self.__electrical_props.get_max_voltage() * self.get_serial_scale()

    def get_min_current(self, battery_state: LithiumIonState) -> float:
        """
        determines the minimal operation current of a battery cell
        Attention: the sign of current is defined in the convention that charging current is positive and discharging
        is negative, therefore the minimal value is defined with regard to the sign.

        Parameters
        ----------
        battery_state : LithiumIonState
            Current BatteryState of the lithium_ion. Used to determine if the lithium_ion is charging or discharging
            and to get the SOC and temperature

        Returns
        -------
        float:
            minimal current in A
        """
        c_rate_limit: float = self.get_nominal_capacity() * self.__electrical_props.get_max_discharge_rate()
        voltage_limit: float = self.__LARGE_NUMBER
        if self.__consider_voltage_limit:
            try:
                voltage: float = battery_state.voltage
                rint: float = battery_state.internal_resistance
                voltage_limit: float = (voltage - self.get_min_voltage()) / rint
            except ZeroDivisionError:
                self.__log.warn('A zero division error for the internal cell resistance (Rint = 0) has been caught.')
        return -max(0.0, min(c_rate_limit, voltage_limit))

    def get_max_current(self, battery_state: LithiumIonState) -> float:
        """
        determines the maximum operation current of a battery cell
        Attention: the sign of current is defined in the convention that charging current is positive and discharging
        is negative, therefore the minimal value is defined with regard to the sign.

        Parameters
        ----------
        battery_state : LithiumIonState
            Current BatteryState of the lithium_ion. Used to determine if the lithium_ion is charging or discharging
            and to get the SOC and temperature

        Returns
        -------
        float:
            maximum current in A
        """
        c_rate_limit: float = self.get_nominal_capacity() * self.__electrical_props.get_max_charge_rate()
        voltage_limit: float = self.__LARGE_NUMBER
        if self.__consider_voltage_limit:
            try:
                voltage: float = battery_state.voltage
                rint: float = battery_state.internal_resistance
                voltage_limit: float = (self.get_max_voltage() - voltage) / rint
            except ZeroDivisionError:
                self.__log.warn('A zero division error for the internal cell resistance (Rint = 0) has been caught.')
        return max(0.0, min(c_rate_limit, voltage_limit))

    def get_self_discharge_rate(self, battery_state: LithiumIonState) -> float:
        """
        determines the self-discharge rate of battery cell

        Returns
        -------
        float:
            self-discharge rate in Wh/s
        """
        return self.__electrical_props.get_self_discharge_rate() * battery_state.soc * self.get_serial_scale() \
               * self.get_parallel_scale()

    def get_nominal_capacity(self) -> float:
        """
        Determines the capacity of the battery under nominal conditions.

        Attention: depending on the battery topology here the capacity refers possibly to that of single cell, module,
        pack and so on.

        Returns
        -------
        float:
            battery capacity in Ah
        """
        return self.__electrical_props.get_nominal_capacity() * self.get_parallel_scale()

    def get_capacity(self, battery_state: LithiumIonState) -> float:
        """
        Determines the current capacity of the battery.

        Attention: depending on the battery topology here the capacity refers possibly to that of single cell, module,
        pack and so on.

        Parameters
        ----------
        battery_state : LithiumIonState
            Current BatteryState of the lithium-ion battery. Used to determine if the avaiable capacity depending on
            C-rate and temperature, if applicable for cell type.

        Returns
        -------
        float:
            battery capacity in Ah
        """
        return self.get_nominal_capacity()

    def get_name(self) -> str:
        """
        determines the class name of a cell  (E.g. SonyLFP)

        Returns
        -------
        str:
            class name of a cell
        """

        return type(self).__name__

    def get_serial_scale(self) -> float:
        """
        determines the number of serially connected battery cells

        Returns
        -------
        float:
            number of serially connected cells
        """
        return self.__SERIAL_SCALE

    def get_parallel_scale(self) -> float:
        """
        determines the number of parallelly connected battery cells

        Returns
        -------
        float:
            number of parallelly connected cells
        """
        return self.__PARALLEL_SCALE

    def get_mass(self) -> float:
        """
        determines the mass of battery cell

        Returns
        -------
        float:
            mass in kg
        """
        return self.__thermal_props.get_mass() * self.get_serial_scale() * self.get_parallel_scale()

    def get_surface_area(self) -> float:
        """
        determines the surface area of battery cell depending on the cell geometry

        Returns
        -------
        float:
            cell surface area in m^2
        """
        return self.__cell_format.get_surface_area() * self.get_serial_scale() * self.get_parallel_scale()

    def get_specific_heat(self) -> float:
        """
        determines the specific heat capacity of a battery cell

        Returns
        -------
        float:
            specific heat capacity in J/(kg*K)
        """
        return self.__thermal_props.get_specific_heat()

    def get_convection_coefficient(self) -> float:
        """
        determines the convective heat transfer coefficient of a battery cell

        Returns
        -------
        float:
            convective heat transfer coefficient in W/(m^2*K)
        """
        return self.__thermal_props.get_convection_coefficient()

    def get_volume(self) -> float:
        return self.__cell_format.get_volume() * self.get_serial_scale() * self.get_parallel_scale()

    @abstractmethod
    def close(self) -> None:
        pass
