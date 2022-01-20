"""
Sets of pre-defined node filters
"""

import ast


def is_sub_class_def(node, ast_info):
    """
    Sub-class filter to identify if parent node of node is a ast.ClassDef instance
    """
    parent_node = ast_info.get_parent_ast_node(node)
    return isinstance(parent_node, ast.ClassDef)
