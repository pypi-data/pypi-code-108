from configparser import ConfigParser

from simses.commons.config.data.data_config import DataConfig


class RedoxFlowDataConfig(DataConfig):

    def __init__(self, path: str = None, config: ConfigParser = None):
        super().__init__(path, config)
        self.__section: str = 'REDOX_FLOW_DATA'

    @property
    def redox_flow_data_dir(self) -> str:
        """Returns directory of redox flow data files"""
        return self.get_data_path(self.get_property(self.__section, 'REDOX_FLOW_DATA_DIR'))

    @property
    def rfb_rint_file_cell_stack(self) -> str:
        """Returns filename for internal resistance of the cell stack 5500W"""
        return self.redox_flow_data_dir + self.get_property(self.__section, 'CELL_STACK_RINT_FILE')

    @property
    def rfb_rint_file_hp_stack(self) -> str:
        """Returns filename for internal resistance of the high-performance stack 9500W"""
        return self.redox_flow_data_dir + self.get_property(self.__section, 'HIGH_PERFORMANCE_STACK_RINT_FILE')

    @property
    def redox_flow_hydrogen_evolution_dir(self) -> str:
        """Returns directory of redox flow hydrogen evolution current data files"""
        return self.get_data_path(self.get_property(self.__section, 'REDOX_FLOW_HYDROGEN_EVOLUTION_DATA'))

    @property
    def rfb_h2_evolution_schweiss_f1_file(self) -> str:
        """Returns filename for the hydrogen evolution of a RFB electrode F1 (source: Schweiss 2016)"""
        return self.redox_flow_hydrogen_evolution_dir + self.get_property(self.__section,
                                                                          'REDOX_FLOW_HYDROGEN_SCHWEISS_F1')

    @property
    def rfb_h2_evolution_schweiss_f2_file(self) -> str:
        """Returns filename for the hydrogen evolution of a RFB electrode F2 (source: Schweiss 2016)"""
        return self.redox_flow_hydrogen_evolution_dir + self.get_property(self.__section,
                                                                          'REDOX_FLOW_HYDROGEN_SCHWEISS_F2')

    @property
    def rfb_h2_evolution_schweiss_f3_file(self) -> str:
        """Returns filename for the hydrogen evolution of a RFB electrode F3 (source: Schweiss 2016)"""
        return self.redox_flow_hydrogen_evolution_dir + self.get_property(self.__section,
                                                                          'REDOX_FLOW_HYDROGEN_SCHWEISS_F3')

    @property
    def rfb_h2_evolution_schweiss_f4_file(self) -> str:
        """Returns filename for the hydrogen evolution of a RFB electrode F4 (source: Schweiss 2016)"""
        return self.redox_flow_hydrogen_evolution_dir + self.get_property(self.__section,
                                                                          'REDOX_FLOW_HYDROGEN_SCHWEISS_F4')

    @property
    def industrial_stack_1500w_shunt_current(self) -> str:
        """Returns filename for shunt current of industrial stack 1500W"""
        return self.redox_flow_data_dir + self.get_property(self.__section, 'INDUSTRIAL_STACK_1500W_SHUNT')

    @property
    def industrial_stack_9000w_shunt_current(self) -> str:
        """Returns filename for shunt current of industrial stack 9000W"""
        return self.redox_flow_data_dir + self.get_property(self.__section, 'INDUSTRIAL_STACK_9000W_SHUNT')

    @property
    def cell_stack_shunt_current(self) -> str:
        """Returns filename for shunt current of cell stack 5500W"""
        return self.redox_flow_data_dir + self.get_property(self.__section, 'CELL_STACK_SHUNT')

    @property
    def high_performance_stack_shunt(self) -> str:
        """Returns filename for shunt current of high-performance stack 9500W"""
        return self.redox_flow_data_dir + self.get_property(self.__section, 'HIGH_PERFORMANCE_STACK_SHUNT')

    @property
    def high_performance_stack_self_discharge(self) -> str:
        """Returns filename for self-discharge current of high-performance stack 9500W"""
        return self.redox_flow_data_dir + self.get_property(self.__section, 'HIGH_PERFORMANCE_STACK_SD_FILE')
