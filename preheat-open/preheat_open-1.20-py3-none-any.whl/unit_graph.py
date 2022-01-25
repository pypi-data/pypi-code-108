import networkx as nx

from .unit import Unit


def generate_unit_graph(building):
    """
    Function to build unit graph from a Building object.
    Iterates through units (nodes) and builds graph based on relations (sub-units).
    Returns a networkx directed multigraph.
    """

    # Empty graph
    G = nx.MultiDiGraph()
    # Number of nodes, initially
    pre = 0

    # First run (top-level units)
    for unit_type, units in building.units.items():
        G.add_nodes_from(
            [(unit.id, {"unit": unit, "name": unit.name}) for unit in units]
        )

    # Note: discovery of sub-units is not optimized (but robust)

    # While new units are discovered
    while pre < G.number_of_nodes():
        # Update number of nodes
        pre = G.number_of_nodes()

        # For each old node (copy of graph)
        for node, data in nx.create_empty_copy(G).nodes.data():
            if hasattr(data["unit"], "sub_units"):
                # Add sub-units as new nodes
                new_nodes = [
                    (unit.id, {"unit": unit, "name": unit.name})
                    for unit in data["unit"].sub_units
                ]
                G.add_nodes_from(new_nodes)

                # Make corresponding edges between nodes
                new_edges = [
                    (node, unit.id, {"weight": 0})
                    for unit in data["unit"].sub_units
                    if not G.has_edge(node, unit.id)
                ]
                G.add_edges_from(new_edges)

    if building.units["main"]:
        # Add edges to Main (heating and hot water)
        G.add_edges_from(
            [
                (building.units["main"][0].id, node, {"weight": 0})
                for node, data in G.nodes.data()
                if data["unit"].unit_type == "heating"
                or data["unit"].unit_type == "hotWater"
            ]
        )

        heating_primary = Unit("supplyPoint", {"id": 0, "name": "Heat"})
        G.add_node(heating_primary.id, name=heating_primary.name, unit=heating_primary)
        G.add_edge(heating_primary.id, building.units["main"][0].id, weight=0)

    # Manually add edges to Main (electricity)
    main_electricity = [
        node
        for node, data in G.nodes.data()
        if data["unit"].name == "Main" and data["unit"].unit_type == "electricity"
    ]

    if main_electricity:
        # Add other meters (not main) to main
        G.add_edges_from(
            [
                (main_electricity[0], node, {"weight": 0})
                for node, data in G.nodes.data()
                if data["unit"].unit_type == "electricity"
                and node != main_electricity[0]
            ]
        )

        electricity_primary = Unit("supplyPoint", {"id": 1, "name": "Electricity"})
        G.add_node(
            electricity_primary.id,
            name=electricity_primary.name,
            unit=electricity_primary,
        )
        G.add_edge(electricity_primary.id, main_electricity[0], weight=0)

    return G


def obtain_loop(graph, id):
    """
    Function which first finds a tree, based on id of origin unit/node.
    The end nodes of the tree are then connected back to the origin, to
    form a loop/circuit -- for circuit analysis.
    """

    # First traverse and find tree based on starting point
    tree = nx.dfs_tree(graph, id)

    # Find end nodes
    end_nodes = [n for n in tree.nodes() if tree.out_degree(n) == 0]

    # Subgraph (copy, because we want to manipulate with it)
    Gi = graph.subgraph(tree)
    Gi = Gi.copy()

    # Close loop to initial node to form circuit
    Gi.add_edges_from([(n, id, {"weight": 0}) for n in end_nodes])

    # Return tree and graph
    return tree, Gi


def load_data_graph(graph, start_date, end_date, time_resolution):
    """
    Loads data for a graph. Loops through nodes (units) and loads
    data on the units with the given start, end and resolution.
    Does not return anything -- data is held in the Unit objects.
    """
    for node, data in graph.nodes.data():
        data["unit"].load_data(start_date, end_date, time_resolution)


def draw_graph(graph):
    """
    Draws graph using networkx built in draw function.
    This is not pretty, but will help to see if graph is constructed correctly.
    """
    nx.draw(
        graph,
        pos=nx.shell_layout(graph),
        node_size=20,
        labels={node: data["unit"].name for node, data in graph.nodes.data()},
        font_size=8,
    )
