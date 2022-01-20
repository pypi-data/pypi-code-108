import typing

__all__ = ['get_nested_complex_nodes']


def get_nested_complex_nodes(node: object, node_name: str, *sub_node_names: str) \
        -> typing.Generator[typing.Tuple[str, object], None, None]:
    """ Get all the nodes in a nested complex node structure.

    For example, with the following XML:

    .. code-block:: xml

        <root>
          <level1>
            <level2>
            <level2>
            <level2>
          </level1>
          <level1>
            <level2>
          </level1>
        </root>

    a call ``get_nested_complex_list(root_node, 'level1', 'level2')`` yields a sequence of

    .. code-block:: python

        [('level1', level1-node),
         ('level2', level2-node),
         ('level2', level2-node),
         ('level2', level2-node),
         ('level1', level1-node),
         ('level2', level2-node)
        ]

    :param node: root node containing 'node_name' nodes
    :param node_name: name of first level nodes to retrieve
    :param sub_node_names: subsequent names of nodes to recursively retrieve
    :return: a generator yielding matching nodes
    """

    child_nodes = getattr(node, node_name, [])

    for child_node in child_nodes:
        yield node_name, child_node
        if sub_node_names:
            yield from get_nested_complex_nodes(child_node, *sub_node_names)
