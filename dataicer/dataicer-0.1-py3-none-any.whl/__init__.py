from typing import Type

from .plugins.file import BaseFileHandler
from ._core import ice, deice, list_handlers
from ._base_archive import BaseArchiveHandler
from ._dir_archive import DirectoryHandler

from ._version import version as __version__

# from ._tar_archive import TarHandler
# from ._zip_archive import ZipHandler


def register_handlers(
    archive_handler: Type[BaseFileHandler], numpy=None, xarray=None, pandas=None
):
    """Register the dataicer plugin handlers for jsonpickle


    Available plugins are:
        "numpy": can
        "xarray"
        "pandas"

    Args:
        archive_handler:
        numpy: One of ["txt", "npy", "npz"]
        xarray: One of ["nc"]
        pandasL One of ["csv", "h5"]

    """
    if numpy:
        from .plugins import numpy as dinp

        dinp.register_handlers(archive_handler, numpy)

    if pandas:
        from .plugins import pandas as dipd

        dipd.register_handlers(archive_handler, pandas)

    if xarray:
        from .plugins import xarray as dixr

        dixr.register_handlers(archive_handler, xarray)
