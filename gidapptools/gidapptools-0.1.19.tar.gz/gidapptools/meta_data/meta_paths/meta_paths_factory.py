"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from typing import Any, Optional
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import AppNameMissingError
from gidapptools.utility.enums import EnvName, NamedMetaPath
from gidapptools.general_helper.enums import MiscEnum
from gidapptools.meta_data.config_kwargs import ConfigKwargs
from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths
from gidapptools.abstract_classes.abstract_meta_factory import AbstractMetaFactory
from gidapptools.meta_data.meta_paths.appdirs_implementations import GidAppDirs

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MetaPathsFactory(AbstractMetaFactory):
    appdirs_class = GidAppDirs
    product_class = MetaPaths
    default_configuration = {"roaming": MiscEnum.OPTIONAL, "multipath": MiscEnum.OPTIONAL}

    def __init__(self, config_kwargs: ConfigKwargs) -> None:
        super().__init__(config_kwargs=config_kwargs)
        self.code_base_dir = Path(self.config_kwargs.get('init_path')).parent

    def get_path_dict(self) -> dict[NamedMetaPath, Optional[Path]]:
        defaults = {'app_name': os.getenv(EnvName.APP_NAME),
                    'app_author': os.getenv(EnvName.APP_AUTHOR)}
        _kwargs = self.config_kwargs.get_kwargs_for(self.appdirs_class.get_path_dict_direct, defaults)
        if _kwargs.get('app_name') is None:
            raise AppNameMissingError()

        path_overwrites = self.config_kwargs.get('path_overwrites', {})
        path_dict = self.appdirs_class.get_path_dict_direct(**_kwargs)
        return path_dict | path_overwrites

    @classmethod
    @property
    def __default_configuration__(cls) -> dict[str, Any]:
        return cls.default_configuration | cls.product_class.__default_configuration__

    def setup(self) -> None:
        self.path_dict = self.get_path_dict()
        self.is_setup = True

    def _build(self) -> None:
        if self.is_setup is False:
            self.setup()
        _kwargs = self.config_kwargs.get_kwargs_for(self.product_class, defaults={'code_base_dir': self.code_base_dir, 'paths': self.path_dict})
        instance = self.product_class(**_kwargs)

        return instance


# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
