# Copyright 2019 Splunk Inc. All rights reserved.

"""
### XML file standards
"""

import logging
import re
import xml
from xml.sax import make_parser

import bs4

import splunk_appinspect

logger = logging.getLogger(__name__)
report_display_order = 7


@splunk_appinspect.tags("splunk_appinspect", "appapproval", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.0.0")
def check_that_all_xml_files_are_well_formed(app, reporter):
    """Check that all XML files are well-formed."""
    # From Python cookbook
    # https://www.safaribooksonline.com/library/view/python-cookbook-2nd/0596007973/ch12s02.html
    def parse_xml(filename):
        parser = make_parser()
        parser.setContentHandler(xml.sax.handler.ContentHandler())
        # Include all external general (text) entities in py3
        parser.setFeature(xml.sax.handler.feature_external_ges, True)
        parser.parse(filename)

    for relative_filepath, full_filepath in app.get_filepaths_of_files(types=[".xml"]):
        try:
            parse_xml(full_filepath)
        except (xml.sax.SAXException, ValueError):
            reporter.fail(f"Invalid XML file: {relative_filepath}", relative_filepath)


@splunk_appinspect.tags("splunk_appinspect", "cloud", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_for_xml_embedded_javascript(app, reporter):
    """Check any XML files that embed JavaScript via CDATA for compliance
    with Splunk Cloud security policy.
    """
    for relative_filepath, full_filepath in app.get_filepaths_of_files(types=[".xml"]):
        soup = bs4.BeautifulSoup(
            open(full_filepath, "rb"), "html.parser", store_line_numbers=False
        )
        script_elements = soup.find_all("script")

        cdata_script_elements = [
            e
            for e in soup(text=True)
            if isinstance(e, bs4.CData) and re.search(r"<script\b", e) is not None
        ]
        script_elements.extend(cdata_script_elements)

        if script_elements:
            total_lines_of_code_output = 0
            for element in script_elements:
                element_as_string = f"{element}"
                element_content_regex = re.compile(
                    ">(.*?)<.*(?:>)", re.DOTALL | re.IGNORECASE | re.MULTILINE
                )
                content_matches = re.findall(element_content_regex, element_as_string)

                for content_match in content_matches:
                    content_match_split = content_match.splitlines()
                    total_lines_of_code_output += len(content_match_split)

            total_lines_of_code_output += len(cdata_script_elements)
            reporter_output = (
                "Embedded JavaScript has been detected."
                f" Total line(s) of code found: {total_lines_of_code_output}."
                f" File: {relative_filepath}"
            )
            reporter.manual_check(reporter_output, relative_filepath)


@splunk_appinspect.tags("splunk_appinspect", "manual")
@splunk_appinspect.cert_version(min="1.1.0")
def check_validate_no_event_handler(app, reporter):
    """Ensure that global event handlers are not used within XML files."""

    def has_global_event_handler_attribute(tag):
        global_event_handlers = [
            "onabort",
            "onblur",
            "onchange",
            "onclick",
            "onclose",
            "oncontextmenu",
            "ondblclick",
            "onerror",
            "onfocus",
            "oninput",
            "onkeydown",
            "onkeypress",
            "onkeyup",
            "onload",
            "onmousedown",
            "onmousemove",
            "onmouseout",
            "onmouseover",
            "onmouseup",
            "onpointercancel",
            "onpointerdown",
            "onpointerenter",
            "onpointerleave",
            "onpointermove",
            "onpointerout",
            "onpointerover",
            "onpointerup",
            "onreset",
            "onresize",
            "onscroll",
            "onselect",
            "onselectstart",
            "onsubmit",
            "ontouchcancel",
            "ontouchmove",
            "ontouchstart",
        ]
        for global_event_handler in global_event_handlers:
            if tag.has_attr(global_event_handler):
                return True
        return False

    for relative_filepath, full_filepath in app.get_filepaths_of_files(types=[".xml"]):
        soup = bs4.BeautifulSoup(open(full_filepath, "rb"), "lxml-xml")
        elements = soup.find_all(has_global_event_handler_attribute)
        if elements:
            elements_as_strings = [f"{element}" for element in elements]
            elements = "".join(elements_as_strings)
            reporter_output = (
                "A global event handler was detected in use."
                " Please verify that this use is valid."
                f" Elements: {elements}"
                f" File: {relative_filepath}"
            )
            reporter.manual_check(reporter_output, relative_filepath)
