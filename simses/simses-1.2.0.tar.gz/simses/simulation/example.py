from configparser import ConfigParser

from simses.commons.config.generation.analysis import AnalysisConfigGenerator
from simses.commons.config.generation.simulation import SimulationConfigGenerator
from simses.simulation.batch_processing import BatchProcessing


class ExampleBatchProcessing(BatchProcessing):

    """
    This is just a simple example on how to use BatchProcessing.
    """

    def __init__(self):
        super().__init__(do_simulation=True, do_analysis=True)

    def _setup_config(self) -> dict:
        # Example for config setup
        config_generator: SimulationConfigGenerator = SimulationConfigGenerator()
        # example: loading default config as base (not necessary)
        config_generator.load_default_config()
        # defining parameters
        capacity: float = 5000.0
        ac_power: float = 5000.0
        voltage_ic: float = 600.0
        # generating config options
        storage_1: str = config_generator.add_generic_cell(capacity=capacity)
        storage_2: str = config_generator.add_lithium_ion_battery(capacity=capacity, cell_type='SonyLFP')
        storage_3: str = config_generator.add_lithium_ion_battery(capacity=capacity, cell_type='PanasonicNCA')
        storage_4: str = config_generator.add_lithium_ion_battery(capacity=capacity, cell_type='MolicelNMC')
        dcdc_1: str = config_generator.add_fix_efficiency_dcdc(efficiency=0.98)
        acdc_1: str = config_generator.add_fix_efficiency_acdc()
        housing_1: str = config_generator.add_no_housing()
        hvac_1: str = config_generator.add_no_hvac()
        # generating storage systems
        config_generator.clear_storage_system_ac()
        ac_system_1: str = config_generator.add_storage_system_ac(ac_power, voltage_ic, acdc_1, housing_1, hvac_1)
        config_generator.clear_storage_system_dc()
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_1)
        # printing config (if wanted)
        config_generator.show()
        # get config ready to be passed to SimSES
        config: ConfigParser = config_generator.get_config()
        # setting up multiple configurations with manual naming of simulations
        config_set: dict = dict()
        config_generator.clear_storage_system_dc()
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_1)
        config_set['storage_1'] = config_generator.get_config()
        config_generator.clear_storage_system_dc()
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_2)
        config_set['storage_2'] = config_generator.get_config()
        config_generator.clear_storage_system_dc()
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_3)
        config_set['storage_3'] = config_generator.get_config()
        config_generator.clear_storage_system_dc()
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_4)
        config_set['storage_4'] = config_generator.get_config()
        config_generator.clear_storage_system_dc()
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_1)
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_2)
        config_set['hybrid_1'] = config_generator.get_config()
        config_generator.clear_storage_system_dc()
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_3)
        config_generator.add_storage_system_dc(ac_system_1, dcdc_1, storage_4)
        config_set['hybrid_2'] = config_generator.get_config()
        return config_set

    def _analysis_config(self) -> ConfigParser:
        config_generator: AnalysisConfigGenerator = AnalysisConfigGenerator()
        config_generator.print_results(False)
        config_generator.do_plotting(True)
        return config_generator.get_config()

    def clean_up(self) -> None:
        pass


if __name__ == "__main__":
    batch_processing: BatchProcessing = ExampleBatchProcessing()
    batch_processing.run()
    batch_processing.clean_up()
