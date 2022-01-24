# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Authorize.conf file standards

Ensure that the authorize configuration file located in the **/default** folder is well formed and valid. For more, see [authorize.conf](http://docs.splunk.com/Documentation/Splunk/7.0.1/Admin/Authorizeconf).
"""
import logging
import os

import splunk_appinspect
from splunk_appinspect.splunk_defined_authorize_capability_list import (
    SPLUNK_DEFINED_CAPABILITY_NAME,
    SPLUNK_DEFINED_WINDOWS_SPECIFIC_CAPABILITY_NAME,
)

logger = logging.getLogger(__name__)


@splunk_appinspect.cert_version(min="1.5.0")
@splunk_appinspect.tags("splunk_appinspect", "cloud", "private_app")
def check_authorize_conf_capability_not_modified(app, reporter):
    """Check that authorize.conf does not contain any modified capabilities."""
    if app.file_exists("default", "authorize.conf"):
        filename = os.path.join("default", "authorize.conf")
        authorize_config = app.get_config("authorize.conf")
        for section in authorize_config.sections():
            if (
                section.name.startswith("capability::")
                and section.name
                in SPLUNK_DEFINED_CAPABILITY_NAME
                | SPLUNK_DEFINED_WINDOWS_SPECIFIC_CAPABILITY_NAME
            ):
                # ONLY fail if the custom capability stanza matches a Splunkwide capability
                lineno = section.lineno
                reporter_output = (
                    f"The following capability was modified: {section.name}. "
                    "Capabilities that exist in Splunk Cloud can not be modified. "
                    f"File: {filename}, Line: {lineno}."
                )
                reporter.fail(reporter_output, filename, lineno)
    else:
        reporter_output = "No `default/authorize.conf`file exists."
        reporter.not_applicable(reporter_output)
