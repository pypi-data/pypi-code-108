# All imports start with an underscore, except the ones we
# want to publicly export.
import os as _os
import inspect as _inspect
import importlib as _importlib
import sys as _sys

import pandas as _pd

from terality_serde.json_encoding import (
    instantiate_pandas_arrow_extension_types as _instantiate_pandas_arrow_extension_types,
)

from .version import __version__

# Rename all imported symbols that should not be public to start with an underscore.
# (prevent a user from doing `from terality import top_level_functions` for instance).
from ._terality.terality_structures.top_level import (
    get_dynamic_top_level_attribute as _get_dynamic_top_level_attribute,
    top_level_functions as _top_level_functions,
)
from ._terality.terality_structures.ndarray import NDArray
from ._terality.terality_structures.dataframe import DataFrame
from ._terality.terality_structures.index import Index
from ._terality.terality_structures.index import Int64Index
from ._terality.terality_structures.index import Float64Index
from ._terality.terality_structures.index import DatetimeIndex
from ._terality.terality_structures.index import MultiIndex
from ._terality.terality_structures.series import Series
from ._terality.utils.anonymous import create_anonymous_user as _create_anonymous_user
from ._terality.caching import disable_cache


def __getattr__(attribute: str):
    return _get_dynamic_top_level_attribute(attribute)


def __dir__():
    # Static members.
    members = set(name for name in globals() if not name.startswith("_"))
    # Dynamic members.
    members |= _top_level_functions
    return members


# Reexport all (public) pandas submodules too.
# This is required to make importing submodules ("import terality.tseries.offsets") work.
for _attribute_name in dir(_pd):
    # Don't reexport private pandas names
    if _attribute_name.startswith("_"):
        continue
    # pandas does some magic when importing these submodules, for instance:
    #     >>> import pandas
    #     >>> from pandas import pandas as pandas_2
    #     >>> pandas_2 is pandas
    #     True
    # so let's just skip them instead of trying to work around this
    if _attribute_name in ["offsets", "pandas"]:
        continue
    _pd_attribute = getattr(_pd, _attribute_name)
    if _inspect.ismodule(_pd_attribute):
        _sys.modules[f"terality.{_attribute_name}"] = _importlib.import_module(
            f".{_attribute_name}", "pandas"
        )


_instantiate_pandas_arrow_extension_types()

# In demonstration notebooks, automatically create a temporary anonymous account.
if "TERALITY_USE_ANONYMOUS_ACCOUNT" in _os.environ:
    _create_anonymous_user()
