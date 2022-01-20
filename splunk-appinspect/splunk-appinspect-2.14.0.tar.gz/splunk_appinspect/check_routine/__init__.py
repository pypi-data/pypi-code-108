"""
Common functions used by Splunk AppInspect checks
"""

import os
from collections import defaultdict

from mako.exceptions import MakoException
from mako.lexer import Lexer
from mako.parsetree import Code, TextTag

from . import util
from .find_endpoint_usage import find_endpoint_usage
from .find_spl_command_usage import find_spl_command_usage
from .util import xml_node

__all__ = [
    "blacklist_conf",
    "find_xml_nodes",
    "xml_node",
    "find_spl_command_usage",
    "find_endpoint_usage",
    "search_for_shell_command",
    "report_on_xml_findings",
]


def blacklist_conf(app, reporter_action, conf_filename, failure_reason):
    """Helper method to fail for existence of conf file.
    Args:
        app (App): App to check
        reporter (Reporter): Reporter to report FAIL or NA
        conf_filename (str): filename of conf file in default/ including extension
        reason (str): reason for notification to be passed to user if file exists
    """
    if app.file_exists("default", conf_filename):
        file_path = os.path.join("default", conf_filename)
        reporter_output = (
            f"This file is prohibited/invalid. Details: {failure_reason}."
            f" Please remove this file: {file_path}"
        )
        reporter_action(reporter_output, file_path)


def report_on_xml_findings(findings, reporter, reason, finding_action=None):
    """This function is supposed to be used following find_xml_nodes(). To peform necessary reporting
    action according to the findings.
    """
    if findings is None:
        reporter_output = "No xml files found."
        reporter.not_applicable(reporter_output)
    else:
        if finding_action is None:
            finding_action = reporter.warn
        for node_name in findings:
            for relative_filepath in findings[node_name]:
                finding_action(reason.format(node_name), relative_filepath)


def find_xml_nodes(app, nodes, path="default"):
    """Return the findings of existence of the given nodes in xmls under given paths.
    Args:
        app (App): App to check
        nodes (List[xml_node]): xml nodes to find.
        path (Union[str, list[str]]): Path or list of path to collect xml.
    Return:
        None: None xml files are found in the given path/paths
        -OR-
        Dict[str, Set[str]]:  {
                                    "module": {"default/data/ui/views/aaa.xml",}
                                }
    """
    xml_files = list(app.get_filepaths_of_files(basedir=path, types=[".xml"]))
    #  Outputs not_applicable if no xml files found
    if not xml_files:
        return None
    findings = util.find_xml_nodes_usages(xml_files, nodes)
    consolidated_findings = defaultdict(set)
    for node, relative_filepath in findings:
        consolidated_findings[node.name].add(relative_filepath)
    return consolidated_findings


def search_for_shell_command(app, reporter_action, retn_msg, cmd_pattern):
    """
    Helper function to find all shell commands in app
    """
    include_cmd_name_in_rtn_msg = False
    if "{}" in retn_msg:
        include_cmd_name_in_rtn_msg = True
    exclude = [".txt", ".md", ".org", ".csv", ".rst", ".py", ".js", ".html"]
    matches = app.search_for_patterns(cmd_pattern, excluded_types=exclude)
    for (fileref_output, match) in matches:
        filepath, line_number = fileref_output.split(":")
        if include_cmd_name_in_rtn_msg:
            retn_msg = retn_msg.format(match.group())
        reporter_action(retn_msg, filepath, line_number)


def is_mako_template(filepath):
    """
    Helper function to identify mako template
    """
    with open(filepath, "rb") as f:
        text = f.read()
        try:
            lexer = Lexer(text)
            lexer.parse()
            stack = lexer.template.nodes[:]
            while stack:
                node = stack.pop()
                if isinstance(node, Code):
                    if not isinstance(node, TextTag):
                        # A normal html Tag will be as TextTag, so we shall
                        # exclude this case.
                        return True
                if hasattr(node, "nodes"):
                    for sub_node in getattr(node, "nodes"):
                        stack.append(sub_node)
        except MakoException:
            # Mako parser raises SyntaxException when the Python code block has syntax error(s). For example, Mako
            # parser raises this exception when it finds Python 2 code block in Python 3 runtime environment.
            # Catching all Mako specific exceptions.
            return True
        except Exception:
            return False

    return False
