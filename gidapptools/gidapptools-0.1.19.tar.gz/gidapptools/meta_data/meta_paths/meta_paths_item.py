"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import shutil
from pprint import pformat
from typing import Any, Union, Callable, Optional
from pathlib import Path
from tempfile import mkdtemp
from contextlib import contextmanager

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.enums import NamedMetaPath
from gidapptools.utility.helper import make_pretty
from gidapptools.utility._debug_tools import dprint
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem

print = dprint

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class MetaPaths(AbstractMetaItem):

    def __init__(self, code_base_dir: Path, paths: dict[NamedMetaPath, Path]) -> None:
        self.code_base_dir = Path(code_base_dir).resolve()
        self._paths: dict[Union[NamedMetaPath, str], Optional[Path]] = paths
        self._created_normal_paths: set[Path] = set()
        self._created_temp_dirs: set[Path] = set()

    def get_path(self, identifier: Union[NamedMetaPath, str], default: Any = NotImplemented) -> Path:
        if isinstance(identifier, str):
            try:
                identifier = NamedMetaPath(identifier)
            except ValueError:
                pass
        path = self._paths.get(identifier, None)
        if path is None:
            return default

        if path.exists() is False:
            path.mkdir(parents=True, exist_ok=True)
            self._created_normal_paths.add(path)
        return path

    @property
    def data_dir(self) -> Path:
        return self.get_path(NamedMetaPath.DATA)

    @property
    def cache_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CACHE)

    @property
    def temp_dir(self) -> Path:
        return self.get_path(NamedMetaPath.TEMP)

    @property
    def log_dir(self) -> Path:
        return self.get_path(NamedMetaPath.LOG)

    @property
    def config_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CONFIG)

    @property
    def config_spec_dir(self) -> Path:
        return self.get_path(NamedMetaPath.CONFIG_SPEC)

    @property
    def db_dir(self) -> Path:
        return self.get_path(NamedMetaPath.DB)

    def get_new_temp_dir(self, suffix: str = None, name: str = None) -> Path:
        if name is not None:
            temp_dir = self.temp_dir.joinpath(name)
        else:
            temp_dir = Path(mkdtemp(dir=self.temp_dir, suffix=suffix))
        if temp_dir.exists() is False:
            temp_dir.mkdir(parents=True, exist_ok=True)
        self._created_temp_dirs.add(temp_dir)
        return temp_dir

    @contextmanager
    def context_new_temp_dir(self, suffix: str = None):
        temp_dir = self.get_new_temp_dir(suffix=suffix)
        yield temp_dir
        shutil.rmtree(temp_dir)

    def clean_all_temp(self) -> None:
        while len(self._created_temp_dirs) != 0:
            temp_dir = self._created_temp_dirs.pop()
            shutil.rmtree(temp_dir)

    def as_dict(self, pretty: bool = False) -> dict[str, Any]:

        _out = vars(self)
        if pretty is True:
            _out = make_pretty(self)

        return pformat(_out)

    def to_storager(self, storager: Callable = None) -> None:
        if storager is None:
            return
        storager(self)

    def clean_up(self, remove_all_paths: bool = False, **kwargs) -> None:
        self.clean_all_temp()
        if remove_all_paths is True:
            for path in self._created_normal_paths:
                if path.exists():
                    if kwargs.get('dry_run', False) is True:
                        print(f"Simulating deleting of path {path.as_posix()!r}, with 'shutil.rmtree'.")
                    else:
                        shutil.rmtree(path)
        # TODO: find a way to clean shit up, but completely, also add optional kwarg that also removes the author folder


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
