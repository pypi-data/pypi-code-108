import sys

from fsos.bucket_manager import (
    make_bucket,
    remove_bucket,
    bucket_exists,
    bucket_list,
    put_filepath,
    get_filepaths,
    get_objects,
)

this = sys.modules[__name__]
this._FSOS_DB = None

__all__ = ["fsos"]
__version__ = "0.0.1"
