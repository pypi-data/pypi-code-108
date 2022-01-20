"""This module provides low-level primitives for working with multiple threads"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.THREAD_SECURITY, TagConsts.PY3_ONLY)
def start_new_thread():
    """start new thread"""
    pass
