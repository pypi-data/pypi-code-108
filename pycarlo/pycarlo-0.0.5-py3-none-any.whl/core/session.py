import configparser
import os
import uuid
from dataclasses import dataclass, InitVar, field

import pkg_resources

from pycarlo.common import get_logger
from pycarlo.common.errors import InvalidSessionError, InvalidConfigFileError
from pycarlo.common.settings import DEFAULT_CONFIG_PATH, MCD_DEFAULT_API_ID, MCD_DEFAULT_API_TOKEN, PROFILE_FILE_NAME, \
    MCD_DEFAULT_PROFILE, DEFAULT_PROFILE_NAME, DEFAULT_MCD_API_ID_CONFIG_KEY, DEFAULT_MCD_API_TOKEN_CONFIG_KEY, \
    DEFAULT_PACKAGE_NAME

logger = get_logger(__name__)


@dataclass
class Session:
    """
    Creates an MC access session.

    Auth resolution hierarchy -
    1. Passing credentials (mcd_id & mcd_token)
    2. Environment variables (MCD_DEFAULT_API_ID & MCD_DEFAULT_API_TOKEN)
    3. Config-file by passing passing profile name (mcd_profile)
    4. Config-file by setting the profile as an environment variable (MCD_DEFAULT_PROFILE)
    5. Config-file by default profile name (default)

    Environment vars can be mixed with passed credentials, but not the config-file profile.

    The config-file path can be set via mcd_config_path.
    """
    mcd_id: InitVar[str] = None
    mcd_token: InitVar[str] = None
    mcd_profile: InitVar[str] = None
    mcd_config_path: InitVar[str] = DEFAULT_CONFIG_PATH

    id: str = field(init=False)
    token: str = field(init=False)
    session_name: str = field(init=False)

    def __post_init__(self, mcd_id: str, mcd_token: str, mcd_profile: str, mcd_config_path: str):
        self.session_name = f"python-sdk-{pkg_resources.get_distribution(DEFAULT_PACKAGE_NAME).version}-{uuid.uuid4()}"
        logger.info(f"Creating named session as '{self.session_name}'.")

        mcd_id = mcd_id or MCD_DEFAULT_API_ID
        mcd_token = mcd_token or MCD_DEFAULT_API_TOKEN
        if mcd_id and mcd_token:
            self.id = mcd_id
            self.token = mcd_token
        elif mcd_id or mcd_token:
            raise InvalidSessionError('Partially setting a session is not supported.')
        else:
            self._read_config(
                mcd_profile=mcd_profile or MCD_DEFAULT_PROFILE or DEFAULT_PROFILE_NAME,
                mcd_config_path=mcd_config_path
            )
        logger.info(f"Created session with MC API ID '{self.id}'.")

    def _read_config(self, mcd_profile: str, mcd_config_path: str) -> None:
        """
        Return configuration from section (profile name) if it exists.
        """
        config_parser = self._get_config_parser()
        file_path = os.path.join(mcd_config_path, PROFILE_FILE_NAME)
        logger.info(f"No provided connection details. Looking up session values from '{mcd_profile}' in '{file_path}'.")

        try:
            config_parser.read(file_path)
            self.id = config_parser.get(mcd_profile, DEFAULT_MCD_API_ID_CONFIG_KEY)
            self.token = config_parser.get(mcd_profile, DEFAULT_MCD_API_TOKEN_CONFIG_KEY)
        except configparser.NoSectionError:
            raise InvalidSessionError(f'Profile \'{mcd_profile}\' not found in \'{file_path}\'.')
        except Exception as err:
            raise InvalidConfigFileError from err

    @staticmethod
    def _get_config_parser() -> configparser.ConfigParser:
        """
        Gets a configparser
        """
        return configparser.ConfigParser()
