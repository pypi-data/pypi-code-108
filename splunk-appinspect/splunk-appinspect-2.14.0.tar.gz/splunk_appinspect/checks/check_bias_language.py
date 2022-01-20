# Copyright 2020 Splunk Inc. All rights reserved.

"""
### Bias language (static checks)
"""
import logging
import os.path
import platform

import splunk_appinspect

logger = logging.getLogger(__name__)
report_display_order = 5


@splunk_appinspect.tags("splunk_appinspect", "bias", "cloud", "private_app")
@splunk_appinspect.cert_version(min="2.3.0")
def check_for_bias_language(app, reporter):
    """Check that the app does not include any bias words."""
    if platform.system() == "Windows":
        pass
    else:
        for directory, filename, _ in app.iterate_files():
            file_path = os.path.join(directory, filename)
            for (
                line_number,
                line,
                found,
                _,
            ) in splunk_appinspect.bias.scan_file_for_bias(
                app.get_filename(directory, filename)
            ):
                formatted = line.replace(found, "<<<" + found.upper() + ">>>")
                if len(formatted) > 65:
                    formatted = formatted[:65] + "..."
                report = (
                    "Bias language is found in the app. "
                    f"{formatted} ({file_path}:{line_number}) [{found}]. "
                    f"File: {file_path}, Line: {line_number}."
                )
                reporter.warn(report, filename, line_number)
