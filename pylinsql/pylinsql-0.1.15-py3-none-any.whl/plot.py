"""
Visualize control flow graphs.
"""

from typing import List

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout

from .node import AbstractNode


def plot_directed_graph(title: str, nodes: List[AbstractNode]) -> None:
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for node in nodes:
        if node.on_true is None and node.on_false is None:
            continue
        if node.on_true is node.on_false:
            if node.on_true in nodes:
                width = 2
            else:
                width = 1
            G.add_edge(node, node.on_true, color="black", width=width)
            continue
        if node.on_true is not None:
            if node.on_true in nodes:
                width = 2
            else:
                width = 1
            G.add_edge(node, node.on_true, color="green", width=width)
        if node.on_false is not None:
            if node.on_false in nodes:
                width = 2
            else:
                width = 1
            G.add_edge(node, node.on_false, color="red", width=width)

    colors = list(nx.get_edge_attributes(G, "color").values())
    widths = list(nx.get_edge_attributes(G, "width").values())
    pos = graphviz_layout(G, prog="dot")

    plt.figure(num=title)
    nx.draw(G, pos, edge_color=colors, width=widths, with_labels=True)
    plt.show()