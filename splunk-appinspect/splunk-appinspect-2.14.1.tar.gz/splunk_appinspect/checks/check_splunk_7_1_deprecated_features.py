# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 7.1

The following features should not be supported in Splunk 7.1 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/7.1.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/latest/Installation/ChangesforSplunkappdevelopers).
"""
import logging

import splunk_appinspect
from splunk_appinspect.check_routine import find_spl_command_usage

logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_7_1",
    "deprecated_feature",
    "splunk_7_3",
    "removed_feature",
    "cloud",
    "private_app",
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_input_command_usage(app, reporter, target_splunk_version):
    """
    Check deprecated input command usage.
    """

    if not target_splunk_version < "splunk_7_1":

        findings = find_spl_command_usage(app, r"input(\s*)(add|remove)")
        reporter_level, kw = (
            (reporter.fail, "deprecated")
            if "splunk_7_1" <= target_splunk_version < "splunk_7_3"
            else (reporter.fail, "removed")
        )

        reporter_output = (
            f"The input search command is {kw}. "
            "To add, enable, or disable inputs, "
            "use Splunk Web or edit the inputs.conf file"
        )

        for file_path, lineno in findings:
            reporter_level(reporter_output, file_path, lineno)
    else:
        pass
