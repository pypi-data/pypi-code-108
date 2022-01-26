import os
import numpy as np
import igraph
from myutils import geo

R = 6371000

##########################################################
def add_lengths(g, x, y):
    """Add length to the edges, assuming each vertex has a location"""

    for i, e in enumerate(g.es()):
        lon1, lat1 = g.vs[e.source][x], g.vs[e.source][y]
        lon2, lat2 = g.vs[e.target][x], g.vs[e.target][y]
        g.es[i]['length'] = geo.haversine([lon1, lat1], [lon2, lat2])
    return g

##########################################################
def simplify_graphml(graphpath, directed=True, simplify=True):
    """Get largest connected component from @graphatph and add weights
    According to the params @undirected, @simplify, convert to
    undirected and/or remove multiple edges and self-loops.
    If the original graph has x,y attributes, we also compute the length"""

    g = igraph.Graph.Read(graphpath)
    if simplify: g.simplify(combine_edges='first')
    if not directed: g.to_undirected()
    g = g.components(mode='weak').giant()

    if ('x' in g.vertex_attributes()) or ('lon' in g.vertex_attributes()):
        if 'x' in g.vertex_attributes(): x = 'x'; y = 'y';
        else: x = 'lon'; y = 'lat';

        g.vs[x] = [float(xx) for xx in g.vs[x]]
        g.vs[y] = [float(yy) for yy in g.vs[y]]

        g = add_lengths(g, x, y)

    g.vs['origid'] = list(range(g.vcount()))

    return g
