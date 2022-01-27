from configparser import ConfigParser

import pytest

from simses.commons.config.data.redox_flow import RedoxFlowDataConfig
from simses.commons.config.simulation.redox_flow import RedoxFlowConfig
from simses.commons.state.technology.redox_flow import RedoxFlowState
from simses.commons.utils.utilities import all_non_abstract_subclasses_of
from simses.technology.redox_flow.stack.abstract_stack import StackModule
from simses.technology.redox_flow.stack.cell_data_stack_5500w import CellDataStack5500W
from simses.technology.redox_flow.stack.dummy_stack_3000w import DummyStack3000W
from simses.technology.redox_flow.stack.dummy_stack_5500W import DummyStack5500W
from simses.technology.redox_flow.stack.electrolyte.abstract_electrolyte import ElectrolyteSystem
from simses.technology.redox_flow.stack.electrolyte.vanadium import VanadiumSystem
from simses.technology.redox_flow.stack.high_performance_stack_5700W import HighPerformanceStack5700W
from simses.technology.redox_flow.stack.industrial_stack_1500w import IndustrialStack1500W
from simses.technology.redox_flow.stack.industrial_stack_9000w import IndustrialStack9000W


class TestClassStackModule:

    redox_flow_state: RedoxFlowState = RedoxFlowState(0, 0)
    redox_flow_state.soc = 0.5

    def make_stack_module(self, stack_module_typ_subclass):
        voltage = 20
        power = 5000
        capacity = 10000
        config: ConfigParser = ConfigParser()
        electrolyte_system = VanadiumSystem(capacity, RedoxFlowConfig(config=config))
        if stack_module_typ_subclass.__name__ in [CellDataStack5500W.__name__, IndustrialStack1500W.__name__,
                                                  IndustrialStack9000W.__name__, HighPerformanceStack5700W.__name__]:
            return stack_module_typ_subclass(electrolyte_system, voltage, power, RedoxFlowDataConfig(),
                                             RedoxFlowConfig(config=config))
        else:
            return stack_module_typ_subclass(electrolyte_system, voltage, power, RedoxFlowConfig(config=config))
        #

    @pytest.fixture()
    def stack_module_subclass_list(self):
        # print(all_non_abstract_subclasses_of(StackModule))
        return all_non_abstract_subclasses_of(StackModule)

    def test_serial_scale_calculation(self, stack_module_subclass_list):
        for stack_module_subclass in stack_module_subclass_list:
            uut = self.make_stack_module(stack_module_subclass)
            # print(uut.get_parallel_scale(), uut.get_serial_scale())
            assert uut.get_parallel_scale() > 0
            assert uut.get_serial_scale() > 0

    def test_current_sign_check(self, stack_module_subclass_list):
        for stack_module_subclass in stack_module_subclass_list:
            uut = self.make_stack_module(stack_module_subclass)
            # print(uut.get_self_discharge_current(self.redox_flow_state))
            assert uut.get_self_discharge_current(self.redox_flow_state) > 0
