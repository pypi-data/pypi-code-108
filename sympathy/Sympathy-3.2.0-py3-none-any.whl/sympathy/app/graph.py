# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import copy
import Qt.QtCore as QtCore
import functools
import itertools
import enum
import traceback
import networkx as nx
from collections import OrderedDict, deque

from sympathy.utils import log


core_logger = log.get_logger('core')


class GraphInterface(object):

    """GraphInterface"""

    def __init__(self, nodes=None, edges=None):
        super(GraphInterface, self).__init__()

    def edges(self):
        raise NotImplementedError('Not implemented for interface')

    def add_node(self, node):
        raise NotImplementedError('Not implemented for interface')

    def remove_node(self, node):
        raise NotImplementedError('Not implemented for interface')

    def add_edge(self, src, dst, **labels):
        raise NotImplementedError('Not implemented for interface')

    def remove_edge(self, src, dst):
        raise NotImplementedError('Not implemented for interface')

    def has_edge(self, src, dst):
        raise NotImplementedError('Not implemented for interface')

    def edge_labels(self, src, dst):
        raise NotImplementedError('Not implemented for interface')

    def _find_cycle(self, src=None):
        orientations = ['original']
        if src:
            orientations = ['original', 'reverse']

        for orientation in orientations:
            try:
                return nx.find_cycle(
                    self._graph, source=src, orientation=orientation)
            except nx.exception.NetworkXNoCycle:
                pass
        return None

    def edges_in_cycles(self):
        orientation = 'original'
        try:
            for src, dst, orientation in nx.find_cycle(
                    self._graph, source=None, orientation='original'):
                yield (src, dst)
        except nx.exception.NetworkXNoCycle:
            return None

    def in_cycle(self, src):
        return self._find_cycle(src) is not None

    def __str__(self):
        raise NotImplementedError('Not implemented for interface')


class Graph(GraphInterface):

    def __init__(self, nodes=None, edges=None):
        super().__init__()

        self._graph = nx.DiGraph()
        if nodes:
            self._graph.add_nodes_from(nodes)

        if edges:
            self._graph.add_edges_from(edges)

    def nodes(self):
        return self._graph.nodes()

    def edges(self):
        return self._graph.edges()

    def add_edge(self, src, dst, **labels):
        if src not in self._graph:
            core_logger.critical('SRC FAIL {}\n{}'.format(src, self.nodes()))
            core_logger.critical(''.join(traceback.format_stack()))
        if dst not in self._graph:
            core_logger.critical('DST FAIL {}\n{}'.format(dst, self.nodes()))
            core_logger.critical(''.join(traceback.format_stack()))
        self._graph.add_edge(src, dst, **labels)

    def remove_edge(self, src, dst):
        self._graph.remove_edge(src, dst)

    def has_edge(self, src, dst):
        return self._graph.has_edge(src, dst)

    def edge_labels(self, src, dst):
        return self._graph.get_edge_data(src, dst)

    def add_node(self, node):
        self._graph.add_node(node)

    def remove_node(self, node):
        self._graph.remove_node(node)

    def subgraph(self, nodes, as_view=True):
        graph = self._graph.subgraph(nodes)
        if not as_view:
            copy = nx.DiGraph()
            copy.add_nodes_from(graph.nodes())
            copy.add_edges_from(graph.edges())
            graph = copy

        res = Graph()
        res._graph = graph
        return res

    def successors(self, node):
        return self._graph.successors(node)

    def predecessors(self, node):
        return self._graph.predecessors(node)

    def descendants(self, node):
        return nx.descendants(self._graph, node)

    def ancestors(self, node):
        return nx.ancestors(self._graph, node)

    def topological_sort(self):
        return nx.topological_sort(self._graph)

    def __str__(self):
        output = 'digraph hub {\nrankdir="LR";\n'
        obj_ids = {}
        count = itertools.count()

        def get_id(obj):
            if obj in obj_ids:
                return obj_ids[obj]
            i = next(count)
            obj_ids[obj] = i
            return i

        for n0 in self.nodes():
            src = get_id(n0)

            for n1 in self.successors(n0):
                dst = get_id(n1)

                output += '"%s" -> "%s";\n' % (src, dst)
        output += '\n}\n'
        return output

    def __contains__(self, node):
        return node in self._graph


