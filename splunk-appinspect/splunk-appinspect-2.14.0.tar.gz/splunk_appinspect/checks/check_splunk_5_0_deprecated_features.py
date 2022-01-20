# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 5.0

The following features should not be supported in Splunk 5.0 or later.
"""
import os

import splunk_appinspect
from splunk_appinspect.check_routine import find_spl_command_usage


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_5_0", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_savedsearches_used_in_eventtypes_conf(app, reporter):
    """Check that saved searches are not used within event types.
    https://docs.splunk.com/Documentation/Splunk/5.0/ReleaseNotes/Deprecatedfeatures
    https://docs.splunk.com/Documentation/Splunk/7.2.5/Knowledge/Abouteventtypes
    """
    path = os.path.join("default", "eventtypes.conf")
    if app.file_exists(path):
        eventtypes_conf = app.eventtypes_conf()
        for section in eventtypes_conf.sections():
            for setting in section.settings():
                if setting.name == "search" and "| savedsearch " in setting.value:
                    reporter.fail(
                        "Detect saved search used within event types. "
                        "Saved search in event types is deprecated in Splunk 5.0. "
                        "Pleas specify search terms for the event type.",
                        "default/eventtypes.conf",
                        setting.lineno,
                    )
    else:
        reporter_output = "eventtypes.conf does not exist."
        reporter.not_applicable(reporter_output)


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_5_0", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.0")
def check_deprecated_eventtype_autodiscovering(app, reporter):
    """Check that app does not use findtypes command. This command was for eventtype
    auto-discovering, which is deprecated in Splunk 5.0.
    """
    reporter_output = (
        "Detect usage of <findtypes> command. This command was for eventtype "
        "auto-discovering, which is deprecated in Splunk 5.0. Please do not use it."
    )
    usages = find_spl_command_usage(app, "findtypes")
    for file_path, lineno in usages:
        reporter.fail(reporter_output, file_path, lineno)
