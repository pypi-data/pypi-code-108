#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
This module provides an interface for reading files that use EA IFF 85 chunks.
"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
class Chunk(object):
    """
    instantiate `chunk.Chunk` class, the instance represents a chunk for file opened.
    """

    pass
