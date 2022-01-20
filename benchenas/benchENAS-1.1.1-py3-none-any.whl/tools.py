import configparser
import os


class StatusUpdateTool(object):
    @classmethod
    def __write_ini_file(cls, alg_name, section, key, value):
        if alg_name != 'cnn_ga' and alg_name != 'nsga_net':
            config_file = os.path.join(os.path.dirname(__file__), 'algs', alg_name, 'genetic', 'global.ini')
        elif alg_name == 'cnn_ga':
            config_file = os.path.join(os.path.dirname(__file__), 'algs', alg_name, 'global.ini')
        else:
            config_file = os.path.join(os.path.dirname(__file__), 'algs', alg_name, 'utils', 'global.ini')
        config = configparser.ConfigParser()
        config.read(config_file)
        config.set(section, key, value)
        config.write(open(config_file, 'w'))

    @classmethod
    def end_evolution(cls, alg_name):
        section = 'evolution_status'
        key = 'IS_RUNNING'
        cls.__write_ini_file(alg_name, section, key, "0")