#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# This file is part of refidx
# License: GPLv3
# See the documentation at benvial.gitlab.io/refidx


try:
    # Python 3.8
    import importlib.metadata as metadata
except ImportError:
    import importlib_metadata as metadata


def get_meta(metadata):
    try:
        data = metadata.metadata("refidx")
        __version__ = metadata.version("refidx")
        __author__ = data.get("author")
        __description__ = data.get("summary")
    except Exception:
        __version__ = "unknown"
        __author__ = "unknown"
        __description__ = "unknown"
    return __version__, __author__, __description__


__version__, __author__, __description__ = get_meta(metadata)
