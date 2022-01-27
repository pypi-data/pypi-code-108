from simses.commons.log import Logger
from simses.commons.state.parameters import SystemParameters
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.commons.utils.utilities import get_average_from
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.technology.lithium_ion.battery import LithiumIonBattery
from simses.technology.storage import StorageTechnology


class BatteryCircuit(StorageTechnology):
    """
    BatteryCircuit is tasked to directly connect several battery types. It handles the balancing currents between
    the batteries by equalizing the voltage difference.

    TODO

    1) Having static max / min values for current and voltage or dynamic for each battery type and state?

    -> Not needed anymore

    2) How to calculate the equilibrium balancing current between batteries?

    -> Calculate balancing current depending on OCV an internal resistence of each battery

    3) How to avoid divergency for specific LIB types? Are LIB types correctly modelled? Why do some work, others dont?
        Working: PanasonicNCA, MolicelNMC, SanyoNMC, AkasolAkmNMC;
        Not working: SonyLFP, GenericCell, AkasolOemNMC;

    -> All battery types should work

    4) Current alogrithm works better with higher capacities / lower C-Rates

    5) Right now the overall current is split between the batteries depending on their capacities. One way to a faster voltage convergence could be to only discharge the battery with higher voltage and charge only the battery with a lower voltage with the applied current.

    -> Current is split depending on OCV and internal resistance, in the same function which also calculate the balance currents

    6) During the balancing process batteries partly cannot handle the balancing current, hence it takes time for converging - in standard simulation around 30 min.

    -> If batteries can not handle the balancing current or overall current (BMS is limiting), the BMS would open the circuit breakers to protect the batterie from overcurrent.
       If this happens, the scenario is not feasable.

    """

    __LARGE_POSITIVE_NUMBER: float = 1e100
    __LARGE_NEGATIVE_NUMBER: float = -1e100

    __VOLTAGE_ACCURACY: float = 1.0
    """Acceptable voltage difference between batteries in V. Possibility of infinite loops if set too low."""

    __CURRENT_ACCURACY: float = 0.1
    """Minimum current applied to batteries in A."""

    __MAX_SLOPE: float = 1.0
    """Maximum change of current per cycle. Trade off between overshooting voltage against performance."""

    def __init__(self, batteries: [LithiumIonBattery]):
        super(BatteryCircuit, self).__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__batteries: [LithiumIonBattery] = batteries
        self.__battery_dict: dict = dict()
        self.__dc_switch_operations: dict = dict()
        self.__last_active_battery_states: dict = dict()
        for battery in batteries:
            self.__battery_dict[battery.id] = battery
            self.__dc_switch_operations[battery.id] = 0
            self.__last_active_battery_states[battery.id] = battery.state
        max_voltage: float = self.__LARGE_POSITIVE_NUMBER
        #ref_min_voltage: float = self.__LARGE_POSITIVE_NUMBER
        #ref_min_voltage: float = 0.0
        min_voltage: float = 0.0
        max_current: float = self.__LARGE_POSITIVE_NUMBER
        min_current: float = self.__LARGE_NEGATIVE_NUMBER
        for battery in batteries:
            max_voltage = min(max_voltage, battery.max_voltage)
            min_voltage = max(min_voltage, battery.min_voltage)
            max_current = min(max_current, battery.max_current)
            min_current = max(min_current, battery.min_current)
        self.__max_voltage: float = max_voltage
        self.__min_voltage: float = min_voltage
        self.__max_current: float = min(max_current, abs(min_current)) * self.__MAX_SLOPE
        self.__switch_current: bool = True

    def __get_mean_voltage(self, battery_states: dict) -> float:
        voltages: [float] = list()
        for battery_state in battery_states.values():
            battery_state: LithiumIonState = battery_state
            voltages.append(battery_state.voltage)
        return get_average_from(voltages)

    def __get_battery_current(self, battery_states: dict, battery_id: int, current: float) -> float:
        """Get the current for one Battery in a direct parallel (before DC/DC) setup"""
        upper_sum: float = 0.0
        lower_sum: float = 0.0
        for battery in battery_states.keys():
            if battery != battery_id:
                if not (battery_states[battery].internal_resistance and battery_states[battery_id].internal_resistance):
                    self.__log.error('Internal resistance of at least one direct parallel battery is 0')
                upper_sum += (battery_states[battery].voltage_open_circuit - battery_states[
                    battery_id].voltage_open_circuit) / battery_states[battery].internal_resistance
                lower_sum += battery_states[battery_id].internal_resistance / battery_states[
                    battery].internal_resistance
        return (current + upper_sum) / (1 + lower_sum)

    @staticmethod
    def __sort_by_soc(data: dict, descending: bool = False) -> dict:
        return dict(sorted(data.items(), key=lambda x: x[1].soc, reverse=descending))

    @staticmethod
    def __sort_list_by_soc(data: list, descending: bool = False) -> list:
        return sorted(data, key=lambda x: x.state.soc, reverse=descending)

    def __balance_batteries(self, time: float, current: float) -> dict:
        #self.__batteries = self.__sort_list_by_voltage(self.__batteries, False)
        local_battery_states: dict = dict()
        active_local_battery_states: dict = dict()
        for battery in self.__batteries:
            local_battery_states[battery.id] = battery.state
            # active battery states: if a direct parallel battery gets empty it disconnects from DC bus temporarily, hence gets removed from active
            active_local_battery_states[battery.id] = battery.state
        min_voltage = self.__LARGE_POSITIVE_NUMBER
        max_voltage = 0.0

        active_local_battery_states, local_battery_states = self.__filter_battery_states_by_voltage(
            active_local_battery_states, current, local_battery_states)

        loop_count: int = 0
        while abs(max_voltage - min_voltage) > self.__VOLTAGE_ACCURACY:
            loop_count += 1
            min_voltage = self.__LARGE_POSITIVE_NUMBER
            max_voltage = 0
            # First calculate the current of each individual battery
            for battery_id in active_local_battery_states.keys():
                active_local_battery_states[battery_id].current = self.__get_battery_current(
                    active_local_battery_states, battery_id, current)
                # sort back
                local_battery_states[battery_id].current = active_local_battery_states[battery_id].current
            # Second update the battery states and check for integrity
            for battery_id in local_battery_states.keys():
                battery: LithiumIonBattery = self.__battery_dict[battery_id]
                # battery_id: int = battery.id
                battery_state: LithiumIonState = battery.get_equilibrium_state_for(time, local_battery_states[
                    battery.id].current, fixed_values=True)
                # if (abs(local_battery_states[
                #             battery_id].current - battery_state.current) > self.__ACCURACY) and battery_id in active_local_battery_states:
                if (abs(battery_state.current) < self.__CURRENT_ACCURACY) and battery_id in active_local_battery_states:
                    battery_state.current = 0
                    del active_local_battery_states[battery_id]
                    local_battery_states[battery_id] = battery_state
                    self.__log.warn('Battery ' + str(battery_id) + ' was removed from active list')
                    # if bs.current != current:
                    #     self.__log.error(
                    #         'Current of a direct parallel battery was limited by the BMS and would therefore disconnect from DC-Link. Results unusable')
                    # break
                local_battery_states[battery_id] = battery_state
                if battery_id in active_local_battery_states:
                    active_local_battery_states[battery_id] = battery_state
                    max_voltage = max(max_voltage, battery_state.voltage)
                    min_voltage = min(min_voltage, battery_state.voltage)
            # Third see which current is possible
            current = 0
            for battery_id in local_battery_states.keys():
                battery_state: LithiumIonState = local_battery_states[battery_id]
                current += battery_state.current
            # Escape while loop if no more active batteries available
            if not active_local_battery_states:
                break
            if loop_count > 10000:
                print('active_local_battery_states: ',active_local_battery_states)
                print('max_voltage: ',max_voltage, 'min_voltage: ',min_voltage)
                raise Exception('Infinite loop')
            # print(max_voltage - min_voltage)
            # print(' ')
        self.__count_dc_switch_operations(local_battery_states, active_local_battery_states)
        self.__last_active_battery_states = active_local_battery_states
        return local_battery_states

    def __filter_battery_states_by_voltage(self, active_local_battery_states: dict, current, local_battery_states: dict):
        if current > 0:
            local_battery_states = self.__sort_by_soc(local_battery_states, True)
            active_local_battery_states = self.__sort_by_soc(active_local_battery_states, True)
            ref_min_voltage: float = self.__LARGE_POSITIVE_NUMBER
            for battery_id in local_battery_states.keys():
                ref_min_voltage = min(ref_min_voltage, local_battery_states[battery_id].voltage)
            for battery_id in local_battery_states.keys():
                if abs(ref_min_voltage - active_local_battery_states[battery_id].voltage) > self.__VOLTAGE_ACCURACY:
                    local_battery_states[battery_id].current = 0
                    del active_local_battery_states[battery_id]
        else:
            local_battery_states = self.__sort_by_soc(local_battery_states, False)
            active_local_battery_states = self.__sort_by_soc(active_local_battery_states, False)
            ref_max_voltage: float = 0.0
            for battery_id in local_battery_states.keys():
                ref_max_voltage = max(ref_max_voltage, local_battery_states[battery_id].voltage)
            for battery_id in local_battery_states.keys():
                if abs(ref_max_voltage - active_local_battery_states[battery_id].voltage) > self.__VOLTAGE_ACCURACY:
                    local_battery_states[battery_id].current = 0
                    del active_local_battery_states[battery_id]
        return active_local_battery_states, local_battery_states

    def __count_dc_switch_operations(self, local_battery_states: dict, active_local_battery_states: dict) -> None:
        last_active_battery_ids = self.__last_active_battery_states.keys()
        current_active_battery_ids = active_local_battery_states.keys()
        for battery_id in local_battery_states.keys():
            if (battery_id in current_active_battery_ids and battery_id not in last_active_battery_ids) or \
                    (battery_id not in current_active_battery_ids and battery_id in last_active_battery_ids):
                self.__dc_switch_operations[battery_id] += 1

    def distribute_and_run(self, time: float, current: float, voltage: float) -> None:
        local_battery_states: dict = self.__balance_batteries(time, current)
        for battery in self.__batteries:
            # TODO improve current distribution to batteries, interface to OparaBatt (Philipp Jocher)
            # 1st approach: equal distribution of current
            # lithium_ion.set(time, current / size)
            # 2nd approach: current distribution is voltage dependent (OCV + RINT)
            battery_state: LithiumIonState = local_battery_states[battery.id]
            battery.distribute_and_run(time, battery_state.current, battery_state.voltage)
            # 3rd approach: Jaehyung Lee, A novel li-ion lithium_ion pack modeling considerging single cell
            #     information and capacity variation, https://doi.org/10.1109/ECCE.2017.8096880

    def wait(self) -> None:
        pass

    def get_auxiliaries(self) -> [Auxiliary]:
        auxiliaries: [Auxiliary] = list()
        for battery in self.__batteries:
            auxiliaries.extend(battery.get_auxiliaries())
        return auxiliaries

    @property
    def volume(self) -> float:
        volume = 0
        for battery in self.__batteries:
            volume += battery.volume
        return volume

    @property
    def mass(self) -> float:
        mass = 0
        for battery in self.__batteries:
            mass += battery.mass
        return mass

    @property
    def surface_area(self) -> float:
        surface_area = 0
        for battery in self.__batteries:
            surface_area += battery.surface_area
        return surface_area

    @property
    def specific_heat(self) -> float:
        specific_heat = 0
        for battery in self.__batteries:
            specific_heat += battery.specific_heat
        return specific_heat / len(self.__batteries)

    @property
    def convection_coefficient(self) -> float:
        convection_coefficient = 0
        for battery in self.__batteries:
            convection_coefficient += battery.convection_coefficient
        return convection_coefficient / len(self.__batteries)

    def get_system_parameters(self) -> dict:
        parameters: dict = dict()
        batteries: list = list()
        for battery in self.__batteries:
            batteries.append(battery.get_system_parameters())
        parameters[SystemParameters.BATTERIES] = batteries
        return parameters

    @property
    def state(self) -> LithiumIonState:
        battery_states: [LithiumIonState] = list()
        for battery in self.__batteries:
            battery_states.append(battery.state)
        return LithiumIonState.sum_parallel(battery_states)

    def close(self) -> None:
        """Closing all resources in lithium_ion circuit"""
        print("DC switch operations for parallel connected batteries", self.__dc_switch_operations)
        self.__log.close()
        for battery in self.__batteries:
            battery.close()
