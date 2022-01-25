"""
"""

# pylint: disable=protected-access
from typing import Union, Any

import datetime
from pathlib import Path
import jsonpickle as jp

from ._base_archive import BaseArchiveHandler
from ._dir_archive import DirectoryHandler
from ._pip import get_pip_freeze
from ._utils import PathType

jp.set_encoder_options("json", sort_keys=True, indent=4)


def _get_json_meta(meta=None):
    """Get the meta data for the archive"""
    jvars = dict()
    jvars["pip_freeze"] = get_pip_freeze()
    date = datetime.datetime.now()
    jvars["datestr"] = f"{date.year:4d}-{date.month:2d}-{date.day:2d}"
    jvars["timestr"] = f"{date.hour}:{date.minute}:{date.second}"
    if meta:
        jvars.update(meta)
    return jp.encode(jvars)


def ice(
    archive_handler: Union[BaseArchiveHandler, Any],
    meta: dict = None,
    **kwargs,
):
    """ice your object using the registered rules for each type cotained within the object.

    Args:
        archive_handler: Wrap the output in an archive file (tar unless zip=zip). Defaults to True.
        meta (Optional: None): Defaults to None, additional dictionary of metadata to ice to the archive.
        zip (Optional): Defaults to False.
        **kwargs: The objects to save to the archive with keys as names.

    """
    archive_handler.save(**{"meta": _get_json_meta(meta)})

    for arg, val in kwargs.items():
        freeze = jp.encode(val)
        archive_handler.save(**{arg: freeze})


def deice(file_path: PathType, classes=None) -> dict:
    """deice your archive

    Args:
        file_path: Archive file path.
        classes: Classes to deice that are not importable from the module store. Passed to jsonpickle.decode

    Returns:
        dict: A decoded dictionary of all the variables in archive.
    """
    file_path = Path(file_path)

    if file_path.is_dir():
        archive_handler = DirectoryHandler(file_path)
    else:
        raise ValueError("Cannot determine archive type for file: {}".format(file_path))

    restored = dict()

    for name, var in archive_handler.iter_json():
        restored[name] = jp.decode(var, keys=True, classes=classes)

    return restored


def list_handlers() -> dict:
    """List all the known jsonpickle handlers"""
    base = jp.handlers.registry._base_handlers
    extra = jp.handlers.registry._handlers
    return {"base": base, "extra": extra}
