import os
import pydoc
import time
from centaur._.pyvmps.logger.get_logger import get_logger
from typing import types
from pathlib import Path

_logger = get_logger(__file__)


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def abs_and_normalize_path(p: str) -> str:
    if p:
        p = os.path.abspath(p)
        return os.path.normpath(p)
    return p


def get_abspath(*args):
    return os.path.abspath(os.path.join(*args))


def get_wheel_package_path(package: str) -> str:
    try:
        module: types.ModuleType = pydoc.locate(package)
        package_path = module.__path__._path[0]
        return str(Path(package_path))
    except Exception:
        _logger.exception("error getting package path")
        return ""


def current_milli_time():
    return round(time.time() * 1000)
