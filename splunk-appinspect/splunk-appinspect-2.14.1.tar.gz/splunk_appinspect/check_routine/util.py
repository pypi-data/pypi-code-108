"""
Helper module to find common object usages in app, e.g. xml node.
"""

import json
import os
import re

import bs4
from lxml import etree


class xml_node(object):
    """
    XML Node Definition
    """

    def __init__(self, name):
        self.name = name


def get_dashboard_nodes(xmlfiles):
    """
    Helper function to return SXML dashboard root nodes
    """
    findings = []
    try:
        for relative_filepath, full_filepath in xmlfiles:
            rootnode = etree.parse(full_filepath, parser=etree.XMLParser(recover=True))
            if (
                rootnode.getroot().tag == "dashboard"
                or rootnode.getroot().tag == "form"
            ):
                findings.append((rootnode.getroot(), relative_filepath))
    except Exception as exception:
        print(f"Exception while getting dashboard nodes: {exception}")

    return findings


def find_xml_nodes_usages(xml_files, nodes):
    """
    Helper function to find xml node usage
    """
    #  Outputs not_applicable if no xml files found
    findings = []
    for relative_filepath, full_filepath in xml_files:
        soup = bs4.BeautifulSoup(open(full_filepath, "rb"), "lxml-xml")
        for node in nodes:
            if hasattr(node, "attrs"):
                findings_per_file = soup.find_all(node.name, attrs=node.attrs)
            else:
                findings_per_file = soup.find_all(node.name)
            findings_per_file = [(e, relative_filepath) for e in findings_per_file]
            findings += findings_per_file
    return findings


def unpack_absolute_path(paths_tuple):
    """This function
    1. unpacks a tuple
    2. Pushes the second tuple value into an array

    @param:
    paths_tuple <Array of tuples>: Any tuple of the form (x,y)

    returns <Array>: Array of values

    Example:

    [('foo', 'bar'), ('candy', 'm&m'), ('icecream', 'chocolate')]

    returns

    ['bar', 'm&m', 'chocolate']
    """
    absolute_paths = []
    if paths_tuple is None:
        return absolute_paths

    for a, b in paths_tuple:
        absolute_paths.append(b)

    return absolute_paths


def validate_imports(  # noqa: C901
    js_files, html_files, bad_imports_set, risky_imports_set
):
    """This function returns paths of files which have require/define statements present in the bad_imports_set imports set

    @param:
    files <Array>: Array of file paths
    bad_imports_set <Set>: Set of bad file path imports
    risky_imports_set <Set>: Set of risky file path imports

    returns

    improper_files <List>: A list of objects corresponding to files with bad imports
        Example: [
            { '/file_one.js': [ { 'bad': ['bad_one'], 'risky': ['risky_one', 'risky_two'] }] },
            { '/file_two.js': [ { 'bad': ['bad_two', 'bad_three'], 'risky': ['risky_three'] }] },
            { '/file_three.html': [ { 'bad_html': ['bad_four', 'bad_five'], 'bad_risky': ['risky_four'] }] }
        ]
    """
    improper_files = []
    try:
        for filepath in js_files:
            with open(filepath, "r", encoding="utf-8") as my_file:
                matches = get_imported_matches(my_file.read())
                bad_imports_in_file = []
                risky_imports_in_file = []
                for match in matches:
                    if match in bad_imports_set:
                        bad_imports_in_file.append(match)
                    elif match in risky_imports_set:
                        risky_imports_in_file.append(match)
                identified_files = None
                if bad_imports_in_file and risky_imports_in_file:
                    identified_files = {
                        "bad": bad_imports_in_file,
                        "risky": risky_imports_in_file,
                    }
                elif bad_imports_in_file:
                    identified_files = {"bad": bad_imports_in_file}
                elif risky_imports_in_file:
                    identified_files = {"risky": risky_imports_in_file}
                if identified_files:
                    improper_files.append({filepath: identified_files})
        for filepath in html_files:
            with open(filepath, "r", encoding="utf-8") as my_file:
                matches = get_static_matches(my_file.read())
                bad_imports_in_file = []
                risky_imports_in_file = []
                for match in matches:
                    if match in bad_imports_set:
                        bad_imports_in_file.append(match)
                    elif match in risky_imports_set:
                        risky_imports_in_file.append(match)
                identified_files = None
                if bad_imports_in_file and risky_imports_in_file:
                    identified_files = {
                        "bad_html": bad_imports_in_file,
                        "risky_html": risky_imports_in_file,
                    }
                elif bad_imports_in_file:
                    identified_files = {"bad_html": bad_imports_in_file}
                elif risky_imports_in_file:
                    identified_files = {"risky_html": risky_imports_in_file}
                if identified_files:
                    improper_files.append({filepath: identified_files})
    except Exception as exception:
        print(f"Exception while validating imports {exception}")

    return improper_files


