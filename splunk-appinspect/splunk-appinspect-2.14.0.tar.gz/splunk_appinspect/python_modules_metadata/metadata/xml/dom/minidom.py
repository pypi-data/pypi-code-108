"""
Execute xml minidom commands
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
    Parse a file into a DOM by filename or file object.
    """
    pass


class Document:
    """
    xml.dom.minidom.Document commands
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def writexml(self):
        """
        Write to file or sys.stdout and so on
        """
        pass
