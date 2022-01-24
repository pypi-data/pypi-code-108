# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Platform targets and claimed supported Splunk Enterprise versions
"""

import json
import logging
import os
import re

from jsoncomment.comments import json_preprocess

import splunk_appinspect

report_display_order = 6
logger = logging.getLogger(__name__)


@splunk_appinspect.tags("splunk_appinspect", "manual", "appapproval")
@splunk_appinspect.cert_version(min="1.0.0")
def check_install_on_claimed_targets(reporter):
    """Check that the app installs on all claimed target platforms."""
    reporter.manual_check("App will be checked during code review.")


@splunk_appinspect.tags("cloud", "splunk_appinspect", "self-service", "manual")
@splunk_appinspect.cert_version(min="1.5.0")
def check_setup_in_distributed_environment(app, reporter):
    """Check that the app can be setup on a distributed system after
    self-service. Warn if setup configures non-search-head features like
    inputs. This makes the app incompatible with distributed environments.
    """
    setup_view_option_found = False
    app_conf = app.app_conf()
    if app_conf.has_section("ui"):
        ui_section = app_conf.get_section("ui")
        setup_view_option_found = ui_section.has_option("setup_view")

    if app.file_exists("app.manifest"):
        reporter.not_applicable("File: app.manifest was found. Skipping this check.")

    elif app.file_exists("default/setup.xml"):
        file_path = os.path.join("default", "setup.xml")
        sp_xml = app.setup_xml()
        try:
            if sp_xml and (
                sp_xml.parse("xml").find_all(
                    "block", endpoint=re.compile(".*/inputs/.*")
                )
                or sp_xml.parse("xml").find_all(
                    "input", endpoint=re.compile(".*/inputs/.*")
                )
            ):
                reporter_output = (
                    "Inputs configuration in default/setup.xml "
                    "are not supported in distributed environments. "
                    f"File: {file_path} "
                )
                reporter.warn(reporter_output, file_path)
            else:
                reporter_output = (
                    "default/setup.xml exists, so manual setup in a distributed"
                    f" environment is required. File: {file_path}"
                )
                reporter.manual_check(reporter_output, file_path)
        except Exception as error:
            reporter_output = (
                "Failed to parse the file: default/setup.xml. This file might be formatted incorrectly."
                f"Exceptions: {str(error)}. File: {file_path}"
            )
            reporter.fail(reporter_output, file_path)

    elif setup_view_option_found:
        # there exists only one custom setup view page, so if xml, no html; otherwise, no xml
        custom_setup_name = ui_section.get_option("setup_view").value
        has_xml_file = app.file_exists(f"default/data/ui/views/{custom_setup_name}.xml")
        has_html_file = app.file_exists(
            f"default/data/ui/html/{custom_setup_name}.html"
        )
        if has_xml_file or has_html_file:
            file_path = (
                os.path.join(
                    "default", "data", "ui", "views", f"{custom_setup_name}.xml"
                )
                if has_xml_file
                else os.path.join(
                    "default", "data", "ui", "html", f"{custom_setup_name}.html"
                )
            )
            try:
                # For html setup view page, we report it as a manual check
                sp_xml = (
                    app.custom_setup_view_xml(custom_setup_name)
                    if has_xml_file
                    else None
                )
                if sp_xml and (
                    sp_xml.parse("xml").find_all(
                        "block", endpoint=re.compile(".*/inputs/.*")
                    )
                    or sp_xml.parse("xml").find_all(
                        "input", endpoint=re.compile(".*/inputs/.*")
                    )
                ):
                    reporter_output = (
                        f"Inputs configuration in default/data/ui/views/{custom_setup_name}.xml "
                        f" are not supported in distributed environments. File: {file_path}"
                    )
                    reporter.warn(reporter_output, file_path)
                else:
                    reporter_output = (
                        "Custom setup page exists, "
                        "so manual setup in a distributed environment is required. "
                        f"File: {file_path}"
                    )
                    reporter.manual_check(reporter_output, file_path)

            except Exception as error:
                reporter_output = (
                    f"Failed to parse the file: {file_path}, so it might be formatted incorrectly."
                    f"Exceptions: {str(error)}, File: {file_path}"
                )
                reporter.fail(reporter_output, file_path)
        else:
            # this checkpoint should have been covered in separate check
            file_path = os.path.join("default", "app.conf")
            reporter_output = f"Custom setup page {custom_setup_name} is not found in default/data/ui. File: {file_path}"
            reporter.fail(reporter_output, file_path)


@splunk_appinspect.tags("self-service")
@splunk_appinspect.cert_version(min="1.6.1")
def check_that_json_schema_is_applicable(app, reporter):
    """If json schema is 2.0.0 in app.manifest then warn it.
    Because schema version of 2.0.0 is not yet compatible with any versions
    of the Splunk Cloud. So far, all cloud stack are 7.0 and lower but
    Json Schema 2.0.0 is only compatible with Splunk 7.1+.
    """
    if not app.package.does_working_artifact_contain_app_manifest():
        reporter.not_applicable("app.manifest does not exist.")
        return
    app_manifest_path = os.path.join(app.package.working_app_path, "app.manifest")
    try:
        schema_version = _extract_json_schema(app_manifest_path)
    except ValueError as error:
        reporter.fail(f"Malformed app.manifest file. Json loading error: {str(error)}")
        return
    if schema_version != "1.0.0":
        reporter_output = (
            "Json Schema version of 2.0.0 is not yet compatible with any versions of the Splunk Cloud (7.0 and lower)"
            " so the app can't be SSAI. http://dev.splunk.com/view/packaging-toolkit/SP-CAAAE96#older"
            " File: app.manifest"
        )
        reporter.warn(reporter_output)


def _extract_json_schema(file_path):
    with open(file_path) as f:
        content = f.read()
        lines = content.splitlines()
        standard_json = json_preprocess(lines)
        try:
            app_manifest_content = json.loads(standard_json)
        except ValueError as json_loading_error:
            raise json_loading_error
        else:
            schema_version = app_manifest_content["schemaVersion"]
    return schema_version
