"""
Execute xml ElementTree commands
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
    Loads an external XML document into this element tree.
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def iterparse():
    """
    Parses an XML section into an element tree incrementally
    """
    pass


@tags(TagConsts.FILE_READ_AND_WRITE)
def dump():
    """
    Writes an element tree or element structure to sys.stdout.  This
    function should be used for debugging only.
    """
    pass


class ElementTree:
    """
    ElementTree class
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        build xml documents and write them to files
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def parse(self):
        """
        Loads an external XML document into this element tree.
        """
        pass
