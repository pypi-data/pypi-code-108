"""
This module provides a simple interface to compress and decompress files just like the GNU programs gzip and gunzip would.
"""

from splunk_appinspect.python_analyzer.ast_types import AstVariable
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    executable,
    tags,
)


@tags(TagConsts.DATA_COMPRESSION)
@executable
def open(args, keywords, **kwargs):
    """construct a new GzipFile object"""
    return AstVariable(None, {"GzipFile"})
