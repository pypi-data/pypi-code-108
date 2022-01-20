""" Visualization functions specialized for Zotero data  """

import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns


def draw_multigraph(g: nx.MultiGraph, pos: dict, radius_mult=0.1,
                    directed=False, **kwargs) -> plt.Axes:
    """A way to draw multiple edges per node pair

    :param g: A multigraph, probably returned by zoviz.DB.build_creator_graph()
    :type g: nx.MultiGraph
    :param pos: networkx layout
    :type pos: dict
    :param directed: Draw arrows?, defaults to False
    :type directed: bool, optional
    :return: return axis handle
    :rtype: plt.Axes
    """
    ax = plt.gca()
    # Draw nodes & labels
    label_kwargs = {k: v for k, v in kwargs.items() if "font" in k}
    node_kwargs = {k: v for k, v in kwargs.items() if "font" not in k}
    nx.draw_networkx_labels(g, pos, **label_kwargs)
    nx.draw_networkx_nodes(g, pos, **node_kwargs)

    # Draw edges w/ different arc radius for each duplicate
    arrowstyle = "->" if directed else "-"
    for e in g.edges:
        startpos = pos[e[0]]
        endpos = pos[e[1]]
        edge_index = e[2]  # I am the Nth edge between these nodes
        radius = radius_mult * float(edge_index)
        connectionstyle = "arc3,rad=%f" % radius
        arrowprops = {"arrowstyle": arrowstyle,
                      "connectionstyle": connectionstyle,
                      "color": kwargs.get("edge_color", 'k'),
                      "alpha": kwargs.get("edge_alpha", 0.3),
                      "linewidth": kwargs.get("edge_linewidth", 1.)}
        ax.annotate("", xy=startpos, xytext=endpos,
                    xycoords="data", arrowprops=arrowprops, zorder=-1)
    return ax


def draw_community_graph(g: nx.MultiGraph, fig=None, **kwargs) -> plt.Figure:
    """A quick, deterministic embedding for the creator graph

    :param collection: Zotero Collection name
    :type collection: str
    :return: figure handle
    :rtype: plt.Figure
    """
    if len(g.nodes) < 2:
        raise ValueError("Community graph has less than 2 members; unable to draw")

    fig = fig or plt.figure(figsize=(10, 10), dpi=120.)
    node_degrees = [g.degree(n) for n in g.nodes]
    cmap = sns.cubehelix_palette(start=0, rot=3., dark=0.6,
                                 as_cmap=True, reverse=True)
    colors = cmap([float(x) / max(max(node_degrees), 1) for x in node_degrees])
    counts = [float(x.count) for x in g.nodes]
    max_count = max(counts)
    sizes_normed = [x * 5e3 / max_count for x in counts]
    layout = nx.spring_layout(g, pos=nx.circular_layout(g),
                              k=len(g.nodes) / 16., iterations=50)
    kwargs["alpha"] = kwargs.get("alpha", 0.9)
    kwargs["font_size"] = kwargs.get("font_size", 6)
    # kwargs["with_labels"] = kwargs.get("with_labels", True)
    draw_multigraph(g, pos=layout, node_color=colors,
                    node_size=sizes_normed, **kwargs)
    return fig, layout
