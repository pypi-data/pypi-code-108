# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Limits.conf file standards

Ensure that **/default/limits.conf** file is omitted.

When included in the app, the **limits.conf** file changes the limits that are placed on the system for hardware use and memory consumption, which is a task that should be handled by Splunk administrators and not by Splunk app developers. For more, see [limits.conf](http://docs.splunk.com/Documentation/Splunk/latest/Admin/Limitsconf).
"""
import os

import splunk_appinspect


@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.0.0")
@splunk_appinspect.display(report_display_order=6)
def check_limits_conf(app, reporter):
    """Check that `default/limits.conf` has not been included."""
    if app.file_exists("default", "limits.conf"):
        file_path = os.path.join("default", "limits.conf")
        reporter_output = (
            "Changes to 'limits.conf' are not allowed. Hardware"
            " and memory limits should be left to Splunk"
            " Administrators. Please remove this file."
            f" File: {file_path}"
        )
        reporter.fail(reporter_output, file_path)
