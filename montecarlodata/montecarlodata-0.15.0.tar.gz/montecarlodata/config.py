import configparser
import os
from dataclasses import dataclass
from typing import Optional

import click

import montecarlodata.settings as settings
from montecarlodata.fs_utils import mkdirs


@dataclass
class Config:
    mcd_id: str
    mcd_token: str
    aws_profile: Optional[str] = None
    aws_region: Optional[str] = None


class ConfigManager:
    def __init__(self, profile_name: str, base_path: str, config_parser: Optional[configparser.ConfigParser] = None):
        self._profile_name = profile_name
        self._base_path = base_path
        self._profile_config_file = os.path.join(self._base_path, settings.PROFILE_FILE_NAME)

        self._config = config_parser or configparser.ConfigParser()
        self._config.read(self._profile_config_file)

    def write(self, **kwargs) -> None:
        """
        Write any configuration key value pairs to the specified section (profile name)
        """
        if self._profile_name not in self._config.sections():
            # if the section does not exist add it
            self._config.add_section(self._profile_name)

        for k, v in kwargs.items():
            self._config.set(self._profile_name, k, v)

        mkdirs(self._base_path)
        with open(self._profile_config_file, 'w') as cf:
            self._config.write(cf)

    def read(self) -> Optional[Config]:
        """
        Return configuration from section (profile name) if it exists.
        Any MCD values can be overwritten by the environment. Uses system default for AWS if not set.
        """
        try:
            return Config(
                mcd_id=settings.MCD_DEFAULT_API_ID or self._config.get(self._profile_name, 'mcd_id'),
                mcd_token=settings.MCD_DEFAULT_API_TOKEN or self._config.get(self._profile_name, 'mcd_token'),
                aws_profile=self._config.get(self._profile_name, 'aws_profile', fallback=None),
                aws_region=self._config.get(self._profile_name, 'aws_region', fallback=None)
            )
        except configparser.NoSectionError:
            click.echo(f"Failed to find configuration for '{self._profile_name}'. Please setup using 'configure' first")