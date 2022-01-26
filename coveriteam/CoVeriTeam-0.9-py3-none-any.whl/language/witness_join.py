#!/usr/bin/env python3

# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
# SPDX-FileCopyrightText: 2020 Jan Haltermann
#
# SPDX-License-Identifier: Apache-2.0

import xml.etree.ElementTree as ET  # noqa N817 use of idiomatic name ET for ElementTree
import sys
import argparse
import hashlib
import logging
import re


class JoinerException(Exception):
    pass


def find_root(graph_xml):
    # find the initial node for first :
    for n in graph_xml.findall("{http://graphml.graphdrawing.org/xmlns}node"):
        logging.debug("%s %s", n.tag, n.attrib)
        for nodeAttr in n:
            if nodeAttr.get("key") == "entry" and nodeAttr.text == "true":
                return n
    return None


def contains_invar(graph_xml):
    # find the initial node for first :
    for n in graph_xml.findall("{http://graphml.graphdrawing.org/xmlns}node"):
        for nodeAttr in n:
            if nodeAttr.get("key") == "invariant" and nodeAttr.text is not None:
                return True
    return False


# Pretty print
def pretty_print(mapping):
    for key in mapping:
        fir = mapping[key]
        print(key.get("id"), "-->", "(", fir.get("id"), ")")


def pretty_print_list(li):
    res = ""
    for n in li:
        res = res + n.get("id") + ","
    return res


def compute_source_to_target(graph_xml):
    res = {}
    for e in graph_xml.findall("{http://graphml.graphdrawing.org/xmlns}edge"):
        if e.get("source") in res:
            res[e.get("source")].append(e)
        else:
            res[e.get("source")] = [e]
    return res


def compute_node_names_to_nodes(g):
    res = {}
    for n in g.findall("{http://graphml.graphdrawing.org/xmlns}node"):
        res[n.get("id")] = n
    return res


def get_invar(graph_node):
    invar = None
    scope = None
    for node_attribute in graph_node:
        if node_attribute.get("key") == "invariant" and node_attribute.text is not None:
            print(f"Considering {node_attribute} for {graph_node}")
            invar = node_attribute.text
            print(f"Got {invar} for {graph_node}")
            scope_match = re.match(r"([a-zA-Z0-9_]+?)__[a-zA-Z_].*", invar)
            if scope_match:
                assert len({scope_match.groups()}) == 1
                scope = scope_match.group(1)
            invar = re.sub(r"[a-zA-Z0-9_]+?__([a-zA-Z_][^\ =*/\+\&-]*)", r"\1", invar)

        elif (
            scope is None
            and node_attribute.get("key") == "invariant.scope"
            and node_attribute.text is not None
        ):
            scope = node_attribute.text
    print("Found invar", invar, "in scope", scope, "at node", graph_node.get("id"))
    return invar, scope


def compute_hash(path):
    blocksize = 65536
    hasher = hashlib.sha256()
    with open(path, "rb") as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()


def parse(argv):
    # Taken from https://stackabuse.com/command-line-arguments-in-python/
    # Initiate the parser
    desc = (
        "Merge two witnesses given as graphml file. They are assumed to be produced by the same tool, as we expect the "
        "edges to contain the same arguments to be matched.\n "
    )
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "-V", "--version", help="show program version", action="version", version="0.1"
    )
    parser.add_argument("-f", "--first", required=True, help="The first witness")
    parser.add_argument("-s", "--second", required=True, help="The second witness")
    parser.add_argument(
        "-t",
        "--target",
        default="merged.graphml",
        help="The path for the merged witness to be stored to. Default is current "
        "directory, filename is 'merged.graphml'",
    )
    # Read arguments from the command line
    return parser.parse_args(argv)


def get_graph(graphml):
    return graphml.find("{http://graphml.graphdrawing.org/xmlns}graph")


def remove_graph(graphml):
    for graph in graphml.findall("{http://graphml.graphdrawing.org/xmlns}graph"):
        graphml.remove(graph)


def get_all_invariants(graph):
    for node_element in graph.iterfind("{http://graphml.graphdrawing.org/xmlns}node"):
        invar, scope = get_invar(node_element)
        if invar and invar.strip() not in ("0", "0||0", "(0)", "((0))"):
            yield invar, scope


