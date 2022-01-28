"""Functions to aid manipulation of networkx graphs as well as some graph 
related utilities.""" 
import inspect
import types
import collections

import networkx as nx

def default_key(d, key, default=None):
    try:
        return d[key]
    except KeyError:
        return default

def flip_dict(dd):
    """Swap kay-value in a dictionary"""
    outdd = collections.defaultdict(list)
    for k,v in dd.items():
        outdd[v].append(k)
    return dict(outdd)

def get_sink_nodes(G):
    '''A sink node is a node with no outgoing edges.
    '''
    out_degree_dict = flip_dict(dict(G.out_degree))
    try:
        sink_nodes = out_degree_dict[0]
    except KeyError:
        sink_nodes = []
    return sink_nodes

def get_source_nodes(G):
    '''A source node is a node with no incoming edges.
    '''
    in_degree_dict = flip_dict(dict(G.in_degree))
    try:
        source_nodes = in_degree_dict[0]
    except KeyError:
        source_nodes = []
    return source_nodes

def get_orphan_nodes(G):
    '''An orphan node is a node with no edges.
    '''

    degree_dict = flip_dict(dict(G.degree))
    try:
        orphan_nodes = list(set(degree_dict[0]))
    except KeyError:
        orphan_nodes = []
    return orphan_nodes

def copy_graph(G):
    '''A trick I often see in networkx's codebase to copy a graph.
    type(G) returns the class of G (e.g. nx.DiGraph) which can accept a graph to
    make a copy of.
    Useful for writing 'pure' functions on graphs.
    '''
    return type(G)(G)

def remove_sinks(G, recursive=True, inplace=False):
    '''Removes nodes with out degree 0 from graph G.
    Sometimes removing a out degree 0 node creates a new out degree 0 node.
    So it is necessary to remove out degree 0 nodes recursively.
    '''
    if not inplace:
        G = copy_graph(G)
    sink_nodes = get_sink_nodes(G)
    if sink_nodes == []:
        # Graph has no sink nodes; break recursion 
        return G
    G.remove_nodes_from(sink_nodes)
    if recursive:
        return remove_sinks(G, recursive=True)
    return G

def remove_sources(G, recursive=True, inplace=False):
    '''Removes nodes with in degree 0 from graph G.
    Sometimes removing a in degree 0 node creates a new in degree 0 node.
    So it is necessary to remove in degree 0 nodes recursively.
    '''
    if not inplace:
        G = copy_graph(G)
    source_nodes = get_source_nodes(G)
    if source_nodes == []:
        # Graph has no sink nodes; break recursion 
        return G
    G.remove_nodes_from(source_nodes)
    if recursive:
        return remove_sources(G, recursive=True)
    return G

def remove_orphans(G, inplace=False):
    '''Removes nodes with in and out degree 0 from graph G.
    This should not need to be recursive.
    '''
    if not inplace:
        G = copy_graph(G)
    orphan_nodes = get_orphan_nodes(G) 
    if len(orphan_nodes) > 0:
        G.remove_nodes_from(orphan_nodes)
    return G

def class_graph(cls, G=None):
    '''Creates a directed graph from a class and all of its base classes.
    |object| is ignored because every class derives from object and so it just 
    clutters up the graph.
    '''
    if G is None:
        G = nx.DiGraph()
    G.add_node(cls)
    for b in cls.__bases__:
        if b is not object:
            G.add_edge(b, cls)
            class_graph(b, G)
    return G

def module_graph(module, G=None, external_modules=False, include_root_module=False):
    '''Creates a directed graph from a module and all of its submodules.
    External submodules can be included in graph but they will not be traversed 
    since that could cause the graph to walk an absurd number of packages.

    The root module is typically not included since it tends to clutter the graph.
    '''
    def _module_graph_iter(module, G, external_modules):
        G.add_node(module)
        for name, obj in inspect.getmembers(module):
            obj_is_public = name[0] != '_'
            if obj_is_public and isinstance(obj, types.ModuleType):
                obj_is_submodule = module.__name__ in obj.__name__
                if external_modules or obj_is_submodule:
                    G.add_edge(module, obj)
                if obj_is_submodule:
                    _module_graph_iter(obj, G, external_modules)

    if G is None:
        G = nx.DiGraph()
    _module_graph_iter(module, G, external_modules)
    if not include_root_module:
        G.remove_node(module)
    return G

def class_graph_from_module_graph(module_graph, G=None):
    '''Creates a directed graph for all the classes and base classes in the 
    module graph.
    '''
    if G is None:
        G = nx.DiGraph(G)
    for module in module_graph.nodes:
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, type):
                if obj not in G.nodes:
                    class_graph(obj, G)
    return G