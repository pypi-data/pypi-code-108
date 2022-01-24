"""
Execute xml xmlreader commands
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


class XMLReader:
    """
    xml.sax.xmlreader XMLReader commands
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def parse(self):
        """
        Process an input source, like a file or a URL
        """
        pass
