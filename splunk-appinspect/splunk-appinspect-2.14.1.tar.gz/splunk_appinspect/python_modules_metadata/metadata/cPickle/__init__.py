"""The cPickle module supports serialization and de-serialization of Python objects, providing an interface and functionality nearly identical to the pickle module"""

from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE, TagConsts.PY2_ONLY)
def load():
    """
    Read a string from the open file object file and interpret it as a pickle data stream, reconstructing and returning the original object hierarchy.
    """
    pass


@tags(TagConsts.DATA_PERSISTENCE, TagConsts.PY2_ONLY)
def dump():
    """
    Write a pickled representation of obj to the open file object file.
    """
    pass
