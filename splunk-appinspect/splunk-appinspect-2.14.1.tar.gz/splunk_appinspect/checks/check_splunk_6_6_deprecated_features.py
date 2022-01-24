# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated or removed features from Splunk Enterprise 6.6

The following features should not be supported in Splunk 6.6 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/6.6.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/latest/Installation/ChangesforSplunkappdevelopers).
"""
import logging
import os

import splunk_appinspect
from splunk_appinspect import check_routine

logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_6",
    "deprecated_feature",
    "ast",
    "cloud",
    "private_app",
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_app_install_endpoint(app, reporter):
    """Check apps/appinstall usages"""
    reporter_output = (
        "apps/appinstall endpoint has been deprecated in Splunk 6.6. "
        "And it might be removed entirely in a future release. An alternative could be found at"
        "https://answers.splunk.com/answers/512205/"
        "how-do-i-install-an-app-via-rest-using-the-appsloc.html#answer-512206"
    )

    kws = ["apps/appinstall"]
    regex_file_types = [".js", ".html", ".xml", ".conf"]

    for matched_file, matched_lineno in check_routine.find_endpoint_usage(
        app=app, kws=kws, regex_file_types=regex_file_types
    ):

        reporter.fail(reporter_output, matched_file, matched_lineno)


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_6", "removed_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_autolb_setting_in_outputs_conf(app, reporter, target_splunk_version):
    """
    Check removed support for setting autoLB in outputs.conf
    """
    reporter_output = (
        "Removed support for setting autoLB in outputs.conf,"
        " since autoLB can only be true, as there is no other "
        "method for forwarding data to indexers."
    )

    if target_splunk_version >= "splunk_6_6":
        if app.file_exists("default", "outputs.conf"):
            file_path = os.path.join("default", "outputs.conf")
            outputs_conf = app.outputs_conf()
            for section in outputs_conf.section_names():
                if outputs_conf.has_option(section, "autoLB"):
                    reporter.fail(
                        reporter_output,
                        file_path,
                        outputs_conf.get_section(section).get_option("autoLB").lineno,
                    )
        else:
            reporter.not_applicable("No outputs.conf file exists.")


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_6", "removed_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.1")
def check_for_displayrownumbers_in_simple_xml(app, reporter, target_splunk_version):
    """
    Check existence for displayRowNumbers option in simple xml. This option
    is no longer supported since Splunk 6.6.
    """
    # This check will examine <option name="displayRowNumbers">true</option> in simple xml.
    # There is another two uses of displayRowNumbers as the following:
    # 1:(in advanced xml)
    #      <module name="SimpleResultsTable" layoutPanel="panel_row1_col1">
    #          <param name="displayRowNumbers">False</param>
    #      </module>
    # 2:(in viewstates.conf)
    #      RowNumbers_x_x_x.displayRowNumbers = xxxx in viewstates.conf
    # However, for case 1, <module> tag is deprecated(as part of the deprecation of AXML,
    # covered by check_for_advanced_xml_module_elements). For case 2, viewstates.conf is deprecated
    # (covered by check_for_viewstates_conf).
    # Therefore, we'll omit these two cases.
    if target_splunk_version < "splunk_6_6":
        return
    reporter_output = (
        "<option> elements with the attribute [name=displayRowNumbers] was detected, "
        "which has been removed since Splunk 6.6. Please do not use it."
    )
    option_node = check_routine.xml_node("option")
    option_node.attrs = {"name": "displayRowNumbers"}
    check_routine.report_on_xml_findings(
        check_routine.find_xml_nodes(app, [option_node]),
        reporter,
        reporter_output,
        reporter.fail,
    )
