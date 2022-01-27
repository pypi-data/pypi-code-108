from typing import Dict, Tuple, Any, Optional
from yaml import safe_load
from pydantic import BaseSettings, HttpUrl, FilePath
from pydantic.env_settings import SettingsSourceCallable


class Settings(BaseSettings):
    '''
    This class defines the configuration structure for the entire application.
    '''
    config_file_path: Optional[FilePath]
    data_cluster_url: HttpUrl
    running_in_data_cluster: bool = False
    management_cluster_url: HttpUrl
    client_id: str
    client_secret: str

    class Config:
        '''
        Environment configuration for loading the Settings by pydantic.
        '''
        env_prefix = 'BDK_'

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            '''
            Add the YAML loading method to the configuration sources
            '''
            config_file_path = init_settings(None)['config_file_path']
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                _yaml_config_setting(config_file_path, True),
                _yaml_config_setting('config/badook.yaml', False),
            )


class _yaml_config_setting:
    def __init__(self, config_file_path: str, throw_if_not_exists: bool) -> None:
        self.config_file_path = config_file_path
        self.throw_if_not_exists = throw_if_not_exists

    def __call__(self, _: BaseSettings) -> Dict[str, Any]:
        '''
        Read settings from a yaml source. Optionally throw an exception if the file does not exist.
        '''
        if self.config_file_path is None:
            return {}

        try:
            with open(self.config_file_path) as config_file:
                return safe_load(config_file)
        except FileNotFoundError:
            if self.throw_if_not_exists:
                raise

            return {}
