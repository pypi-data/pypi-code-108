from __future__ import annotations
from typing import Union, Optional, Any, Type, TypeVar
from pathlib import Path
from logging import getLogger
from pydantic import BaseSettings, Field
from pydantic.env_settings import read_env_file


class Settings(BaseSettings):
    def __init__(self, base_dir: Union[Path, str], _env_file: Union[Path, str, None] = ..., _env_file_encoding: Optional[str] = None,
                 _secrets_dir: Union[Path, str, None] = None, **values: Any) -> None:
        super().__init__(_env_file=_env_file, _env_file_encoding=_env_file_encoding,
                         _secrets_dir=_secrets_dir, **values)
        self._base_dir = base_dir

    # EXECUTION ENVIRONMENT
    exec_env: str = Field('development', env='EXEC_ENV')

    @property
    def configuration(self):
        return self.exec_env.lower()

    # PATH
    @property
    def base_dir(self) -> str:
        return self._base_dir

    # TEST
    test_run: bool = False
    test_env_value: str = ''  # for unit test config

    # APP DETAILS
    project_name: str = 'PropZen'

    # DATABASE
    db_url: str = 'postgres://user:pass@localhost:5432/propzen'

    # MESSAGE BUS
    bus_url: str = 'amqp://localhost:5672'

    def override_with_dict(self, overrides: dict):
        def env_and_original():
            for key in self.__fields__.keys():
                env = self.__fields__[key].field_info.extra.get('env')
                yield (env or key).lower(), key
        [
            setattr(self, original, overrides[env])
            for (env, original) in env_and_original()
            if env in overrides.keys() and overrides[env] is not None
        ]

    def override_with_envfile(self, env_path: Path):
        if env_path.exists():
            overrides = read_env_file(env_path)
            self.override_with_dict(overrides)
            getLogger().info('Loaded %s environment overrides.', env_path)

    class Config:
        case_sensitive = False
        extra = 'allow'


SettingsType = TypeVar('SettingsType', bound=Settings)


def init_settings(
    base_dir: Union[Path, str],
    settings_cls: Type[SettingsType] = Settings
) -> SettingsType:

    def get_configuration_path(env_filename: str):
        return Path(base_dir, 'configurations', env_filename or '')

    default = settings_cls(
        base_dir=base_dir,
        _env_file=get_configuration_path('.env'),
        _env_file_encoding='utf-8')

    configuration = default.configuration
    env_filename = f'.env.{configuration}'

    try:
        default.override_with_envfile(
            env_path=get_configuration_path(env_filename))

        env_filename = f'.env.{configuration}.local'
        default.override_with_envfile(
            env_path=get_configuration_path(env_filename))

        env_filename = '.env.local'
        default.override_with_envfile(
            env_path=get_configuration_path(env_filename))

        default = settings_cls(
            base_dir=base_dir,
            _env_file=get_configuration_path('.env'),
            _env_file_encoding='utf-8',
            **default.dict())

    except Exception as exc:
        getLogger().exception(
            'Exception thrown when trying to load %s environment overrides.', env_filename,
            exc_info=exc
        )

    return default
