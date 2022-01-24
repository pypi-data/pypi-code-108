"""
Helper module to provide search ability for components in parsed AST syntax tree
"""
from collections import defaultdict
from functools import partial

from splunk_appinspect.python_analyzer.ast_types import AstVariable


def _get_args(call_node, ast_info):
    args = []
    for variable in [ast_info.get_variable_details(node) for node in call_node.args]:
        if variable is not None and AstVariable.is_string(variable):
            args.append(variable.variable_value)
        else:
            args.append("?")
    return args


def _get_keyword_dict(call_node, ast_info):
    keyword_dict = {}
    for keyword in call_node.keywords:
        variable = ast_info.get_variable_details(keyword.value)
        if variable is not None and AstVariable.is_string(variable):
            keyword_dict[keyword.arg] = variable.variable_value
        else:
            keyword_dict[keyword.arg] = "?"

    return keyword_dict


def _convert_to_result_dict(
    node, ast_info=None, line_number_only=True, get_func_params=False
):
    result = {"node": node, "line_number": node.lineno}
    if get_func_params:
        result["args"] = _get_args(node, ast_info)
        result["keywords"] = _get_keyword_dict(node, ast_info)
    return result


class AstSearcher(object):
    """
    Helper class to provide search ability for components in parsed AST syntax tree
    """

    def __init__(self, analyzer_client):
        self.analyzer_client = analyzer_client

    def search(
        self,
        components,
        node_filter=None,
        search_module_usage=False,
        line_number_only=True,
        get_func_params=False,
        check_name=None,
    ):
        """
        Search the given components in the abstract syntax tree and return the files
        and AST nodes or line numbers using these components
        :param components: functions/classes/modules components in metadata store
        :param node_filter: a filter function to filter some unqualified AST nodes
        :param search_module_usage: a boolean flag indicating if we are searching module usages or module function call
        usages, defaults to False
        :param line_number_only: if function call usages is searched,
        whether to return the full AST node or return line number only
        :param check_name: which check run this search, None if it is not given
        :return: a dictionary representing the files/lines containing the component usage,
        the dictionary key is a file path, string type
        the dictionary value is also a dictionary, whose key is the component's namespace, whose value is a set of
        line numbers using the component or AST nodes for these components
        """
        files_with_results = {}
        for file_path, ast_info in self.analyzer_client.get_all_ast_infos(
            check_name=check_name
        ):
            result_mapper_with_ast_info = partial(
                _convert_to_result_dict,
                ast_info=ast_info,
                line_number_only=line_number_only,
                get_func_params=get_func_params,
            )
            if node_filter:
                node_filter_with_ast_info = partial(node_filter, ast_info=ast_info)
            component_with_results = defaultdict(list)
            for component in components:
                module_name = component.module_name
                if search_module_usage:
                    call_nodes = ast_info.get_module_usage(module_name)
                else:
                    func_name = component.name
                    # TODO: is it more efficient if we set lineno_only to True?
                    call_nodes = ast_info.get_module_function_call_usage(
                        module_name, func_name, lineno_only=False
                    )

                if node_filter:
                    call_nodes = list(filter(node_filter_with_ast_info, call_nodes))

                result_dict = map(result_mapper_with_ast_info, call_nodes)

                if call_nodes:
                    component_with_results[component.namespace].extend(result_dict)

            if component_with_results:
                files_with_results[file_path] = component_with_results
        return files_with_results
