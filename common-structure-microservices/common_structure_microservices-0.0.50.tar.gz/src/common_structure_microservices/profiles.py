import yaml
from termcolor import colored

from common_structure_microservices.exception import GenericMicroserviceError


class Profiles:
    file_config = yaml.load(open('profile.yaml'), Loader=yaml.FullLoader)['django']
    APP_NAME = file_config['application']['name']
    PROFILE = file_config['profiles']['active']
    ENVIRONMENTS = f'.environments/{APP_NAME}_{PROFILE}.yml'
    APPLICATION = file_config['application']
    CONFIG = {}
    env = {}

    def get_general_env(self):
        return self.APPLICATION

    def get_specific_env(self):
        try:
            self.env = yaml.load(open(self.ENVIRONMENTS), Loader=yaml.FullLoader)['django']
            self.CONFIG = self.env['application']['config']
            print(colored('ARCHIVO DE CONFIGURACIONES -> ' + self.ENVIRONMENTS, 'green'))
        except Exception as e:
            raise GenericMicroserviceError(status=500, detail=f'ERROR CONFIG ENV: {e}')

    def get_email_env(self):
        return self.env['application']['email']

    def get_redis_env(self):
        return self.env['redis']['config']

    def get_operating_system(self):
        return self.file_config.get('operating-system')
