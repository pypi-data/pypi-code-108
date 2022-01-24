"""
create socket connection
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)

__tags__ = [TagConsts.CRITICAL_SYSTEM_MODULE, TagConsts.NETWORK_CONNECTION]


@tags(TagConsts.NETWORK_CONNECTION)
def bind(address):
    """Bind the socket to address."""
    pass


@tags(TagConsts.NETWORK_CONNECTION)
def connect(address):
    """Connect to a remote socket at address."""
    pass


@tags(TagConsts.NETWORK_CONNECTION)
def connect_ex(address):
    """Like connect(address), but return an error indicator instead of raising an exception for errors returned by
    the C-level connect() call"""
    pass
