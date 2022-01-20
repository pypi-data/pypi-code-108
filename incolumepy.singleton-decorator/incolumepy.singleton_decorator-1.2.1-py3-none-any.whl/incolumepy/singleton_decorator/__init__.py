#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Principal Module."""
from functools import lru_cache, wraps
from pathlib import Path

import toml

configproject = Path(__file__).parents[2].joinpath("pyproject.toml")
assert configproject.is_file(), f"configproject: {configproject}"

version_file = Path(__file__).parent.joinpath("version.txt")
assert version_file.is_file(), f"version_file: {version_file}"

version_file.write_text(f"{toml.load(configproject)['tool']['poetry']['version']}\n")
__version__ = version_file.read_text().strip()


@lru_cache()
def singleton(cls):
    """Decorate for classes and definitions."""
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