def communicate_bad_import_message(reporter, file_list):
    """This function returns paths of files which have require/define statements not present in the allowed imports set

    @param:
    reporter: <Reporter>: An object which reports messages in App Inspect
    file_list <List>: A list of objects corresponding to files with bad imports
        Example: [
            { '/file_one.js': [ { 'bad': ['bad_one'], 'risky': ['risky_one', 'risky_two'] }] },
            { '/file_two.js': [ { 'bad': ['bad_two', 'bad_three'], 'risky': ['risky_three'] }] },
            { '/file_three.html': [ { 'bad_html': ['bad_four', 'bad_five'], 'bad_risky': ['risky_four'] }] }
        ]

    returns

    None
    """
    for file_object in file_list:
        source_file = next(iter(file_object))
        identified_files = file_object[source_file]
        if "bad" in identified_files:
            bad_imports_list = identified_files["bad"]
            message = (
                "Embed all your app's front-end JS dependencies in the /appserver directory. "
                "If you import files from Splunk Web, your app might fail when Splunk Web updates "
                f"in the future. Bad imports: {bad_imports_list}"
            )
            reporter.fail(message, source_file)
        if "risky" in identified_files:
            risky_imports_list = identified_files["risky"]
            message = (
                "Embed all your app's front-end JS dependencies in the /appserver directory. "
                "If you import files from Splunk Web, your app might be at risk of failing "
                "due to the removal of files when Splunk Web updates in the future. "
                f"Risky imports: {risky_imports_list}"
            )
            reporter.warn(message, source_file)
        if "bad_html" in identified_files:
            bad_html_imports_list = identified_files["bad_html"]
            message = (
                "Embed all your app's front-end JS dependencies in the /appserver directory. "
                "If you import files from Splunk Web, your app might fail when Splunk Web updates "
                f"in the future. Bad imports (HTML): {bad_html_imports_list}"
            )
            reporter.warn(message, source_file)
        if "risky_html" in identified_files:
            risky_html_imports_list = identified_files["risky_html"]
            message = (
                "Embed all your app's front-end JS dependencies in the /appserver directory. "
                "If you import files from Splunk Web, your app might be at risk of failing "
                "due to the removal of files when Splunk Web updates in the future. "
                f"Risky imports (HTML): {risky_html_imports_list}"
            )
            reporter.warn(message, source_file)


def get_imported_matches(file):
    """Utility function that matches require js imports in a given file.

    @param
    file <String>: File path

    Returns
    matches <Array>: List of imports done by require statements

    Example:

    require(['jquery', 'underscore', 'splunkjs/mvc', 'util/console'], function ($, _, mvc, console) {
        // Do nothing
    })

    returns

    ['jquery', 'underscore', 'splunkjs/mvc', 'util/console']
    """
    matches = []
    pattern = re.compile(r"(^|[\n\r\s]+)(require|define)\([^)\]]+(\]|\))")
    for matched_object in pattern.finditer(file):
        imported_matches = re.finditer(r"['\"]([^'\"]*)['\"]", matched_object.group())
        for imported in imported_matches:
            match = imported.group(1)
            if match not in matches:
                matches.append(match)
    return matches


def parse_static_js_match(match):
    """Utility function that parses a static/js file match into a require-style import.

    @param
    file <String>: Static file path

    Returns
    matches <String>: Require-style import path

    Example:

    '/static/js/foo/bar.js'

    returns

    'foo/bar'
    """
    split_match = match.split("/static/js/")
    match = split_match[1] if len(split_match) > 1 else None
    if match and "." in match:
        return ".".join(match.split(".")[:-1])
    return None


def get_static_matches(file):
    """Utility function that matches static imports in a given file.

    @param
    file <String>: File path

    Returns
    matches <Array>: List of imports done by static loading

    Example:

    make_url('/static/js/foo/bar.js')
    make_url('/static/js/views/Base.js')

    returns

    ['foo/bar', 'views/Base']
    """
    matches = []
    pattern = re.compile(r"(make_url)\([^)]+\)")
    for matched_object in pattern.finditer(file):
        imported_matches = re.finditer(r"['\"]([^'\"]*)['\"]", matched_object.group())
        for imported in imported_matches:
            match = parse_static_js_match(imported.group(1))
            if match and match not in matches:
                matches.append(match)
    return matches


def find_xml_nodes_usages_absolute_path(xml_files, nodes):
    """Unfortunately, need to duplicate this function as we need absolute paths
    Helper function to find xml node usage
    """
    #  Outputs not_applicable if no xml files found
    findings = []
    for relative_filepath, full_filepath in xml_files:
        soup = bs4.BeautifulSoup(open(full_filepath, "rb"), "lxml-xml")
        for node in nodes:
            if hasattr(node, "attrs"):
                findings_per_file = soup.find_all(node.name, attrs=node.attrs)
            else:
                findings_per_file = soup.find_all(node.name)
            findings_per_file = [(e, full_filepath) for e in findings_per_file]
            findings += findings_per_file
    return findings


def get_spa_template_file_paths(abs_paths, spa_referenced_files):
    """This function returns intersection of Array A and B

    @param:
    abs_paths <Array>: Array of file paths
    spa_referenced_files <Array>: Array of file paths

    returns:
    final_paths <Array>: Intersection of Array A and B
    """
    final_paths = []

    for path in abs_paths:
        head, tail = os.path.split(path)  # Extract file name
        if tail in spa_referenced_files:  # filter HTML files referenced by SPA's
            final_paths.append(path)

    return final_paths


def populate_set_from_json(file_path):
    """This function take a json file object as a parameter and returns a set from the json values in the file

    @param
    file_path <file object>: JSON file object obtained from open() function

    returns

    json_set <Set>: A set of values from the json file
    """
    json_set = set()
    try:
        array_from_json = json.load(file_path)
        for i in array_from_json:
            json_set.add(i)
    except Exception as exception:
        print(f"Error while loading json to a set. {exception}")

    return json_set


def handle_multiple_scripts(scripts):
    seperated_scripts = []
    multiple_scripts = scripts.split(",")
    for script in multiple_scripts:
        seperated_scripts.append(script.strip())

    return seperated_scripts
