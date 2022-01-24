"""
A module for animating graphviz graphs.
"""
# Standard imports
import re

# Third-party imports
from PIL import Image as PIL_Image

# pylint: disable=anomalous-backslash-in-string


def make_sepset_node_name(node_a_name, node_b_name):
    """
    Make a standard sepset node name using the two neighboring nodes.

    :param str node_a_name: The one node's name.
    :param str node_b_name: The other node's name.
    :return: The sepset's name
    :rtype: str
    """
    return "sepset__" + "__".join(sorted([node_a_name, node_b_name]))


def change_cluster_graph_edge_color(graph, node_a_name, node_b_name, new_color):
    """
    Change the color of an edge in a cluster graph graphviz object. Note that the cluster graph has cluster and sepset
    nodes. The 'edge' of which the color is changed in this function is actually two edges in the graphviz object (the
    edge between node_a and the sepset node and the edge between the sepset node and node_b).

    :param graph: The graphviz graph
    :param node_a_name: The edge's one neighboring node's name.
    :param node_b_name: The edge's other neighboring node's name.
    :param new_color: The new color (i.e 'green' or 'red')
    """

    sepset_node_name = make_sepset_node_name(node_a_name, node_b_name)
    change_graph_edge_color(
        graph=graph, node_a_name=node_a_name, node_b_name=sepset_node_name, new_color=new_color
    )
    change_graph_edge_color(
        graph=graph, node_a_name=node_b_name, node_b_name=sepset_node_name, new_color=new_color
    )


def sub_and_super_both_in(sub_string, super_string, main_string):
    """
    Check if a substring and a super (contains the substring) string are both in another string in non overlapping areas.

    :param sub_string: The string contained in the super-string.
    :param super_string: The string containing the sub-string.
    :param main_string: The main string to check the independent presence of the strings.
    :return:
    """
    if sub_string not in main_string:
        return False
    reduced_string = main_string.replace(super_string, "")
    if sub_string in reduced_string:
        return True
    return False


def contains_non_overlapping_substrings(substring_a, substring_b, main_string):
    """
    Check that both sub-strings can be found in separate locations in strings

    :param substring_a: The one substring to check for.
    :param substring_b: The other substring to check for.
    :param main_string: The string to check in.
    :return: Result of check for independent string presence.

    :Examples:

    >>> substring_a = "abc"
    >>> substring_b = "123"
    >>> main_string = "abc123 -- def"
    >>> contains_non_overlapping_substrings(substring_a, substring_b, string)
    >>> False

    >>> substring_a = "abc"
    >>> substring_b = "123"
    >>> main_string = "abc -- 123"
    >>> contains_non_overlapping_substrings(substring_a, substring_b, string)
    >>> True
    """

    if substring_a in substring_b:
        return sub_and_super_both_in(substring_a, substring_b, main_string)

    if substring_b in substring_a:
        return sub_and_super_both_in(substring_b, substring_a, main_string)
    # Neither substring strings is a substring of the other, so we can remove the one and check if the other is still
    # present.
    if substring_a in main_string:
        reduced_string = main_string.replace(substring_a, "")
    else:
        return False
    result = substring_b in reduced_string
    return result


def change_graph_edge_color(graph, node_a_name, node_b_name, new_color):
    """
    Change the edge color of the edge between two nodes in a graphviz object.

    :param graph: The graphviz graph
    :param node_a_name: The one node
    :param node_b_name: The other node
    :param new_color: The new color of the edge (i.e 'green', 'blue', 'red')
    """

    edge_found = False
    for i, string_i in enumerate(graph.body):
        if "--" in string_i:
            if contains_non_overlapping_substrings(node_a_name, node_b_name, string_i):
                pattern = f'(\\t?"?{node_a_name}"?\s--\s"?{node_b_name}"?\s\[.*color=)([\S]*\s)(.*)'
                new_string_i = re.sub(pattern, f"\g<1>{new_color} \g<3>", string_i)
                # TODO: improve this (it's a bit hacky)
                if new_string_i == string_i:
                    pattern = f'(\\t?"?{node_b_name}"?\s--\s"?{node_a_name}"?\s\[.*color=)([\S]*\s)(.*)'
                    new_string_i = re.sub(pattern, f"\g<1>{new_color} \g<3>", string_i)

                graph.body[i] = new_string_i
                edge_found = True
    if not edge_found:
        raise ValueError(f"no edge between node {node_a_name} and node {node_b_name} in graph.")


def change_graph_node_color(graph, node_name, new_color):
    """
    Change the fill color of a node in a cluster graph graphviz object.

    :param graph:  The graphviz graph
    :param node_name: The name of the node which colour should be changed.
    :param new_color: The new fill color of the node (i.e 'green', 'blue', 'red')
    :return:
    """
    node_found = False
    for i, element_string in enumerate(graph.body):
        if "--" not in element_string:  # not edge
            if node_name in element_string:
                graph.body[i] = re.sub(
                    f'(\\t?"?{node_name}"?\s\[.*fillcolor=)([\S]*\s)(.*)', f"\g<1>{new_color} \g<3>", element_string
                )
                node_found = True
    if not node_found:
        raise ValueError(f"cannot change colour of not existing node: no node {node_name} in graph")


def graph_to_pil_image(graph):
    """
    Convert the graph to a PIL image.
    :param graph: The graph to convert.
    """
    graph.render("/tmp/test.gv", view=False)
    pil_image = PIL_Image.open("/tmp/test.gv.png")
    pil_image_copy = pil_image.copy()
    pil_image.close()
    return pil_image_copy


def add_message_pass_animation_frames(graph, frames, node_a_name, node_b_name):
    """
    Add frames (as part of the animation) representing a message being passed between two nodes in the graph.
    :param graph: The graph.
    :param frames: The frames to add.
    :param node_a_name: The one node.
    :param node_b_name: The other node.
    """
    new_color = "red"
    change_graph_node_color(graph=graph, node_name=node_a_name, new_color=new_color)
    frames.append(graph_to_pil_image(graph))

    change_cluster_graph_edge_color(
        graph=graph, node_a_name=node_a_name, node_b_name=node_b_name, new_color=new_color
    )
    frames.append(graph_to_pil_image(graph))

    change_graph_node_color(graph=graph, node_name=node_b_name, new_color=new_color)
    frames.append(graph_to_pil_image(graph))
    change_graph_node_color(graph=graph, node_name=node_a_name, new_color="white")
    frames.append(graph_to_pil_image(graph))

    change_cluster_graph_edge_color(
        graph=graph, node_a_name=node_a_name, node_b_name=node_b_name, new_color="black"
    )
    frames.append(graph_to_pil_image(graph))
    change_graph_node_color(graph=graph, node_name=node_b_name, new_color="white")
    frames.append(graph_to_pil_image(graph))
