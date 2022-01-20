#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This module provides a convenient interface to the WAV sound format.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
def open():
    """
    open file or file-like object using wave.open(),
    return Wave_read or Wave_write objects
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def openfp():
    """
    alias for wave.open(), open file or file-like object using wave.openfp(),
    return Wave_read or Wave_write objects
    """
    pass
