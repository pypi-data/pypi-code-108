# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.3

These following features should not be supported in Splunk 6.3 or later. For more, see [Deprecated features](http://docs.splunk.com/Documentation/Splunk/6.3.5/ReleaseNotes/Deprecatedfeatures#Previously_deprecated_features_that_still_work) and [Changes for Splunk App developers](http://docs.splunk.com/Documentation/Splunk/6.3.5/Installation/ChangesforSplunkappdevelopers).
"""

import logging
import os
import re

import bs4

import splunk_appinspect
from splunk_appinspect.check_routine import (
    find_xml_nodes,
    report_on_xml_findings,
    xml_node,
)
from splunk_appinspect.splunk.util import normalizeBoolean

logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_3", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.1.11")
def check_for_simple_xml_seed_element(app, reporter):
    # Warning: This may give false positives on account that it checks EVERY
    # xml file, and there may be a possibility that someone may want to use
    # the <seed> element in a totally different context. That said this isn't
    # likely to cause problems in the future.
    """Check for the deprecated `<seed>` option in Simple XML forms.
    Use the `<initialValue>` element instead.
    """
    reporter_output = "<seed> element detected. It's deprecated in Splunk 6.3. Please use <initialValue> instead."
    report_on_xml_findings(
        find_xml_nodes(app, [xml_node("seed")]),
        reporter,
        reporter_output,
        reporter.fail,
    )


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_3", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_simple_xml_search_related_element(app, reporter):
    # Warning: This may give false positives on account that it checks EVERY
    # xml file, and there may be a possibility that someone may want to use
    # these elements in a totally different context. That said this isn't
    # likely to cause problems in the future.
    """Check for the deprecated `<searchTemplate>`, `<searchString>`, `<searchName>`,
    and `<searchPostProcess>` element in Simple XML files.
    Use the `<search>` element instead.
    """
    reporter_output = "<{}> element detected. It's deprecated in Splunk 6.3. Please use <search> instead."
    findings = find_xml_nodes(
        app,
        [
            xml_node("searchTemplate"),
            xml_node("searchString"),
            xml_node("searchName"),
            xml_node("searchPostProcess"),
        ],
    )
    report_on_xml_findings(findings, reporter, reporter_output, reporter.fail)


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_3", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.1.11")
def check_for_simple_xml_option_element_with_name_previewresults(app, reporter):
    # Warning: This may give false positives on account that it checks EVERY
    # xml file, and there may be a possibility that someone may want to use
    # the <option name="previewResults"> element in a totally different context.
    # That said this isn't likely to cause problems in the future.
    """Check for the deprecated `<option name='previewResults'>` in Simple XML
    files.
    """
    reporter_output = (
        "<option> with name of previewResults has been deprecated in Splunk 6.3."
    )
    option_node = xml_node("option")
    option_node.attrs = {"name": "previewResults"}
    report_on_xml_findings(
        find_xml_nodes(app, [option_node]), reporter, reporter_output, reporter.fail
    )


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_3", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.1.11")
def check_for_simple_xml_chart_element_with_deprecated_option_names(app, reporter):
    # Warning: This may give false positives on account that it checks EVERY
    # xml file. That said this isn't likely to cause problems in the future.
    """Check for Simple XML `<chart>` panels with deprecated options
    `charting.axisLabelsY.majorTickSize` or
    `charting.axisLabelsY.majorLabelVisibility`.
    """
    attributes = [
        "charting.axisLabelsY.majorLabelVisibility",
        "charting.axisLabelsY.majorTickSize",
    ]
    attribute_regex_string = "|".join(attributes)
    attribute_regex = re.compile(attribute_regex_string)
    xml_files = list(app.get_filepaths_of_files(basedir="default", types=[".xml"]))

    #  Outputs not_applicable if no xml files found
    if not xml_files:
        reporter_output = "No xml files found."
        reporter.not_applicable(reporter_output)

    # Performs the checks
    for relative_filepath, full_filepath in xml_files:
        soup = bs4.BeautifulSoup(open(full_filepath, "rb"), "lxml-xml")
        # Get all chart elements
        chart_elements = list(soup.find_all("chart"))
        for chart_element in chart_elements:
            # Gets all child option elements of said charts, and filters out to
            # only the ones that have a name attribute with the deprecated
            # values
            option_elements = chart_element.find_all(
                "option", {"name": attribute_regex}
            )
            if option_elements:
                reporter_output = (
                    "A <chart> was detected with "
                    "options [charting.axisLabelsY.majorTickSize] or "
                    "[charting.axisLabelsY.majorLabelVisibility]. "
                    "These options have been deprecated in Splunk 6.3."
                )
                reporter.fail(reporter_output, relative_filepath)
            else:
                pass  # Do nothing, everything is fine


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_3",
    "deprecated_feature",
    "django_bindings",
    "splunk_7_3",
    "removed_feature",
    "cloud",
    "private_app",
)
@splunk_appinspect.cert_version(min="1.1.11")
def check_for_django_bindings(app, reporter, target_splunk_version):
    """Check for use of Django bindings."""
    # Checks to see that the django directory exist. If it does, then
    # django bindings are being used.
    if not target_splunk_version < "splunk_6_3":
        if app.directory_exists("django"):
            file_path = "django"
            deprecated_or_removed, splunk_version_that_feature_involved = (
                ("deprecated", "Splunk 6.3")
                if "splunk_6_3" <= target_splunk_version < "splunk_7_3"
                else ("removed", "Splunk 7.3")
            )
            reporter_output = (
                "The `django` directory was detected, which implies you're  "
                "using Django bindings feature. Django bindings has been "
                f"{deprecated_or_removed} in {splunk_version_that_feature_involved}."
            )
            reporter.fail(reporter_output, file_path)
        else:
            pass  # Do nothing, everything is fine
    else:
        pass


@splunk_appinspect.tags(
    "splunk_appinspect", "splunk_6_3", "deprecated_feature", "cloud", "private_app"
)
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_run_script_alert_action(app, reporter):
    """Check for use of running a script in alert action"""
    saved_searches = app.get_saved_searches()
    if saved_searches.configuration_file_exists():
        filepath = os.path.join("default", "savedsearches.conf")
        config_file = saved_searches.get_configuration_file()
        for section in config_file.sections():
            if not section.has_option("action.script"):
                continue
            script_option = section.get_option("action.script")
            if not normalizeBoolean(script_option.value):
                reporter_output = (
                    "Alert of running a script found in "
                    "savedsearches.conf, though it's disabled. "
                    "This feature is deprecated in Splunk 6.3 "
                    "and might be removed in the future. "
                    "Use the custom alert action framework instead."
                )
            else:
                reporter_output = (
                    "Alert of running a script found in "
                    "savedsearches.conf. This feature is deprecated "
                    "in Splunk 6.3 and might be removed in the future. "
                    "Use the custom alert action framework instead."
                )
            reporter.fail(reporter_output, filepath, script_option.lineno)

    else:
        return
