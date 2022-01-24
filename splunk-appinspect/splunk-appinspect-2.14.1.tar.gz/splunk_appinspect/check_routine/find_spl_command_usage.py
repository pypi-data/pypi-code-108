"""
Helper module to find splunk search command usage in app
"""

import os
import re

from . import util


def find_spl_command_usage(app, command):
    """
    Search for the SPL command usage in the following files:

    savedsearches.conf, commands.conf, macros.conf, searchbnf.conf,
    transactiontypes.conf, default/*/*.xml

    return [(<filepath>, <lineno>)...]
    """
    command = r"(^|\W)" + command + r"(\W|$)"
    findings_in_simple_xml = _find_spl_command_usage_in_simple_xml(app, command)
    checked_confs = {
        "savedsearches.conf": ["search"],
        "commands.conf": ["streaming_preop"],
        "macros.conf": ["definition"],
        "searchbnf.conf": ["syntax"],
        "transactiontypes.conf": ["search"],
        "eventtypes.conf": ["search"],
    }
    findings_in_confs = []
    for conf_filename, options in checked_confs.items():
        findings_in_conf = _find_spl_command_usage_in_conf_file(
            app, command, conf_filename, options
        )
        findings_in_confs += [
            (os.path.join("default", conf_filename), lineno)
            for lineno in findings_in_conf
        ]
    findings_in_simple_xml = [(file_path, None) for file_path in findings_in_simple_xml]
    findings = findings_in_simple_xml + findings_in_confs
    return findings


def _find_spl_command_usage_in_simple_xml(app, command):
    xml_files = list(app.get_filepaths_of_files(basedir="default", types=[".xml"]))
    nodes = [util.xml_node("query"), util.xml_node("searchString")]
    query_nodes = util.find_xml_nodes_usages(xml_files, nodes)
    findings = []
    for query_node, relative_filepath in query_nodes:
        query_string = query_node.text
        match = re.search(command, query_string)
        if match:
            findings.append(relative_filepath)
    return findings


def _find_spl_command_usage_in_conf_file(app, command, conf_filename, option_names):
    findings = []
    if not app.file_exists("default", conf_filename):
        return findings
    conf_file = app.get_config(conf_filename)
    for section_name in conf_file.section_names():
        for option_name in option_names:
            if not conf_file.has_option(section_name, option_name):
                continue
            option_value = conf_file.get(section_name, option_name)
            match = re.search(command, option_value)
            if match:
                section = conf_file.get_section(section_name)
                option_lineno = section.get_option(option_name).lineno
                findings.append(option_lineno)
    return findings
