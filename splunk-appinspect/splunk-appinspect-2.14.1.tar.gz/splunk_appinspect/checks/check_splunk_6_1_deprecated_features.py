# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.1

The following features should not be supported in Splunk 6.1 or later.
"""
import splunk_appinspect
from splunk_appinspect import check_routine


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_1",
    "deprecated_feature",
    "ast",
    "cloud",
    "private_app",
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_datamodel_acceleration_endpoint_usage(app, reporter):
    """Check that deprecated datamodel/acceleration is not used.
    https://docs.splunk.com/Documentation/Splunk/6.2.0/RESTREF/RESTknowledge
    """
    kws = ["services/datamodel/acceleration"]
    report_output = (
        "From Splunk 6.1, datamodel/acceleration endpoint is deprecated. "
        "And it might be removed entirely in a future release."
        "An applicable replacement is"
        " https://answers.splunk.com/answers/326499/how-can-i-programmatically-monitor-data-model-acce.html"
    )

    regex_file_types = [".js", ".html", ".xml", ".conf"]

    for matched_file, matched_lineno in check_routine.find_endpoint_usage(
        app=app, kws=kws, regex_file_types=regex_file_types
    ):

        reporter.fail(report_output, matched_file, matched_lineno)
