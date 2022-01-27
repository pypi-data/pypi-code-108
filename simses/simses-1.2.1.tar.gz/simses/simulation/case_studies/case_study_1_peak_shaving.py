from configparser import ConfigParser

from simses.simulation.batch_processing import BatchProcessing


class PeakShavingCaseStudyBatchProcessing(BatchProcessing):

    def __init__(self):
        super().__init__(do_simulation=True, do_analysis=True)

    def __generate_dc_systems(self) -> dict:
        config_set: dict = dict()
        config_set['simses_lib_rfb'] = 'system_1,fix,lib\nsystem_1,fix,rfb\n'
        config_set['simses_lib_only'] = 'system_1,no_loss,lib_only\n'
        config_set['simses_rfb_only'] = 'system_1,no_loss,rfb_only\n'
        return config_set

    def _setup_config(self) -> dict:
        # generate config
        dc_systems: dict = self.__generate_dc_systems()
        # setup config
        configs: dict = dict()
        for name in dc_systems.keys():
            config: ConfigParser = ConfigParser()
            config.add_section('STORAGE_SYSTEM')
            config.set('STORAGE_SYSTEM', 'STORAGE_SYSTEM_DC', dc_systems[name])
            configs[name] = config
        # print configs
        print(dc_systems)
        print('Configured ' + str(len(configs)) + ' simulations')
        return configs

    def clean_up(self) -> None:
        pass


if __name__ == "__main__":
    batch_processing: BatchProcessing = PeakShavingCaseStudyBatchProcessing()
    batch_processing.run()
    print(type(batch_processing).__name__ + ' finished')
