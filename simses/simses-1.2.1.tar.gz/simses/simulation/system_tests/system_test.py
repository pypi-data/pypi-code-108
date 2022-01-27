import os
import shutil
import time
from configparser import ConfigParser
from simses.commons.config.abstract_config import Config
from simses.commons.config.generation.analysis import AnalysisConfigGenerator
from simses.commons.config.simulation.simulation_config import SimulationConfig
from simses.commons.utils.utilities import remove_file
from simses.simulation.batch_processing import BatchProcessing


class SystemTest(BatchProcessing):

    """
    TestBatchProcessing execute system tests for various system configurations.
    """

    __TEST_NAME: str = 'test_'
    __TEMP_FILE_ENDING: str = '.test.tmp'
    __CONFIG_EXT: str = Config.CONFIG_EXT
    __LOCAL_CONFIG_EXT: str = Config.LOCAL
    __CONFIG_PATH: str = SimulationConfig.CONFIG_PATH
    __SIMULATION_CONFIG: str = SimulationConfig.CONFIG_NAME
    __DATA_DIR: str = os.path.join(os.path.dirname(__file__), 'configs')

    __SELECTED_TESTS: [str] = list()
    """List with names of selected tests to run. If list is empty, all tests will be executed."""
    # __SELECTED_TESTS.append('test_16')
    # __SELECTED_TESTS.append('test_14')

    def __init__(self):
        super().__init__(do_simulation=True, do_analysis=True)
        # self.__id_generator = self.__get_id_generator()
        self.__tests: [str] = list()

    def _setup_config(self) -> dict:
        # test set for config setup
        self.__rename_local_config()
        configs: dict = dict()
        if not self.__SELECTED_TESTS:
            self.__add('test_0', ConfigParser(), configs)
        for file in os.listdir(self.__DATA_DIR):
            if file.endswith(self.__CONFIG_EXT):
                config: ConfigParser = ConfigParser()
                config.read(os.path.join(self.__DATA_DIR, file))
                test_id: str = file.split('.')[-2]
                if self.__SELECTED_TESTS:
                    if test_id not in self.__SELECTED_TESTS:
                        continue
                self.__add(test_id, config, configs)
        return configs

    def _analysis_config(self) -> ConfigParser:
        config_generator: AnalysisConfigGenerator = AnalysisConfigGenerator()
        config_generator.print_results(False)
        config_generator.do_plotting(False)
        config_generator.merge_analysis(False)
        return config_generator.get_config()

    def __add(self, test_id: str, config: ConfigParser, configs: dict) -> None:
        # if test_id is None:
        #     test_id: str = next(self.__id_generator)
        self.__tests.append(test_id)
        configs[test_id] = config

    def __get_id_generator(self) -> str:
        test_id: int = 1
        while True:
            yield self.__TEST_NAME + str(test_id)
            test_id += 1

    def __rename_local_config(self):
        self.__rename_local_simulation_config(self.__LOCAL_CONFIG_EXT, self.__TEMP_FILE_ENDING)

    def __reverse_local_config(self):
        self.__rename_local_simulation_config(self.__TEMP_FILE_ENDING, self.__LOCAL_CONFIG_EXT)

    def __rename_local_simulation_config(self, src_ext: str, dest_ext: str) -> None:
        # 1) Only the simulation.local.ini needs to be renamed.
        # 2) It is safer to copy a file instead of moving or renaming it.
        # 3) Only one place for logic.
        file: str = os.path.join(self.__CONFIG_PATH, self.__SIMULATION_CONFIG + src_ext)
        new_file: str = file.replace(src_ext, dest_ext)
        if os.path.exists(file):
            shutil.copy(file, new_file)
            remove_file(file)
        # for file in os.listdir(self.__CONFIG_PATH):
        #     if file.endswith(self.__LOCAL_CONFIG_EXT):
        #         new_file = file.replace(self.__LOCAL_CONFIG_EXT, self.__TEMP_FILE_ENDING)
        #         os.rename(os.path.join(self.__CONFIG_PATH, file), os.path.join(self.__CONFIG_PATH, new_file))

    # def __rename_local_configs_reverse(self) -> None:
    #     for file in os.listdir(self.__CONFIG_PATH):
    #         if file.endswith(self.__TEMP_FILE_ENDING):
    #             new_file = file.replace(self.__TEMP_FILE_ENDING, self.__LOCAL_CONFIG_EXT)
    #             os.rename(os.path.join(self.__CONFIG_PATH, file), os.path.join(self.__CONFIG_PATH, new_file))

    def clean_up(self) -> None:
        self.__reverse_local_config()
        for test in self.__tests:
            while True:
                try:
                    shutil.rmtree(os.path.join(self.get_results_path(), test))
                    break
                except FileNotFoundError:
                    break
                except PermissionError:
                    print('Waiting for simulation to finish...')
                    time.sleep(1)


if __name__ == "__main__":
    batch_processing: BatchProcessing = SystemTest()
    try:
        batch_processing.run()
    finally:
        batch_processing.clean_up()
        print('System tests Finished')
