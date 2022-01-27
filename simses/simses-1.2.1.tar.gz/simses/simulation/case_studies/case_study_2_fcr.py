from configparser import ConfigParser

from simses.simulation.batch_processing import BatchProcessing


class FCRCaseStudyBatchProcessing(BatchProcessing):

    def __init__(self):
        super().__init__(do_simulation=True, do_analysis=True)

    def __generate_dc_systems(self) -> dict:
        config_set: dict = dict()
        config_set['lib_big'] = 'system_1,no_loss,lib_big\n'
        subsystems: str = ''
        for i in range(8):
            subsystems += 'system_1,fix,lib_small\n'
        config_set['lib_small'] = subsystems
        return config_set

    def __generate_ac_systems(self) -> dict:
        config_set: dict = dict()
        config_set['single'] = 'system_1,1.6e6,600,notton,no_housing,no_hvac\n'
        config_set['cascade'] = 'system_1,1.6e6,600,notton_cascade,no_housing,no_hvac\n'
        return config_set

    def _setup_config(self) -> dict:
        # generate config
        dc_systems: dict = self.__generate_dc_systems()
        ac_systems: dict = self.__generate_ac_systems()
        # setup config
        configs: dict = dict()
        for dc_name,dc_system in dc_systems.items():
            for ac_name,ac_system in ac_systems.items():
                config: ConfigParser = ConfigParser()
                config.add_section('STORAGE_SYSTEM')
                config.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_AC', ac_system)
                config.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_DC', dc_system)
                configs['simses_' + dc_name + '_' + ac_name] = config
        # print configs
        print(dc_systems)
        print('Configured ' + str(len(configs)) + ' simulations')
        return configs

    def clean_up(self) -> None:
        pass


if __name__ == "__main__":
    batch_processing: BatchProcessing = FCRCaseStudyBatchProcessing()
    batch_processing.run()
    print(type(batch_processing).__name__ + ' finished')
