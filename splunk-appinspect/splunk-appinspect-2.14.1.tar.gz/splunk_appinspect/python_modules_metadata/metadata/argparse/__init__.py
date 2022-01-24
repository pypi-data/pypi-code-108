"""
The argparse module makes it easy to write user-friendly command-line interfaces.
"""
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    tags,
)


class ArgumentParser:
    """
    Create a new ArgumentParser object.
    """

    @tags(TagConsts.GENERIC_OPERATING_SYSTEM_SERVICES)
    def parse_args(self):
        """
        parse all arguments
        """
        pass
