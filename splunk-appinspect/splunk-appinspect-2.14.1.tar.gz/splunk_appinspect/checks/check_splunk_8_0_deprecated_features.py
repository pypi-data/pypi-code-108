# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 8.0

The following features should not be supported in Splunk 8.0.0 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/8.0.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/latest/Installation/ChangesforSplunkappdevelopers).
"""
import logging
import os
import re

import splunk_appinspect
import splunk_appinspect.check_routine as check_routine

logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    "splunk_appinspect", "removed_feature", "ast", "splunk_8_0", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_removed_m2crypto_usage(app, reporter, target_splunk_version):
    """
    Check for the existence of the M2Crypto package usage, which is removed in the Splunk Enterprise 8.0.
    """
    # This package was removed in Splunk Enterprise 8.0 release and App shouldn't use it.
    # However, Since we don't know whether the user has packaged their own M2Crypto. We
    # only report warning once the usage is found.
    if target_splunk_version < "splunk_8_0":
        return
    reporter_output = (
        "Remove dependencies on the M2Crypto package. "
        "This package was removed in the Splunk Enterprise 8.0."
    )
    client = app.python_analyzer_client
    for file_path, ast_info in client.get_all_ast_infos():
        lines = ast_info.get_module_usage("M2Crypto", lineno_only=True)
        for line in lines:
            reporter.fail(reporter_output, file_path, line)


@splunk_appinspect.tags(
    "splunk_appinspect", "removed_feature", "splunk_8_0", "cloud", "private_app"
)
def check_for_cherry_py_custom_controller_web_conf_endpoints(
    app, reporter, target_splunk_version
):
    """Check for the existence of custom CherryPy endpoints, which must be upgraded to
    be Python 3-compatible for the Splunk Enterprise 8.0.
    """
    # Checks to see if [endpoint:*] stanzas are defined in web.conf.
    if target_splunk_version < "splunk_8_0":
        return
    config_file_paths = app.get_config_file_paths("web.conf")
    if not config_file_paths:
        reporter_output = "No web.conf file found."
        reporter.not_applicable(reporter_output)
        return
    reporter_output_a = (
        "Update custom CherryPy endpoints to be Python 3-compatible"
        " for the Splunk Enterprise 8.0. Splunk Web, which CherryPy"
        " endpoints depend on, will support only Python 3.7."
        " If you've finished your update, please disregard this message."
    )
    reporter_output_b = (
        "CherryPy endpoints are defined in web.conf but no controller file found."
        " Please provide controller file under appserver/controllers as <py_module_name>.py"
        " and make sure it's Python 3-compatible for the Splunk Enterprise 8.0."
        " Splunk Web, which CherryPy endpoints depend on, will support only Python 3.7."
        " If you've finished your update, please disregard this message."
    )
    reported_files = set()
    for directory, filename in iter(config_file_paths.items()):
        web_conf = app.web_conf(directory)
        for section in web_conf.sections():
            if section.name.startswith("endpoint:"):
                python_module_name = re.search(r"endpoint:(\w+)", section.name).group(1)
                file_path = os.path.join(
                    "appserver", "controllers", f"{python_module_name}.py"
                )
                if app.file_exists(file_path):
                    reporter_output = reporter_output_a
                else:
                    file_path = os.path.join(directory, filename)
                    reporter_output = reporter_output_b
                if file_path not in reported_files:
                    reported_files.add(file_path)
                    reporter.warn(reporter_output, file_path)


@splunk_appinspect.tags("splunk_appinspect", "splunk_8_0", "cloud", "private_app")
def check_for_existence_of_python_code_block_in_mako_template(
    app, reporter, target_splunk_version
):
    """
    Check for the existence of Python code block in Mako templates, which must be upgraded
    to be Python 3-compatible for the Splunk Enterprise 8.0.
    """
    if target_splunk_version < "splunk_8_0":
        return
    reporter_output = (
        "Update Mako templates to be Python 3-compatible."
        " Splunk Web, which Mako templates depend on, will support only Python 3.7."
        " If you've finished your update, please disregard this message."
    )
    for directory, filename, _ in app.iterate_files(types=[".html"]):
        current_file_relative_path = os.path.join(directory, filename)
        current_file_full_path = app.get_filename(directory, filename)
        if check_routine.is_mako_template(current_file_full_path):
            reporter.warn(reporter_output, current_file_relative_path)


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_3",
    "deprecated_feature",
    "advanced_xml",
    "splunk_8_0",
    "removed_feature",
    "cloud",
    "private_app",
)
@splunk_appinspect.cert_version(min="1.1.11")
def check_for_advanced_xml_module_elements(app, reporter, target_splunk_version):
    """
    Check that there is no Advanced XML, which was deprecated in Splunk Enterprise 6.3.
    """
    # Please refer to https://jira.splunk.com/browse/SPL-176582?focusedCommentId=3646334&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-3646334
    # for the logic behind this check.
    if target_splunk_version < "splunk_6_3":
        return
    if target_splunk_version < "splunk_8_0":
        finding_action, reporter_output = (
            reporter.fail,
            (
                "Module tag is found in your XML, which indicates your're using Advanced XML. "
                "Replace Advanced XML with Simple XML. "
                "Advanced XML was deprecated in Splunk Enterprise 6.3. "
            ),
        )
    else:
        finding_action, reporter_output = (
            reporter.fail,
            (
                "Module tag is found in your XML, which indicates your're using Advanced XML. "
                "Replace Advanced XML with Simple XML. "
                "Advanced XML was deprecated in Splunk Enterprise 6.3 "
                "and was removed in Splunk Enterprise 8.0."
            ),
        )
    findings = check_routine.find_xml_nodes(
        app,
        [check_routine.xml_node("module")],
        path=["default/data/ui/views", "local/data/ui/views"],
    )
    if findings is None:
        reporter.not_applicable("No xml files are found.")
        return
    try:
        has_canary_dep = app_conf_contain_stanza(
            app, "dependency:app:canary"
        ).with_option("requiredVersion")
    except Exception:
        has_canary_dep = False
    try:
        has_sideview_utils_dep = app_conf_contain_stanza(
            app, "dependency:app:sideview_utils"
        ).with_option("requiredVersion")
    except Exception:
        has_sideview_utils_dep = False
    for node_name in findings:
        for relative_filepath in findings[node_name]:
            if has_sideview_utils_dep and not has_canary_dep:
                finding_action(
                    "This app is dependent on Sideview Utils, and may not function without additional app "
                    "dependencies defined in app.conf in Splunk Enterprise 8.0 and later. "
                    "Please contact the Sideview, LLC. to learn more.",
                    relative_filepath,
                )
            elif not has_sideview_utils_dep and not has_canary_dep:
                finding_action(reporter_output, relative_filepath)


def app_conf_contain_stanza(app, stanza_name):
    """Helper function to check app conf stanza"""

    class Floater:
        """Helper class to check app conf stanza"""

        @staticmethod
        def with_option(option_name):
            """Helper method to check app conf option"""
            for dir_name in ["local", "default"]:
                # Put local ahead of default as config of app.conf in local
                # would preempt those in default.
                value = app._get_app_info(
                    stanza_name, option_name, dir_name
                )  # pylint: disable=W0212
                if value.startswith("[MISSING"):
                    continue
                return True
            return False

    return Floater()


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_4",
    "deprecated_feature",
    "web_conf",
    "splunk_8_0",
    "removed_feature",
)
@splunk_appinspect.cert_version(min="1.1.11")
def check_for_splunk_web_legacy_mode(app, reporter, target_splunk_version):
    """
    Check that Splunk Web is not in Legacy Mode, which was deprecated in Splunk Enterprise 6.4.
    """
    # Per the documentation
    # This was a temporary setting for use in specific cases where SSO would
    # break using the new mode. These issues have since been resolved, and
    # therefore this workaround is no longer needed. Switching to normal mode is
    # recommended given the performance and configuration benefits

    # appServerPorts is a comma separated list of ports
    if target_splunk_version < "splunk_6_4":
        return
    config_file_paths = app.get_config_file_paths("web.conf")
    if not config_file_paths:
        reporter_output = "No web.conf file found."
        reporter.not_applicable(reporter_output)
        return
    for directory, filename in iter(config_file_paths.items()):
        web_config_file_path = os.path.join(directory, filename)
        web_config = app.web_conf(directory)
        property_being_checked = "appServerPorts"
        for section in web_config.sections():
            all_sections_with_app_server_ports = [
                (p, v, lineno)
                for p, v, lineno in section.items()
                if p == property_being_checked
            ]

            for prop, value, lineno in all_sections_with_app_server_ports:
                if prop == property_being_checked and "0" in value.split(","):
                    if target_splunk_version < "splunk_8_0":
                        reporter_output = (
                            "Running Splunk Web in Legacy Mode by setting appServerPorts = 0 in web.conf was deprecated in Splunk Enterprise 6.4."
                            " Set it to other values, e.g., 8065."
                        )
                        reporter.fail(reporter_output, web_config_file_path, lineno)
                    else:
                        reporter_output = (
                            "Switch from legacy mode to normal mode. "
                            "Running Splunk Web in Legacy Mode by setting appServerPorts = 0 in web.conf was deprecated. "
                            "This was a temporary workaround for issues that are now resolved."
                            "Normal mode provides performance and configuration benefits."
                        )
                        reporter.fail(reporter_output, web_config_file_path, lineno)


@splunk_appinspect.tags(
    "splunk_appinspect", "deprecated_feature", "splunk_8_0", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_python_script_existence(app, reporter, target_splunk_version):
    """
    Check for the existence of Python scripts, which must be upgraded to be cross-compatible
    with Python 2 and 3 for Splunk Enterprise 8.0.
    """
    if target_splunk_version < "splunk_8_0":
        return
    count = 0
    for _, _, _ in app.iterate_files(
        types=[".py", ".py3", ".pyc", ".pyo", ".pyi", ".pyd", ".pyw", ".pyx", ".pxd"]
    ):
        count += 1
    report_output = (
        f"{count} Python files found."
        " Update these Python scripts to be cross-compatible with Python 2 and 3 for Splunk Enterprise 8.0."
        " See https://docs.splunk.com/Documentation/Splunk/latest/Python3Migration/AboutMigration for more information."
        " If you've finished your update, please disregard this message."
    )
    if count > 0:
        reporter.warn(report_output)
