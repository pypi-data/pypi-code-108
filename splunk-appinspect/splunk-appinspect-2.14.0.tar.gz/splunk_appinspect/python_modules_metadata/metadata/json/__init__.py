"""
Handle JSON formats.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.INET_DATA_HANDLING]


@tags(TagConsts.FILE_READ_AND_WRITE)
def dump(obj, fp):
    """
    Serialize obj as a JSON formatted stream to fp.
    """
    # parameters are dummies
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def load(fp):
    """
    Deserialize fp to a Python object.
    """
    # parameter is dummy
    pass
