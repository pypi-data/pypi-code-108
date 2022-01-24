# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.2

The following features should not be supported in Splunk 6.2 or later.
https://docs.splunk.com/Documentation/Splunk/6.2.0/ReleaseNotes/Deprecatedfeatures
"""
import re
from collections import defaultdict

import splunk_appinspect
import splunk_appinspect.check_routine.util as util
from splunk_appinspect.check_routine import (
    find_xml_nodes,
    report_on_xml_findings,
    xml_node,
)


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_2",
    "splunk_6_5",
    "deprecated_feature",
    "removed_feature",
    "cloud",
    "private_app",
)
@splunk_appinspect.cert_version(min="1.2.1")
def check_for_dashboard_xml_list_element(app, reporter, target_splunk_version):
    """Check Dashboard XML files for `<list>` element. `<list>` was deprecated in Splunk 6.2
    and removed in Splunk 6.5.
    """
    if target_splunk_version < "splunk_6_2":
        return
    if target_splunk_version < "splunk_6_5":
        reporter_output = "<list> element is detected. <list> was deprecated since Splunk 6.2. Please do not use it."
        reporter_action = reporter.fail
    else:
        reporter_output = "<list> element is detected. <list> was removed since Splunk 6.5. Please do not use it."
        reporter_action = reporter.fail

    xml_files = list(app.get_filepaths_of_files(basedir="default", types=[".xml"]))
    xml_node_list = None
    if xml_files:
        xml_node_list = defaultdict(set)

    dashboard_xml_files = []
    for node, dashboard_relative_path in util.get_dashboard_nodes(xml_files):
        for xml_file in xml_files:
            relative_path = xml_file[0]
            if dashboard_relative_path == relative_path:
                dashboard_xml_files.append(xml_file)

    found_xml_node_list = util.find_xml_nodes_usages(
        dashboard_xml_files, [xml_node("list")]
    )

    if found_xml_node_list:
        for node, relative_filepath in found_xml_node_list:
            xml_node_list[node.name].add(relative_filepath)

    report_on_xml_findings(
        xml_node_list,
        reporter,
        reporter_output,
        reporter_action,
    )


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_2", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_simple_xml_row_grouping(app, reporter, target_splunk_version):
    """Check for the deprecated grouping attribute of `row` node in Simple XML files.
    Use the `<panel>` node instead.
    """
    if target_splunk_version < "splunk_6_2":
        return
    grouping_re_obj = re.compile(r"""[0-9,"'\s]+""")
    node = xml_node("row")
    node.attrs = {"grouping": grouping_re_obj}
    finding_action, reporter_output = (
        reporter.fail,
        (
            "Detect grouping attribute of <row>, which is deprecated in Splunk 6.2. Please use "
            "the <panel> node instead."
        ),
    )
    report_on_xml_findings(
        find_xml_nodes(app, [node], path="default/data/ui/views"),
        reporter,
        reporter_output,
        finding_action,
    )


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_2", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_populating_search_element_in_dashboard_xml(app, reporter):
    """Check for the deprecated `<populatingSearch>` and `<populatingSavedSearch>` elements in dashboard XML files.
    Use the `<search>` element instead.
    """
    nodes = [xml_node("populatingSearch"), xml_node("populatingSavedSearch")]
    reporter_output = (
        "<{}> element was deprecated in Splunk 6.2 and supposed to be removed in future releases, "
        "please use the <search> element instead."
    )
    report_on_xml_findings(
        find_xml_nodes(app, nodes, path="default/data/ui/views"),
        reporter,
        reporter_output,
        reporter.fail,
    )


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_2", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_earliest_time_and_latest_time_elements_in_dashboard_xml(
    app, reporter, target_splunk_version
):
    """Check for the deprecated `<earliestTime>` and `<latestTime>` elements in dashboard XML files.
    As of version 6.2 these elements are replaced by `<earliest>` and `<latest>` elements.
    """
    if target_splunk_version < "splunk_6_2":
        return
    nodes = [xml_node("earliestTime"), xml_node("latestTime")]
    reporter_output = (
        "<{}> element was deprecated in Splunk 6.2. "
        "please use the <earliest>/<latest> element instead."
    )
    report_on_xml_findings(
        find_xml_nodes(app, nodes, path="default/data/ui/views"),
        reporter,
        reporter_output,
        reporter.fail,
    )
