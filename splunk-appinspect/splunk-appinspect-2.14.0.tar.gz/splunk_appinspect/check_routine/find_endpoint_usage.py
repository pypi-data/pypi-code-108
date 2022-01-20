"""
Helper module to find splunk search command usage in app
"""

from splunk_appinspect.python_analyzer.ast_info_query import Any, MultiOr


def find_endpoint_usage(app, kws, regex_file_types):
    """
    Search for the endpoint usage:
    1. using search_for_patterns to find endpoint usage in file types listed in regex_file_types
    2. using ast client to find endpoint usage in python files
    return [(<filepath>, <lineno>)...]
    """
    matches_found = app.search_for_patterns(kws, types=regex_file_types)
    for match_file_and_line, _ in matches_found:
        match_split = match_file_and_line.rsplit(":", 1)
        match_file = match_split[0]
        match_line = match_split[1]
        yield match_file, match_line

    client = app.python_analyzer_client
    for kw in kws:
        for file_path, ast_info in client.get_all_ast_infos():
            query = ast_info.query().call_nodes()
            query.filter(Any(ast_info.get_literal_string_usage(kw)))
            query.filter(
                MultiOr(
                    Any(ast_info.get_module_function_call_usage("urllib2", "urlopen")),
                    Any(ast_info.get_module_function_call_usage("requests", "get")),
                    Any(
                        ast_info.get_module_function_call_usage(
                            "httplib2.Http", "request"
                        )
                    ),
                )
            )
            usages = query.collect()
            for usage in usages:
                yield file_path, usage.lineno
