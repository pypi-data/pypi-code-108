# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.5

The following features should not be supported in Splunk 6.5 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/6.5.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/latest/Installation/ChangesforSplunkappdevelopers).
"""
import logging

import splunk_appinspect
from splunk_appinspect.check_routine import (
    find_xml_nodes,
    report_on_xml_findings,
    xml_node,
)

logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_5", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.2.1")
def check_for_dashboard_xml_option_element_with_deprecated_attribute_value(
    app, reporter
):
    """Check Dashboard XML files for `<option>` element with the deprecated option value "refresh.auto.interval"
    i.e. `<option name="refresh.auto.interval">`
    """
    reporter_output = (
        "<option> elements with the attribute refresh.auto.interval was detected, "
        "which has been deprecated in Splunk 6.5."
    )
    option_node = xml_node("option")
    option_node.attrs = {"name": "refresh.auto.interval"}
    report_on_xml_findings(
        find_xml_nodes(app, [option_node]), reporter, reporter_output, reporter.fail
    )


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_5", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.2.1")
def check_for_splunk_js_header_and_footer_view(app, reporter):
    """
    Checks that views are not importing splunkjs/mvc/headerview or splunkjs/mvc/footerrview.
    These are replaced by LayoutView in Splunk 6.5.  LayoutView is not backwards compatible to Splunk 6.4 or earlier.
    Only use LayoutView if you are only targeting Splunk 6.5 or above.
    """
    library_import_pattern = ["splunkjs/mvc/headerview", "splunkjs/mvc/footerview"]
    relevant_file_types = [".js", ".html"]

    # This is a little lazy, but search for pattern doesn't return a list of
    # the files being searched, so in order to know the count I get the list of
    # iterated files and then completely ignore it if < 0
    files = list(app.get_filepaths_of_files(types=relevant_file_types))

    if not files:
        file_type = ",".join(relevant_file_types)
        reporter_output = f"No {file_type} files exist."
        reporter.not_applicable(reporter_output)
        return

    # Check starts here
    matches_found = app.search_for_patterns(
        library_import_pattern, types=relevant_file_types
    )
    for match_file_and_line, match_object in matches_found:
        match_split = match_file_and_line.rsplit(":", 1)
        match_file = match_split[0]
        match_line = match_split[1]
        reporter_output = (
            "As of Splunk 6.5, this functionality is deprecated and should be removed in future"
            f"app versions. Match: {match_object.group()} File: {match_file} Line: {match_line}"
        )
        reporter.warn(reporter_output, match_file, match_line)
