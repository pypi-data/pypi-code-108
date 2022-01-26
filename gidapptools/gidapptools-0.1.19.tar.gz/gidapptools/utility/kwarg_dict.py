"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import inspect
from abc import ABCMeta
from typing import Any, Union, Iterable, Optional
from pathlib import Path
from collections import UserDict

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import MiscEnum

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class PostInitMeta(ABCMeta):
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        instance = super(PostInitMeta, cls).__call__(*args, **kwargs)
        if hasattr(instance, "_post_init"):
            instance._post_init()
        return instance


class KwargDict(UserDict, metaclass=PostInitMeta):
    # pylint: disable=useless-super-delegation
    def __init__(self, base_defaults: dict = None, **kwargs) -> None:
        super().__init__(base_defaults, **kwargs)

    def get_kwargs_for(self, target_class: object, defaults: dict[str, Any] = None, exclude: Iterable[str] = None, overwrites: dict[str, Any] = None) -> Optional[dict[str, Any]]:
        defaults = {} if defaults is None else defaults
        overwrites = {} if overwrites is None else overwrites
        exclude = set() if exclude is None else set(exclude)
        kwarg_names = [name for name, obj in inspect.signature(target_class).parameters.items() if obj.kind is not obj.VAR_KEYWORD]

        _kwargs = {}
        for name in kwarg_names:
            if name in exclude:
                continue
            if name in overwrites:
                value = overwrites.get(name)
            else:
                value = self.get(name, defaults.get(name, MiscEnum.NOTHING))

            if value is MiscEnum.NOTHING or value is MiscEnum.OPTIONAL:
                continue
            _kwargs[name] = value
        return _kwargs

    def get_many(self, keys: Union[list[str], dict[str, Any]]) -> dict[str, Any]:
        keys = keys if isinstance(keys, dict) else {key: None for key in keys}
        result = {}
        for key in keys:
            result[key] = self.get(key, keys.get(key, None))
        return result


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
