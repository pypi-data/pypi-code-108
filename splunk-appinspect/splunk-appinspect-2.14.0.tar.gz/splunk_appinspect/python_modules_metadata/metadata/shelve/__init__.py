"""
"shelf" is a persistent, dictionary-like object.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


@tags(TagConsts.DATA_PERSISTENCE)
def open():
    """
    Open a persistent dictionary.
    """
    pass
