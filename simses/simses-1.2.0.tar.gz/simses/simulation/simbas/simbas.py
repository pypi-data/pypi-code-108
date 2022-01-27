from configparser import ConfigParser

from simses.commons.config.generation.analysis import AnalysisConfigGenerator
from simses.commons.config.generation.simulation import SimulationConfigGenerator
from simses.simulation.batch_processing import BatchProcessing


class SimBAS(BatchProcessing):

    """
    This is just a simple example on how to use BatchProcessing.
    """

    __CELL_CONFIG_FILE: str = 'cell_config.csv'
    __CELL_EXT: str = '.xml'

    def __init__(self):
        super().__init__(do_simulation=True, do_analysis=True)

    def _setup_config(self) -> dict:
        # Example for config setup
        config_generator: SimulationConfigGenerator = SimulationConfigGenerator()
        # example: loading default config as base (not necessary)
        config_generator.load_default_config()
        config_generator.load_local_config()
        # defining parameters
        capacity: float = 5000.0
        ac_power: float = 5000.0
        voltage_ic: float = 600.0
        # generating config options
        config_generator.clear_storage_technology()
        dcdc_1: str = config_generator.add_fix_efficiency_dcdc(efficiency=0.98)
        acdc_1: str = config_generator.add_fix_efficiency_acdc()
        housing_1: str = config_generator.add_no_housing()
        hvac_1: str = config_generator.add_no_hvac()
        # generating storage systems
        config_generator.clear_storage_system_ac()
        ac_system_1: str = config_generator.add_storage_system_ac(ac_power, voltage_ic, acdc_1, housing_1, hvac_1)
        config_generator.clear_storage_system_dc()
        # get config ready to be passed to SimSES
        config: ConfigParser = config_generator.get_config()
        # setting up multiple configurations with manual naming of simulations
        cell_config: [[str]] = self.__read_cell_config(self.__CELL_CONFIG_FILE)
        config_set: dict = dict()
        count: int = 0
        for cells in cell_config:
            config_generator.clear_storage_system_dc()
            config_generator.clear_storage_technology()
            storages: [str] = list()
            for cell in cells:
                cell_type: str = 'IseaCellType;' + cell + self.__CELL_EXT
                storages.append(config_generator.add_lithium_ion_battery(capacity=capacity, cell_type=cell_type))
            for storage in storages:
                config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage)
            count += 1
            config_set['storage_' + str(count)] = config_generator.get_config()
            # config_generator.show()
        return config_set

    def _analysis_config(self) -> ConfigParser:
        config_generator: AnalysisConfigGenerator = AnalysisConfigGenerator()
        config_generator.print_results(False)
        config_generator.do_plotting(True)
        config_generator.do_batch_analysis(True)
        return config_generator.get_config()

    def clean_up(self) -> None:
        pass

    def __read_cell_config(self, filename: str, delimiter: str = ',') -> [[str]]:
        cell_config: [[str]] = list()
        with open(filename, 'r', newline='') as file:
            for line in file:
                line: str = line.rstrip()
                if not line or line.startswith('#') or line.startswith('"'):
                    continue
                cell_config.append(line.split(delimiter))
        return cell_config


if __name__ == "__main__":
    batch_processing: BatchProcessing = SimBAS()
    batch_processing.run()
    batch_processing.clean_up()
