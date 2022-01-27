import pandas as pd
import scipy.interpolate

from simses.commons.config.data.redox_flow import RedoxFlowDataConfig
from simses.commons.log import Logger
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.technology.redox_flow.degradation.capacity_degradation import CapacityDegradationModel
from simses.technology.redox_flow.stack.abstract_stack import StackModule


class VariableHydrogenCurrent(CapacityDegradationModel):
    """Model that considers the reduction in capacity due to a hydrogen current for a redox flow battery. The hydrogen
     current is dependent on the state-of-charge."""

    def __init__(self, capacity: float, stack_module: StackModule, redox_flow_data_config: RedoxFlowDataConfig):
        super().__init__(capacity)
        self.__log: Logger = Logger(type(self).__name__)
        self.__stack_module = stack_module
        """
        The hydrogen evolution current density used in this model is based on data from Schweiss et al. for single cell 
        measurements. The values overestimate the expected capacity degradation due to hydrogen evolution. The model is 
        still in need of a published hydrogen current density of an industrial-sized stack. 
        
        In the paper of Schweiss et al. different carbon felt electrodes regarding precursor and graphitization level 
        are investigated. The hydrogen current density is dependent on the state of charge.
        F1: Carbon precursor is Rayon, traces of iron and nickel
        F2: Carbon precursor is Rayon, heat treatment above 2000 °C (Ar) and thermal surface oxidation (air, 750 °C) for
            better wettability
        F3: Carbon precursor is PAN, traces of iron and nickel
        F4: Carbon precursor is PAN, heat treatment above 2000 °C (Ar) and thermal surface oxidation (air, 750 °C) for
            better wettability
        Order of hydrogen evolution: F4 < F2 < F1 < F3
        
        Literature source: 
        Schweiss, Ruediger, Alexander Pritzl, and Christian Meiser. "Parasitic hydrogen evolution at different carbon 
        fiber electrodes in vanadium redox flow batteries." Journal of the Electrochemical Society 163.9 (2016): A2089. 
        """
        self.__HYDROGEN_EVOLUTION_CURRENT_FILE = redox_flow_data_config.rfb_h2_evolution_schweiss_f4_file
        self.__hydrogen_current_mat = pd.read_csv(self.__HYDROGEN_EVOLUTION_CURRENT_FILE)
        self.__soc_arr = self.__hydrogen_current_mat.iloc[:, 0]
        self.__i_h2 = self.__hydrogen_current_mat.iloc[:, 1]

    def get_capacity_degradation(self, time: float, redox_flow_state: RedoxFlowState):
        time_passed = time - redox_flow_state.time
        hydrogen_current = (self.__get_hydrogen_current_density(redox_flow_state) *
                            self.__stack_module.get_specific_cell_area())
        self.__log.debug('The hydrogen generation current (per cell) is: ' + str(hydrogen_current))
        capacity_degradation = (hydrogen_current * time_passed * self.__stack_module.get_nominal_voltage_cell() / 3600 *
                                self.__stack_module.get_cell_per_stack() * self.__stack_module.get_serial_scale() *
                                self.__stack_module.get_parallel_scale())
        return capacity_degradation  # Wh

    def __get_hydrogen_current_density(self, redox_flow_state: RedoxFlowState) -> float:
        """
        Determines the hydrogen evolution current from table values.

        Parameters
        ----------
        redox_flow_state : RedoxFlowState
            Current state of redox_flow.

        Returns
        -------
        float :
            Hydrogen evolution current density in A/cm^2
        """
        i_h2_interp1d = scipy.interpolate.interp1d(self.__soc_arr, self.__i_h2, kind='linear')
        hydrogen_current_density = i_h2_interp1d(redox_flow_state.soc)  # A/cm^2
        self.__log.debug('The hydrogen generation current density is: ' + str(hydrogen_current_density))
        return hydrogen_current_density

    def close(self):
        super().close()
        self.__log.close()
        self.__stack_module.close()
