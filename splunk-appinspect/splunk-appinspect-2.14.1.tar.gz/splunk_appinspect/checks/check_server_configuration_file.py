# Copyright 2016 - 2019 Splunk Inc. All rights reserved.

"""
### Server configuration file standards

Ensure that server.conf is well formed and valid.
For detailed information about the server configuration file, see [server.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Serverconf).
"""
import logging
import os

import splunk_appinspect

report_display_order = 2
logger = logging.getLogger(__name__)


@splunk_appinspect.tags("cloud", "private_app")
@splunk_appinspect.cert_version(min="1.6.1")
def check_server_conf_only_contains_custom_conf_sync_stanzas_or_diag_stanza(
    app, reporter
):
    r"""Check that server.conf in an app is only allowed to contain:
    1) conf_replication_include.\<custom_conf_files\> in \[shclustering\] stanza
    2) or EXCLUDE-\<class\> property in \[diag\] stanza
    """
    server_conf_existed = False
    for directory in ["default", "local"]:
        if app.file_exists(directory, "server.conf"):
            server_conf_existed = True
            file_path = os.path.join(directory, "server.conf")

            server_config = app.server_conf()

            for section in server_config.sections():
                if section.name == "shclustering":
                    _check_disallow_settings(
                        reporter, file_path, section, r"conf_replication_include\..*"
                    )
                elif section.name == "diag":
                    _check_disallow_settings(reporter, file_path, section, "EXCLUDE-.*")
                else:
                    reporter_output = (
                        f"Stanza `[{section.name}]` configures Splunk server "
                        "settings and is not permitted in Splunk Cloud. "
                        f"File: {file_path}, Line: {section.lineno}."
                    )
                    reporter.fail(reporter_output, file_path, section.lineno)

    if not server_conf_existed:
        reporter_output = "No server.conf file exists."
        reporter.not_applicable(reporter_output)


def _check_disallow_settings(reporter, file_path, section, allowed_settings_pattern):
    all_setting_names = [s.name for s in section.settings()]
    allowed_setting_names = _get_setting_names_with_key_pattern(
        section, allowed_settings_pattern
    )
    disallowed_settings = _get_disallowed_settings(
        all_setting_names, allowed_setting_names
    )
    if disallowed_settings:
        reporter_output = (
            f"Only {allowed_settings_pattern} properties are allowed "
            f"for `[{section.name}]` stanza. The properties "
            f"{disallowed_settings} are not allowed in this stanza. "
            f"File: {file_path}, Line: {section.lineno}"
        )
        reporter.fail(reporter_output, file_path, section.lineno)


def _get_setting_names_with_key_pattern(section, pattern):
    return [s.name for s in section.settings_with_key_pattern(pattern)]


def _get_disallowed_settings(setting_names, allowed_settings):
    return set(setting_names).difference(set(allowed_settings))
