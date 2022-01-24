# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.0

The following features should not be supported in Splunk 6.0 or later.
"""
import os

import splunk_appinspect
from splunk_appinspect import check_routine


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_0", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.6.1")
def check_for_viewstates_conf(app, reporter):
    """Check that default/viewstates.conf does not exist in the app.
    (http://docs.splunk.com/Documentation/Splunk/6.0/AdvancedDev/Migration#Viewstates_are_no_longer_supported_in_simple_XML)
    """
    path = os.path.join("default", "viewstates.conf")
    if app.file_exists(path):
        reporter_output = "There exists a default/viewstates.conf which is deprecated from Splunk 6.0."
        reporter.fail(reporter_output, path)
    else:
        reporter_output = "viewstates.conf does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_0",
    "deprecated_feature",
    "splunk_7_0",
    "removed_feature",
    "cloud",
    "private_app",
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_crawl_conf_black_list(app, reporter, target_splunk_version):
    """Check that app does not contain crawl.conf as it was deprecated&removed in Splunk."""
    if "splunk_6_0" <= target_splunk_version < "splunk_7_0":
        check_routine.blacklist_conf(
            app,
            reporter.fail,
            "crawl.conf",
            "crawl.conf allows Splunk to introspect the file system, which is "
            "deprecated in Splunk 6.0 and not permitted.",
        )
    if target_splunk_version >= "splunk_7_0":
        check_routine.blacklist_conf(
            app,
            reporter.fail,
            "crawl.conf",
            "crawl.conf allows Splunk to introspect the file system, which is "
            "removed in Splunk 7.0 and not permitted.",
        )