def merge_witnesses(first_path, second_path, target_path):
    ET.register_namespace("", "http://graphml.graphdrawing.org/xmlns")
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
    tree1 = ET.parse(first_path)  # noqa S314
    root1 = tree1.getroot()
    graph1 = get_graph(root1)
    tree2 = ET.parse(second_path)  # noqa S314
    root2 = tree2.getroot()
    graph2 = get_graph(root2)

    if graph1 is None or graph2 is None:
        raise JoinerException(
            str(
                "Either the first or second graph is not formatted correctly, it does not contain an '{"
                "http://graphml.graphdrawing.org/xmlns}graph'"
            )
        )

    # Compute Hash to check if both witnesses are equal
    hash1 = compute_hash(first_path)
    hash2 = compute_hash(second_path)
    if hash1 == hash2:
        print("Both witnesses are equal, hence returning the first one")
        tree1.write(str(target_path))
        return

    # first, check if both G1 and G2 contain invariants:
    g1containsInvars = contains_invar(graph1)
    g2containsInvars = contains_invar(graph2)
    if not g1containsInvars:
        graphRes = graph2
    if not g2containsInvars:
        graphRes = graph2
    else:
        invariants_with_scope = set(get_all_invariants(graph1)) | set(
            get_all_invariants(graph2)
        )
        graphRes = build_default_graph(invariants_with_scope, graph1)

    # put merged graph into a graphml root (with corresponding headers)
    graphml = create_graphml(graphRes, root1)

    ET.ElementTree(element=graphml).write(str(target_path), xml_declaration=True)


def get_data(key, graph):
    for data_element in graph.iterfind("{http://graphml.graphdrawing.org/xmlns}data"):
        if data_element.get("key", "") == key:
            return data_element
    return None


def build_default_graph(invariants_with_scopes, original):
    graph = ET.Element("graph", attrib={"edgedefault": "directed"})
    metadata = {
        "programfile": get_data("programfile", original),
        "programhash": get_data("programhash", original),
        "sourcecodelang": get_data("sourcecodelang", original),
        "producer": get_data("producer", original),
        "specification": get_data("specification", original),
        "creationtime": get_data("creationtime", original),
        "witnesstype": get_data("witness-type", original),
        "architecture": get_data("architecture", original),
    }
    for metadata_element in metadata.values():
        if metadata_element is None:
            continue
        graph.append(metadata_element)
    entry_node = ET.SubElement(
        graph, "{http://graphml.graphdrawing.org/xmlns}node", attrib={"id": "N0"}
    )
    entry_node.tail = "\n"
    entry_data = ET.SubElement(
        entry_node,
        "{http://graphml.graphdrawing.org/xmlns}data",
        attrib={"key": "entry"},
    )
    entry_data.text = "true"
    entry_data.tail = "\n"

    edges = []
    for idx, (inv, scope) in enumerate(invariants_with_scopes, start=1):
        node_id = f"N{idx}"
        node = ET.SubElement(
            graph, "{http://graphml.graphdrawing.org/xmlns}node", attrib={"id": node_id}
        )
        node.text = "\n\t"
        node.tail = "\n"
        inv_element = ET.SubElement(
            node,
            "{http://graphml.graphdrawing.org/xmlns}data",
            attrib={"key": "invariant"},
        )
        inv_element.text = inv
        inv_element.tail = "\n"
        if scope:
            scope_element = ET.SubElement(
                node,
                "{http://graphml.graphdrawing.org/xmlns}data",
                attrib={"key": "invariant.scope"},
            )
            scope_element.text = scope
            scope_element.tail = "\n"
        edge_from_entry_to_node = ET.Element(
            "{http://graphml.graphdrawing.org/xmlns}edge",
            attrib={"id": f"E{idx}", "source": "N0", "target": node_id},
        )
        edge_from_entry_to_node.tail = "\n"
        edges.append(edge_from_entry_to_node)
    [graph.append(edge) for edge in edges]
    return graph


def create_graphml(graph_element, original_graphml):
    """Create a new graphml element with the original graphml as basis, but the new graph element."""
    remove_graph(original_graphml)
    original_graphml.append(graph_element)
    return original_graphml


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]
    args = parse(argv)
    first_path, second_path, target_path = args.first, args.second, args.target

    try:
        merge_witnesses(first_path, second_path, target_path)
    except JoinerException as e:
        print(e, file=sys.stderr)
        return 1
    else:
        print("The merged result is stored at", target_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
