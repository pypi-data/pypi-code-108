# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 7.3

The following features should not be supported in Splunk 7.3 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/7.3.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/latest/Installation/ChangesforSplunkappdevelopers).
"""
import logging

import splunk_appinspect
from splunk_appinspect.check_routine import find_spl_command_usage

logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_7_3", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_tscollect_command_usage(app, reporter):
    """
    Check deprecated tscollect command usage.
    """
    reporter_output = (
        "tscollect command has been deprecated in Splunk 7.3, "
        "and might be removed in future version. "
        "The use of legacy TSIDX namespaces which reside only on the individual"
        " search head and are therefore incompatible with search head clustering"
        " has been discouraged for several releases. This feature has been superseded"
        " by datamodel, which reside on the indexer and has better performance"
        " and is accessible from any search header"
    )

    findings = find_spl_command_usage(app, "tscollect")

    for file_path, lineno in findings:
        reporter.fail(reporter_output, file_path, lineno)
