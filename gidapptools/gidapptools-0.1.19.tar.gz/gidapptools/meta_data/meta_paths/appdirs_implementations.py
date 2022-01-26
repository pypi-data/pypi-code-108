"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import Optional
from pathlib import Path
from tempfile import gettempdir

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.enums import NamedMetaPath
from gidapptools.utility.helper import PathLibAppDirs

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidAppDirs(PathLibAppDirs):

    @PathLibAppDirs.mark_path
    def user_config_dir(self) -> Path:
        config_dir = super().user_config_dir().joinpath('config')
        return config_dir

    @PathLibAppDirs.mark_path
    def user_config_spec_dir(self) -> Path:
        config_spec_dir = self.user_config_dir().joinpath('_spec')
        return config_spec_dir

    @PathLibAppDirs.mark_path
    def user_cache_dir(self) -> Path:
        cache_dir = super().user_cache_dir()
        return cache_dir.with_name(cache_dir.name.lower())

    @PathLibAppDirs.mark_path
    def user_log_dir(self) -> Path:
        log_dir = super().user_log_dir()
        return log_dir.with_name(log_dir.name.lower())

    @PathLibAppDirs.mark_path
    def user_temp_dir(self) -> Path:
        default_temp_dir = Path(gettempdir())
        app_temp_dir = default_temp_dir.joinpath(self.appname)
        return Path(str(app_temp_dir))

    @PathLibAppDirs.mark_path
    def database_dir(self) -> Path:
        return self.user_data_dir().joinpath('database')

    @classmethod
    def get_path_dict_direct(cls,
                             app_name: str,
                             app_author: str = None,
                             roaming: bool = True,
                             multipath: bool = False) -> dict[NamedMetaPath, Optional[Path]]:
        inst = cls(appname=app_name, appauthor=app_author, roaming=roaming, multipath=multipath)
        return inst.as_path_dict()


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
