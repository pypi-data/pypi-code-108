"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import platform
from enum import Enum, auto
from typing import Any
from pathlib import Path

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class BaseGidEnum(Enum):
    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, str):
            mod_value = value.casefold()
            for member_name, member_value in cls.__members__.items():
                if member_name.casefold() == mod_value or member_value == mod_value:
                    return cls(member_value)
                if isinstance(member_value, str) and member_value.casefold() == mod_value:
                    return cls(member_value)
        return super()._missing_(value)

    @classmethod
    def is_in_value(cls, other: Any) -> bool:
        return other in {member.value for name, member in cls.__members__.items()}

    def __str__(self) -> str:
        return self.name


class OperatingSystem(BaseGidEnum):
    WINDOWS = auto()
    LINUX = auto()
    MAC_OS = auto()
    JYTHON = auto()
    UNDETERMINED = auto()

    @classmethod
    @property
    def default_member(cls) -> "OperatingSystem":
        return cls.UNDETERMINED

    @classmethod
    @property
    def member_str_map(cls) -> dict[str, "OperatingSystem"]:
        return {'windows': cls.WINDOWS,
                'linux': cls.LINUX,
                'darwin': cls.MAC_OS,
                'java': cls.JYTHON}

    @classmethod
    def str_to_member(cls, os_string: str) -> "OperatingSystem":
        def _normalize_name(in_name: str) -> str:
            mod_name = in_name.casefold()
            mod_name = mod_name.strip()
            return mod_name

        return cls.member_str_map.get(_normalize_name(os_string), cls.default_member)

    @classmethod
    def determine_operating_system(cls) -> "OperatingSystem":
        os_string = platform.system()

        return cls.str_to_member(os_string)

    def __str__(self) -> str:
        return self.name


class NamedMetaPath(BaseGidEnum):
    DATA = 'user_data_dir'
    LOG = 'user_log_dir'
    CACHE = 'user_cache_dir'
    CONFIG = 'user_config_dir'
    CONFIG_SPEC = 'user_config_spec_dir'
    STATE = 'user_state_dir'
    SITE_DATA = 'site_data_dir'
    SITE_CONFIG = 'site_config_dir'
    TEMP = 'user_temp_dir'
    DB = 'database_dir'

    def __str__(self) -> str:
        return self.name


class EnvName(str, Enum):
    APP_NAME = 'APP_NAME'
    APP_AUTHOR = 'APP_AUTHOR'
    LOG_DIR = 'APP_LOG_DIR'


# region[Main_Exec]


if __name__ == '__main__':
    x = 'something'
    print(str(NamedMetaPath.DATA))

# endregion[Main_Exec]
