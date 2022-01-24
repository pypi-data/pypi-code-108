#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This module provides a convenient interface to the Sun AU sound format.
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
    open file or file-like object using sunau.open(), return AU_read or AU_write objects
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def openfp():
    """
    alias for sunau.open(), open file or file-like object using sunau.openfp(),
    return AU_read or AU_write objects
    """
    pass
