#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This module provides support for reading and writing AIFF and AIFF-C files
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
    open file or file-like object using aifc.open(), return Aifc_read objects
    """
    pass
