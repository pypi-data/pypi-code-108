"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from typing import TYPE_CHECKING, Union
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.enums import NamedMetaPath
from gidapptools.utility.kwarg_dict import KwargDict

# * Type-Checking Imports --------------------------------------------------------------------------------->
if TYPE_CHECKING:
    from gidapptools.meta_data.meta_info.meta_info_item import MetaInfo
    from gidapptools.meta_data.meta_paths.meta_paths_item import MetaPaths
    meta_items_type = Union[MetaInfo, MetaPaths, object]

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class ConfigKwargs(KwargDict):

    def __init__(self, base_configuration: dict = None, **kwargs) -> None:
        self._path_overwrites: dict[NamedMetaPath, Path] = {}
        self.created_meta_items: dict[str, "meta_items_type"] = {}
        super().__init__(base_defaults=base_configuration, **kwargs)

    def _post_init(self):
        for key, value in self.data.items():
            if NamedMetaPath.is_in_value(key) is True:
                self._path_overwrites[NamedMetaPath(key)] = self.data.pop(key)

    def add_path_overwrite(self, name: Union[NamedMetaPath, str], path: Path) -> None:
        name = name if isinstance(name, NamedMetaPath) else NamedMetaPath(str(name))
        self._path_overwrites[name] = path

    def __setitem__(self, key, item) -> None:
        if key == 'path_overwrites':
            raise KeyError('Not allowed to set path_overwrites this way, use "add_path_overwrite".')
        for meta_item in self.created_meta_items.values():
            if hasattr(meta_item, key):
                raise KeyError('Not allowed to set Meta_item attributes this way, use the meta_item directly.')
        return super().__setitem__(key, item)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            for meta_item in self.created_meta_items.values():
                if hasattr(meta_item, key):
                    return getattr(meta_item, key)
            if key == 'path_overwrites':
                return self._path_overwrites
            raise


# region[Main_Exec]

if __name__ == '__main__':
    pass
# endregion[Main_Exec]
