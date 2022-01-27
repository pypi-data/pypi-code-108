#!/usr/bin/env python

"""Utility classes."""

from pathlib import Path
from typing import Union


def get_test_data_path(request, name) -> Path:
    """Helper method to retrieve the path of test data."""
    return Path(request.fspath).parent.joinpath("data").joinpath(name)


def get_test_data(request, klass, name, mode="rb") -> Union[bytes, str]:
    """Helper method to retrieve test data."""
    key = f"{klass}/{name}"
    result = request.config.cache.get(key, None)
    if result is None:
        path = get_test_data_path(request, name)
        with open(path, mode) as file:
            result = file.read()
            # TODO: How do we / Should we serialize binary data?
            # request.config.cache.set(key, result)
    return result
