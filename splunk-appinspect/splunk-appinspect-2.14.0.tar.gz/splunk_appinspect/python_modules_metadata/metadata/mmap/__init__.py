"""
Memory-mapped file objects behave like both strings and like file objects.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.MEMORY_MAPPING)
class mmap:
    """
    Maps length bytes from the file specified by the file handle fileno, and creates a mmap object.
    """

    pass
