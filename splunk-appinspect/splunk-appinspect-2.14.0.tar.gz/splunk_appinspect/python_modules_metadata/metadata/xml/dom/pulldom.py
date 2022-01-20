"""
Execute xml pulldom commands, the pulldom is support for building partial DOM trees
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
def parse():
    """
    Parse a file or file-like object.
    """
    pass
