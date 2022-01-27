from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.degradation.capacity_degradation import CapacityDegradationModel
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class ConstHydrogenCurrent(CapacityDegradationModel):
    """Simplified model that considers the reduction in capacity due to a constant hydrogen current for a redox flow
    battery."""

    def __init__(self, capacity: float, stack_module: StackModule):
        super().__init__(capacity)
        self.__log: Logger = Logger(type(self).__name__)
        self.__stack_module = stack_module
        """
        In the model a hydrogen evolution current density of 5 * 10^-8 A/cm^2 is assumed. This creates a capacity 
        degradation under 1 % per year (depends on the energy to power ratio of the storage). Whitehead et al. 
        observed that for a commercial system with suitable operation parameters a capacity degradation under 1 % can 
        be achieved without additional measures like additives in the electrolyte or rebalancing cells.
        
        The hydrogen evolution data from Schweiss et al. of single cell measurements show a hydrogen evolution current 
        density around 5 * 10^-6 A/cm^2 (calculated from the hydrogen evolution rate). Values as high as this 
        overestimate the expected capacity degradation. 
        
        Literature sources: 
        Whitehead, Adam H., and Martin Harrer. "Investigation of a method to hinder charge imbalance in the vanadium 
        redox flow battery." Journal of power sources 230 (2013): 271-276.
        
        Schweiss, Ruediger, Alexander Pritzl, and Christian Meiser. "Parasitic hydrogen evolution at different carbon 
        fiber electrodes in vanadium redox flow batteries." Journal of the Electrochemical Society 163.9 (2016): A2089.        
        """
        self.__hydrogen_current_density = 5 * 10 ** -8  # A/cm^2
        self.__hydrogen_current = (self.__hydrogen_current_density * self.__stack_module.get_specific_cell_area())
        self.__log.debug('The hydrogen generation current (per cell) is: ' + str(self.__hydrogen_current))

    def get_capacity_degradation(self, time: float, redox_flow_state: RedoxFlowState):
        time_passed = time - redox_flow_state.time
        capacity_degradation = (self.__hydrogen_current * time_passed * self.__stack_module.get_nominal_voltage_cell() /
                                3600 * self.__stack_module.get_cell_per_stack() * self.__stack_module.get_serial_scale()
                                * self.__stack_module.get_parallel_scale())
        return capacity_degradation  # Wh

    def close(self):
        super().close()
        self.__log.close()
        self.__stack_module.close()