class DocumentGraph(GraphInterface):
    """
    Graph which keeps track of entry and exit nodes through
    two special nodes: entry and exit.

    These will not be included in the return values of normal methods
    but can be used to in traversals.
    """

    def __init__(self, nodes=None, edges=None):
        super().__init__()
        nodes = nodes or []
        edges = edges or []
        self._entry_node = 'entry'
        self._exit_node = 'exit'
        self._g = Graph()
        self._g.add_node(self._entry_node)
        self._g.add_node(self._exit_node)
        for node in nodes:
            self.add_node(node)
        for src, dst in edges:
            self.add_edge(src, dst)

    def nodes(self):
        return self._remove_io_nodes(self._g.nodes())

    def edges(self):
        return self._remove_io_edges(self._g.edges())

    def edges_in_cycles(self):
        return self._remove_io_edges(self._g.edges_in_cycles())

    def add_node(self, node):
        self._no_io_guard(node)
        self._g.add_node(node)
        self._add_entry_edge(node)
        self._add_exit_edge(node)

    def remove_node(self, node):
        self._no_io_guard(node)
        self._g.remove_node(node)

    def add_edge(self, src, dst, **labels):
        for node in [src, dst]:
            self._no_io_guard(node)

        self._remove_entry_edge(dst)
        self._remove_exit_edge(src)
        self._g.add_edge(src, dst, **labels)

    def remove_edge(self, src, dst):
        for node in [src, dst]:
            self._no_io_guard(node)

        self._g.remove_edge(src, dst)

        if len(self.successors(src)) == 0:
            self._add_exit_edge(src)
        if len(self.predecessors(dst)) == 0:
            self._add_entry_edge(dst)

    def has_edge(self, src, dst):
        io = self._io_nodes()
        for node in [src, dst]:
            if node in io:
                return False
        return self._g.has_edge(src, dst)

    def edge_labels(self, src, dst):
        io = self._io_nodes()
        for node in [src, dst]:
            if node in io:
                return {}
        return self._g.get_edge_data(src, dst)

    def subgraph(self, nodes, as_view=True):
        nodes = list(nodes)
        g = self._g.subgraph(
            [self._entry_node, self._exit_node] + nodes, as_view=as_view)
        dg = DocumentGraph()
        dg._g = g
        return dg

    def __str__(self):
        return self._g.__str__()

    def _add_entry_edge(self, node):
        self._g.add_edge(self._entry_node, node)

    def _add_exit_edge(self, node):
        self._g.add_edge(node, self._exit_node)

    def _remove_entry_edge(self, node):
        try:
            self._g.remove_edge(self._entry_node, node)
        except Exception:
            pass

    def _remove_exit_edge(self, node):
        try:
            self._g.remove_edge(node, self._exit_node)
        except Exception:
            pass

    def _no_io_guard(self, node):
        if node in self._io_nodes():
            raise ValueError()

    def _io_nodes(self):
        return (self._entry_node, self._exit_node)

    def _remove_io_nodes(self, nodes):
        io = self._io_nodes()
        nodes = list(nodes)
        return [n for n in nodes if n not in io]

    def _remove_io_edges(self, edges):
        io = self._io_nodes()
        edges = list(edges)
        return [(src, dst) for src, dst in edges
                if src not in io and dst not in io]

    def entry_nodes(self):
        return self._remove_io_nodes(self._g.successors(self._entry_node))

    def exit_nodes(self):
        return self._remove_io_nodes(self._g.predecessors(self._exit_node))

    def successors(self, node):
        return self._remove_io_nodes(self._g.successors(node))

    def predecessors(self, node):
        return self._remove_io_nodes(self._g.predecessors(node))

    def descendants(self, node):
        return self._remove_io_nodes(self._g.descendants(node))

    def ancestors(self, node):
        return self._remove_io_nodes(self._g.ancestors(node))

    def entry_descendants(self):
        return self._remove_io_nodes(self._g.descendants(self._entry_node))

    def exit_ancestors(self):
        return self._remove_io_nodes(self._g.ancestors(self._exit_node))

    def topological_sort(self):
        return self._remove_io_nodes(self._g.topological_sort())

    def in_cycle(self, src):
        return self._g.in_cycle(src)

    def node_depths(self):
        depths = {}
        for dst in self._g.topological_sort():
            depths[dst] = max((depths[src] for src in self.predecessors(dst)), default=-1) + 1
        io = self._io_nodes()
        return {n: i for n, i in depths.items() if n not in io}

    def __contains__(self, node):
        return node not in self._io_nodes() and node in self._g
