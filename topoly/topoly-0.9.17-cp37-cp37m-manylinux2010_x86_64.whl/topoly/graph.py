"""
The graph class containing the methods to calculate the graph (and knot) polynomials.
The graphs are stored as extended PD codes, including the information on vertices and crossings in planar projection.

Pawel Dabrowski-Tumanski
p.dabrowski at cent.uw.edu.pl
27.06.2019

Docs:
https://realpython.com/documenting-python-code/#docstring-types

The type used here: Google


Support in PyCharm:
https://www.jetbrains.com/help/pycharm/settings-tools-python-integrated-tools.html
- change default reStructuredText to Google

Docs will be published in: https://readthedocs.org/

"""
import os
import re
from copy import deepcopy
from itertools import combinations
import random

import numpy as np
from topoly.topoly_homfly import *
from topoly.topoly_preprocess import *
from topoly.manipulation import DataParser
from topoly.params import *

TK = True
import matplotlib
try:
    matplotlib.use("TkAgg")
except ImportError:
    TK = False
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


plot_colors = ['blue', 'red', 'green', 'yellow', 'cyan', 'magenta']


class Graph:
    def __init__(self, init_data='', chain=None, model=None, bridges=[], breaks=[], bridges_type=Bridges.SSBOND, debug=False):
        self.orig_input = init_data

        if type(init_data) is str and os.path.isfile(init_data):
            with open(init_data, 'r') as myfile:
                init_data = myfile.read()
        self.init_data = init_data

        if type(self.init_data) is list and len(self.init_data) == 0:
            raise TopolyException("The list entered is empty. Cannot calculate anything on it... Sorry.")

        data = DataParser.read_format(self.init_data, self.orig_input, chain, model, bridges, breaks, bridges_type, debug)

        if not data['coordinates'] and not data['pdcode'] and not data['emcode']:
            raise TopolyException('The input data incorrect. Maybe its just missing file? (trying to open ' +
                                  self.orig_input + ')')

        # real, coordinate-based properties of the graph:
        self.coordinates = data['coordinates']
        self.closed = data['closed']
        self.arcs = data['arcs']
        self.breaks = data['breaks']
        self.bridges = data['bridges']
        self.spatial_graph = self.generate_spatial_graph()
        self.coordinates_c = []
        self.generate_coordinates_c()
        self.identifier = ()
        self.run_from_code = False

        # abstract, code-based properties of the graph
        self.pdcode = data['pdcode']
        self.emcode = data['emcode']
        self.pdcanonical = ''
        if self.pdcode or self.emcode:
            self.run_from_code = True
        self.vertices = []
        self.crossings = []
        self.edge_colors = {}
        self.abstract_graph = {}
        self.edges = set()
        self.orientation = []

        if self.closed:
            self.parse_closed()

    def get_coords(self):
        return self.coords2list(self.coordinates)

    @staticmethod
    def coords2list(coords):
        keys = list(coords.keys())
        vals = list(coords.values())
        for i in range(len(keys)):
            vals[i].insert(0, keys[i])
        return vals

    def parse_closed(self):
        if self.coordinates:
            self.generate_coordinates_c()
        if self.coordinates_c and not self.emcode:
            self.generate_em_from_coords()
        if self.emcode and not self.pdcode:
            #print("JESTEM w graph, generuje pd z em: ", self.emcode)
            self.generate_pd_from_em()
        self.generate_crossings()
        self.generate_vertices()
        self.generate_colors()
        self.generate_orientation()
        self.generate_edges()
        self.check_crossings_vs_orientation()
        self.generate_abstract_graph()
        self.generate_em_from_pd()
        self.generate_pd_canonical()
        return

    ''' Methods for generating, finding, and checking '''
    def check_crossings_vs_orientation(self):
        for k in range(len(self.crossings)):
            for arc in self.orientation:
                if self.crossings[k][0] in arc:     # TODO - to jakas tragedia. Moze mozna prosciej?
                    ind = arc.index(self.crossings[k][0])
                    if arc[ind - 1] == self.crossings[k][2]:
                        self.crossings[k] = self.crossings[k][2:] + self.crossings[k][:2]
        self.update_pdcode()
        return

    def generate_colors(self):
        colors = {}
        for element in self.pdcode.split(';'):
            for edge in element.strip('V[]').split(','):
                splitted = re.split(r'(\d+)', edge)
                if splitted[-1]:
                    colors[int(splitted[1])] = splitted[1] + splitted[-1]
                else:
                    colors[int(splitted[1])] = int(splitted[1])
        self.edge_colors = colors
        return

    def generate_pd_canonical(self):
        self.pdcanonical = self.pdcode
        return

    def generate_coordinates_c(self):
        self.coordinates_c = []
        for arc in self.arcs:
            chain = ''
            for atom in arc:
                if atom in self.coordinates.keys():
                    chain += str(atom) + ' ' + ' '.join([str(x) for x in self.coordinates[atom]]) + '\n'

            chain_c, unable = chain_read_from_string(chain.encode('utf-8'))
            self.coordinates_c.append(chain_c)
        return

    def generate_em_from_coords(self):
        # TODO polaczyc przypadki w programie Wandy
        termini = {}
        yamada_mode = False
        for arc in self.arcs:
            if arc[0] not in termini:
                termini[arc[0]] = 0
            if arc[-1] not in termini:
                termini[arc[-1]] = 0
            termini[arc[0]] += 1
            termini[arc[-1]] += 1
        if all([termini[key] >= 2 for key in list(termini.keys())]):
            yamada_mode = True
        if yamada_mode:
            code = find_link_yamada_code(self.coordinates_c)
        else:
            code = find_link_homfly_code(self.coordinates_c)
        code = code.decode('utf-8').strip().replace('\n', ';')
        self.emcode = code
        return

    def generate_pd_from_em(self):
        result = ''
        letters = 'abcd'
        intervals = []
        for cross in self.emcode.split(';'):
            if not cross:
                continue
            number, rest = re.sub('[-+V]', ' ', cross, count=1).split()
            typ = cross.strip(number)[0]
            code_tmp = []
            tmp = re.split(r'(\d+)', rest)[1:]
            for k in range(0, len(tmp), 2):
                end = tmp[k] + tmp[k + 1]
                if typ == 'V':
                    start = number + 'V'
                else:
                    start = number + letters[int(k / 2)]
                interval = [start, end]
                interval_rev = list(reversed(interval))
                if interval_rev in intervals:
                    code_tmp.append(str(intervals.index(interval_rev)))
                    intervals[intervals.index(interval_rev)] = 0
                else:
                    intervals.append(interval)
                    code_tmp.append(str(len(intervals) - 1))
            if typ == '-':
                code_tmp = list(reversed(code_tmp))
            if typ == '+':
                code_tmp = [code_tmp[1], code_tmp[0], code_tmp[3], code_tmp[2]]
            result += re.sub('[-+]', 'X', typ) + '[' + ','.join(code_tmp) + '];'
        self.pdcode = result[:-1].strip()
        return

    def generate_em_from_pd(self):
        # TODO rewrite this in a more readable way
        letters = {-1: 'dcba', 1: 'badc'}
        signs = {-1: '-', 1: '+'}
        code = []
        # making the vertices part
        for k in range(len(self.vertices)):
            vertex = self.vertices[k]
            vertex_trans = []
            for edge in vertex:
                for l in range(len(self.vertices)):
                    if l == k:
                        continue
                    if edge in self.vertices[l]:
                        vertex_trans.append(str(l+1) + 'V')
                        break
                for l in range(len(self.crossings)):
                    if edge in self.crossings[l]:
                        vertex_trans.append(str(len(self.vertices) + l + 1) + letters[self.find_crossing_sign(l)][self.crossings[l].index(edge)])
            code.append(str(k+1) + 'V' + ''.join(vertex_trans))
        # making the crossing part
        for k in range(len(self.crossings)):
            crossing = self.crossings[k]
            sign = self.find_crossing_sign(k)
            crossing_trans = []
            for e in range(len(crossing)):
                edge = crossing[e]
                for l in range(len(self.vertices)):
                    if edge in self.vertices[l]:
                        crossing_trans.append(str(l+1) + 'V')
                        break
                for l in range(len(self.crossings)):
                    if l == k:
                        if edge in crossing[:e]:
                            newind = crossing[:e].index(edge)
                        elif edge in crossing[e+1:]:
                            newind = crossing[e+1:].index(edge) + e + 1
                        else:
                            continue
                        crossing_trans.append(str(len(self.vertices) + l + 1) + letters[self.find_crossing_sign(l)][newind])
                        break
                    if edge in self.crossings[l]:
                        crossing_trans.append(str(len(self.vertices) + l + 1) + letters[self.find_crossing_sign(l)][self.crossings[l].index(edge)])
                        break
            if sign > 0:
                crossing_trans = crossing_trans[2:] + crossing_trans[:2]
            crossing_trans = list(reversed(crossing_trans))
            code.append(str(len(self.vertices) + k + 1) + signs[sign] + ''.join(crossing_trans))
        self.emcode = ';'.join(code)
        return

    def generate_vertices(self):
        self.vertices = []
        if not self.pdcode:
            return
        for element in self.pdcode.split(';'):
            if element[0] == 'V':
                self.vertices.append([int(x) for x in element.strip('V[]').replace('b','').split(',')])
        return

    def generate_crossings(self):
        self.crossings = []
        if not self.pdcode:
            return
        for element in self.pdcode.split(';'):
            if element[0] == 'X':
                self.crossings.append([int(x) for x in element.strip('X[]').replace('b','').split(',')])
        return

    def generate_edges(self):
        self.edges = set()
        for cross in self.crossings:
            self.edges |= set(cross)
        for vert in self.vertices:
            self.edges |= set(vert)
        return

    def generate_spatial_graph(self):
        graph = {}
        for arc in self.arcs:
            if arc[0] not in graph.keys():
                graph[arc[0]] = []
            if arc[-1] not in graph.keys():
                graph[arc[-1]] = []
            graph[arc[0]].append([arc[-1], arc[1:]])
            if arc[-1] != arc[0]:
                graph[arc[-1]].append([arc[0], list(reversed(arc[:-1]))])
        return graph

    def generate_abstract_graph(self):
        graph = {}
        graph_edges = []    # the edges coming out of vertices
        for k in range(len(self.vertices)):
            graph[k] = []
            graph_edges += self.vertices[k]
        self.abstract_graph = graph
        for arc in self.orientation:
            beg, end = (-1, -1)
            for k in range(len(self.vertices)):
                if arc[-1] in self.vertices[k]:
                    if arc[-1] != arc[0] or beg >= 0 or arc[-1] in self.vertices[k][self.vertices[k].index(arc[-1])+1:]:
                        end = k
                if arc[0] in self.vertices[k] and beg < 0:
                    beg = k
            graph[beg].append([end, arc])
            if beg != end:
                graph[end].append([beg, list(reversed(arc))])
        return

    def Pawla_generate_coords_from_c(self):
        self.coordinates = {}
        self.arcs = []
        last_id = 0
        for arc in self.coordinates_c:
            id = 0
            new_arc = []
            for atom in arc:
                id = int(atom['id']) + last_id
                chains = [x for x in atom.keys() if x != 'id']
                coord_dict = atom[chains[0]]
                coords = [coord_dict[k] for k in ['x', 'y', 'z']]
                self.coordinates[id] = coords
                new_arc.append(id)
            self.arcs.append(new_arc)
            last_id = id
        return

    def generate_coords_from_c(self):
        self.coordinates = {}
        self.arcs = []
        last_id = 0
        for arc in self.coordinates_c:
            id = 0
            new_arc = []
            for atom in arc:
                id = int(atom['id']) #+ last_id
                chains = [x for x in atom.keys() if x != 'id']
                coord_dict = atom[chains[0]]
                coords = [coord_dict[k] for k in ['x', 'y', 'z']]
                #if 
                self.coordinates[id] = coords
                new_arc.append(id)
            self.arcs.append(new_arc)
            last_id = id
        return

    def generate_coords_from_atom_list(self, atoms):
        result = ''
        bridges = []
        translate = {}
        for arc in atoms:
            for atom in arc:
                result += str(atom) + ' ' + ' '.join([str(_) for _ in self.coordinates[atom]]) + '\n'
            result += 'X\n'
        return result[:-2]

    def generate_code_from_edges(self, arcs):
        code = ''
        crossings = []
        vertices = []
        trans = {}

        edges = [edge for arc in arcs for edge in arc]

        # choosing appropriate crossings and vertices
        for cross in self.crossings:
            if all([c in edges for c in cross]):
                crossings.append(cross)
            else:
                trans[cross[0]] = cross[2]
                trans[cross[1]] = cross[3]
        for v in self.vertices:
            codev = []
            for e in edges:
                if e in v:
                    codev.append(e)
            if codev:
                vertices.append(codev)

        # simplifying the dictionary
        changed = True
        while changed:
            changed = False
            keys = list(trans.keys())
            for key in keys:
                if trans[key] in keys:
                    val = trans[trans[key]]
                    trans.pop(trans[key])
                    trans[key] = val
                    changed = True
                    break

        # making a PD code
        for cross in crossings:
            for k in range(len(cross)):
                if cross[k] in trans.keys():
                    cross[k] = trans[cross[k]]
            code += 'X[' + ','.join([str(x) for x in cross]) + '];'
        for vert in vertices:
            for k in range(len(vert)):
                if vert[k] in trans.keys():
                    vert[k] = trans[vert[k]]
            code += 'V[' + ','.join([str(x) for x in vert]) + '];'
        generator = code[:-1]
        return generator

    def generate_orientation(self):
        # TODO uproscic
        edges = set([c for cross in self.crossings for c in cross] + [v for vert in self.vertices for v in vert])
        edges_num = len(edges)
        vertex_edges = [edge for vertex in self.vertices for edge in vertex]
        crossing_edges = [edge for cross in self.crossings for edge in cross]
        paths = [[x] for x in list(set(vertex_edges) - set(crossing_edges))]
        checked = []
        while len(checked) < edges_num:

            for vert in self.vertices:
                if len(vert) == 2 and vert[0] == vert[1] and [vert[0]] not in paths:
                    paths.append([vert[0]])
            # searching for starting crossing
            path = []
            cross = []
            for cross in self.crossings:
                if cross[0] not in checked:
                    path += [cross[0], cross[2]]
                    break
            if not path:
                for cross in self.crossings:
                    if cross[1] not in checked:
                        path += [cross[1], cross[3]]
                        break

            while path and cross and len(checked) + len(path) < edges_num:
                non_found = True
                for c in self.crossings:
                    if path[-1] in c and c[c.index(path[-1]) - 2] not in path:
                        path.append(c[c.index(path[-1]) - 2])
                        non_found = False
                        break
                    if path[0] in c and c[c.index(path[0]) - 2] not in path:
                        path = [c[c.index(path[0]) - 2]] + path
                        non_found = False
                        break
                    if path[-1] in c and path[-1] in c[c.index(path[-1])+1:]:
                        ind = c.index(path[-1]) + c[c.index(path[-1])+1:].index(path[-1]) + 1
                        non_found = False
                        if c[ind-2] in path:
                            non_found = True
                            break
                        path.append(c[ind-2])
                    if path[0] in c and path[0] in c[c.index(path[0])+1:]:
                        ind = c.index(path[0]) + c[c.index(path[0])+1:].index(path[0]) + 1
                        non_found = False
                        if c[ind-2] in path:
                            non_found = True
                            break
                        path = [c[ind-2]] + path
                    if path[-1] in c and c[c.index(path[-1]) - 2] == path[0] and c != cross:
                        non_found = True
                        break
                if non_found or path[-1] in vertex_edges and path[0] in vertex_edges:
                    break
            if path:
                paths.append(path)
            checked = [item for sublist in paths for item in sublist]
        # adding base points for each component
        for k in range(len(paths)):
            path = paths[k]
            vertices = [vert for vertex in self.vertices for vert in vertex]
            if not set(path) & set(vertices):
                ind = max([edge for cross in self.crossings for edge in cross] + vertices) + 1
                self.vertices.append([path[0], ind])
                for l in range(len(self.crossings)):
                    cross = self.crossings[l]
                    if path[0] in cross and path [-1] in cross:
                        cross[cross.index(path[0])] = ind
                        self.crossings[l] = cross
                        break
                path.append(ind)
                self.update_pdcode()
        self.orientation = paths
        return

    def update_pdcode(self):
        code = ''
        for vert in self.vertices:
            code += 'V[' + ','.join([str(self.edge_colors.get(x,x)) for x in vert]) + '];'
        for cross in self.crossings:
            code += 'X[' + ','.join([str(self.edge_colors.get(x,x)) for x in cross]) + '];'
        self.pdcode = code[:-1]

    def update(self, trans={}):
        # filling in the untranslated edges
        for key in self.edges:
            if key not in trans.keys():
                trans[key] = key

        # making the translation
        self.crossings = [[trans[c[i]] for i in range(4)] for c in self.crossings]
        self.vertices = [[trans[v[i]] for i in range(len(v))] for v in self.vertices]
        self.update_pdcode()
        return

    def parse_substructure(self, arcs, abstract=False, output_type=OutputType.PDcode, arc_bridges=1):
        if abstract:
            function = self.generate_code_from_edges
        else:
            function = self.generate_coords_from_atom_list
        g = Graph(function(arcs))
        identifiers = [cut_arc(arc) for arc in arcs]
        if not abstract and arc_bridges > 0 and \
                any([len(identifier.split('-')) > arc_bridges + 1 for identifier in identifiers]):
            del g
            return
        g.identifier = ';'.join(identifiers)        # TODO some tricky result in case of abstract. Is it OK?
        if not abstract and not g.closed:
            g.close(method=Closure.CLOSED)
            g.parse_closed()
        if type(output_type) is list:
            result = [g.print_data(output_type=o_type) for o_type in output_type]
        else:
            result = g.print_data(output_type=output_type)
        del g
        return result

    def find_commons(self, arcs, abstract=False):
        if not abstract:
            result = set(arcs[-1])
            for k in range(len(arcs)-1):
                result = result & set(arcs[k])
            return list(result)
        else:
            results = []
            multi_vertices = [vertex for vertex in self.vertices if len(vertex) > 2]
            for vert in multi_vertices:
                commons = [set(vert) & set(arc) != set() for arc in arcs]
                if True in commons and True in commons[:commons.index(True)] + commons[commons.index(True)+1:]:
                    results.append(vert)
                    continue
            return results

    def find_loop_connections(self, arcs, abstract=False):
        result = []
        if not abstract:
            for v1 in arcs[0]:
                for v2 in arcs[1]:
                    result.append(find_path(v1, v2, self.spatial_graph))
        else:
            for k1, k2 in combinations(range(len(self.vertices)), 2):
                v1 = self.vertices[k1]
                v2 = self.vertices[k2]
                if (set(v1) & set(arcs[0]) and set(v2) & set(arcs[1])) or \
                        (set(v2) & set(arcs[0]) and set(v1) & set(arcs[1])):
                    for path in find_path(k1, k2, self.abstract_graph):
                        if all([len(set(path) & set(arc)) == 0 for arc in arcs]):
                            result.append(path)
        return result

    def decide_finding_type(self, output_type):
        if not self.coordinates:    # abstract code
            graph, abstract = self.abstract_graph, True
            if output_type not in [OutputType.PDcode, OutputType.EMcode]:
                raise TopolyException("Cannot generate the coordinates (yet)! "
                                      "Please choose output_type=OutputType.PDcode.")
        else:                       # graph with coordinates
            graph, abstract = self.spatial_graph, False
        vertices = list(graph.keys())

        return graph, abstract, vertices

    def find_loops(self, output_type=OutputType.PDcode, arc_bridges=1, output='list', file_prefix='loop',
                        folder_prefix=''):
        # different cases if we start from coordinates, or from abstract code
        graph, abstract, vertices = self.decide_finding_type(output_type)
        found = []

        # first option - loop on one vertex
        for v in vertices:
            for path in find_path(v, v, graph):
                edges = set(path)
                if edges in found:
                    continue
                if not abstract:
                    path = [v] + path
                result = self.parse_substructure([path], abstract=abstract, output_type=output_type,
                                                 arc_bridges=arc_bridges)

                if result:
                    yield result
                    found.append(edges)

        # second case, loop as two arcs joining the same pair of vertices
        for v1, v2 in combinations(vertices, 2):
            for arc1, arc2 in combinations([path for path in find_path(v1, v2, graph)], 2):
                if not abstract:
                    arc1 = [v1] + arc1[:-1]
                    arc2 = [v1] + arc2
                loop = arc1 + list(reversed(arc2))

                if set(arc1) & set(arc2) != {v1} or set(loop) in found:
                    continue
                result = self.parse_substructure([loop], abstract=abstract, output_type=output_type,
                                                 arc_bridges=arc_bridges)
                if result:
                    yield result
                    found.append(set(loop))
        return

    def find_links(self, output_type=OutputType.PDcode, arc_bridges=1, components=2):
        if self.coordinates:
            abstract = False
            o_type = OutputType.ATOMS
        else:
            abstract = True
            o_type = OutputType.PDcode
        found = []

        for pot_link in combinations(self.find_loops(output_type=o_type, arc_bridges=arc_bridges, output='generator'),
                                     components):
            if self.find_commons(pot_link, abstract):
                continue
            if abstract:
                arcs = [list(set([int(_) for _ in re.sub('[VX\[\]]', '', component).replace(';', ',').split(',')]))
                        for component in pot_link]
            else:
                arcs = list(pot_link)
                arcs = [[arc[-1]] + arc for arc in arcs]
            edges = [edge for arc in arcs for edge in arc]
            result = self.parse_substructure(arcs, abstract=abstract, output_type=output_type,
                                             arc_bridges=arc_bridges)

            if result:
                yield result
                found.append(set(edges))
        return

    def find_handcuffs(self, output_type=OutputType.PDcode, arc_bridges=1):
        graph, abstract, vertices = self.decide_finding_type(output_type)
        found = []

        for v1, v2 in combinations(vertices, 2):
            for arc1 in find_path(v1, v1, graph):
                if not abstract:
                    arc1 = [v1] + arc1
                for arc2 in find_path(v1, v2, graph):
                    if not abstract:
                        arc2 = [v1] + arc2
                    for arc3 in find_path(v2, v2, graph):
                        if not abstract:
                            arc3 = [v2] + arc3
                        arcs = [arc1, arc2, arc3]
                        edges = sorted([sorted(arc) for arc in arcs])
                        if edges not in found and set(arc1) & set(arc2) == {v1} and set(arc2) & set(arc3) == {v2} and \
                                set(arc1) & set(arc3) == set():
                            result = self.parse_substructure(arcs, abstract=abstract, output_type=output_type,
                                                             arc_bridges=arc_bridges)
                            if result:
                                yield result
                                found.append(set(edges))
        return

    def find_thetas(self, output_type=OutputType.PDcode, arc_bridges=1):
        graph, abstract, vertices = self.decide_finding_type(output_type)
        found = []

        for v1, v2 in combinations(vertices, 2):
            for arc1, arc2, arc3 in combinations([path for path in find_path(v1, v2, graph)], 3):
                if not abstract:
                    arc1, arc2, arc3 = [v1] + arc1, [v1] + arc2, [v1] + arc3
                arcs = [arc1, arc2, arc3]
                edges = sorted([sorted(arc) for arc in arcs])
                verts = {v1, v2}
                if edges not in found and set(arc1) & set(arc2) <= verts and set(arc2) & set(arc3) <= verts and\
                        set(arc1) & set(arc3) <= verts:
                    result = self.parse_substructure(arcs, abstract=abstract, output_type=output_type,
                                                     arc_bridges=arc_bridges)
                    if result:
                        yield result
                        found.append(set(edges))
        return

    def find_noloop_edges(self):
        noloop = []
        for e in self.edges:
            n = 0
            for v in self.vertices:
                if e in v:
                    n += 1
            if n == 2:
                noloop.append(e)
        return noloop

    def find_connected_components(self):
        # 0.1 case
        if len(self.crossings) == 0 and len(self.vertices) == 0:
            return [set()]
        connected = []
        # connected are 0-2 and 1-3
        for c in self.crossings:
            connected.append((c[0], c[2]))
            connected.append((c[1], c[-1]))
        # vertex connects edges
        for v in self.vertices:
            connected.append(tuple(v))
        return find_connections(connected)

    def find_disjoined_components(self):
        components = self.find_connected_components()
        for cross in self.crossings:
            k = 0
            while k < len(components):
                l = k + 1
                while l < len(components):
                    if set(cross) & components[k] and set(cross) & components[l]:
                        components[k] |= components[l]
                        components.pop(l)
                    l += 1
                k += 1
        subgraphs = ['' if len(element) != 0 else 'V' for element in components]
        for k in range(len(components)):
            for vertex in self.vertices:
                if len(vertex) > 0 and all(v in components[k] for v in vertex):
                    subgraphs[k] += 'V' + str([int(_) for _ in vertex]).replace(' ', '') + ';'
            for cross in self.crossings:
                if all(c in components[k] for c in cross):
                    subgraphs[k] += 'X' + str([int(_) for _ in cross]).replace(' ', '') + ';'
        subgraphs = [x[:-1] for x in subgraphs]
        return subgraphs

    def find_crossing_sign(self, n):
        signs = [0, 0]
        for path in self.orientation:
            if self.crossings[n][1] in path:
                signs[1] = path.index(self.crossings[n][1]) - path.index(self.crossings[n][3])
            if self.crossings[n][0] in path:
                signs[0] = path.index(self.crossings[n][2]) - path.index(self.crossings[n][0])
        for k in range(2):
            if signs[k] < -1:
                signs[k] = 1
            elif signs[k] > 1:
                signs[k] = -1
        return signs[0] * signs[1]

    def find_reidemeister_1(self, num_cross=-1):
        # num_cross is the number of crossings to be returned
        crossings = []
        for k in range(len(self.crossings)):
            c = self.crossings[k]
            for i in range(4):
                if c[i - 1] == c[i]:  # crossing to be reduced:
                    crossings.append([k, i])
                    break
            if len(crossings) == num_cross:
                return crossings
        return crossings

    def find_reidemeister_1v(self, num_cross=-1):
        # num_cross is the number of crossings to be returned
        crossings = []
        for l in range(len(self.crossings)):
            c = self.crossings[l]
            for k in range(len(self.vertices)):
                v = self.vertices[k]
                if len(v) == 2:
                    for i in range(4):
                        if [c[i], c[i - 1]] == v or [c[i - 1], c[i]] == v:
                            crossings.append([l, i, k])
                            break
            if len(crossings) == num_cross:
                return crossings
        return crossings

    def find_reidemeister_2(self, num_cross=-1):
        # num_cross is the number of crossings to be returned
        crossings = []
        for k in range(len(self.crossings)):
            c1 = self.crossings[k]
            for j in range(k):
                c2 = self.crossings[j]
                for i in range(4):
                    if c1[i] == c2[i] and c1[i - 1] == c2[i - 3]:
                        crossings.append([k, j, c1[i], c1[i - 1]])
                        break
                    elif c1[i] == c2[i] and c1[i - 3] == c2[i - 1]:
                        crossings.append([k, j, c1[i], c1[i - 3]])
                        break
                if len(crossings) == num_cross:
                    return crossings
        return crossings

    def find_reidemeister_2v(self, num_cross=-1):
        # num_cross is the number of crossings to be returned
        crossings = []
        for l in range(len(self.vertices)):
            v = self.vertices[l]
            if len(v) == 2:
                for k in range(len(self.crossings)):
                    c1 = self.crossings[k]
                    for j in range(k):
                        c2 = self.crossings[j]
                        for i in range(4):
                            if c1[i] == c2[i] and ([c1[i - 1], c2[i - 3]] == v or [c2[i - 3], c1[i - 1]] == v):
                                crossings.append([k, j, c1[i], l])
                                break
                            elif c1[i - 1] == c2[i - 3] and ([c1[i], c2[i]] == v or [c2[i], c1[i]] == v):
                                crossings.append([k, j, c1[i - 1], l])
                                break
                            elif c1[i] == c2[i] and ([c1[i - 3], c2[i - 1]] == v or [c2[i - 1], c1[i - 3]] == v):
                                crossings.append([k, j, c1[i], l])
                                break
                            elif c1[i - 3] == c2[i - 1] and ([c1[i], c2[i]] == v or [c2[i], c1[i]] == v):
                                crossings.append([k, j, c1[i - 3], l])
                                break
                        if len(crossings) == num_cross:
                            return crossings
        return crossings

    def find_reidemeister_3(self, num_cross=-1):
        # num_cross is the number of crossings to be returned
        crossings = []
        for i in range(len(self.crossings)):
            for j in range(i):
                for k in range(j):
                    c1, c2, c3 = self.crossings[i], self.crossings[j], self.crossings[k]
                    for m in range(4):
                        # checking if the crosings form a triangle
                        if c1[m] in c3 and c1[m - 1] in c2 and c3[(c3.index(c1[m]) - 3) % 4] in c2:
                            c3, c2 = c2, c3
                        if c1[m] in c2 and c1[m - 1] in c3 and c2[(c2.index(c1[m]) - 3) % 4] in c3:
                            # the edges have to be consecutive counterclockwise
                            if c3.index(c1[m - 1]) - c3.index(c2[(c2.index(c1[m]) - 3) % 4]) not in (1, -3):
                                continue
                            comm12 = c1[m]
                            comm13 = c1[m - 1]
                            comm23 = c2[(c2.index(c1[m]) - 3) % 4]
                            if (1, 1) not in [(c1.index(comm12) % 2, c2.index(comm12) % 2),
                                              (c1.index(comm13) % 2, c3.index(comm13) % 2),
                                              (c2.index(comm23) % 2, c3.index(comm23) % 2)]:
                                continue
                            crossings.append(
                                [self.crossings.index(c1), self.crossings.index(c2), self.crossings.index(c3), comm12,
                                 comm13, comm23])
                            break
                    if len(crossings) == num_cross:
                        return crossings
        return crossings

    def find_reidemeister_4(self, num_cross=-1):
        # num_cross is the number of crossings to be returned
        crossings = []
        for i in range(len(self.crossings)):
            for j in range(i):
                for k in range(len(self.vertices)):
                    c1, c2, v = self.crossings[i], self.crossings[j], self.vertices[k]
                    if len(v) != 3:
                        continue
                    for l in range(3):
                        if v[l] in c2 and v[l - 1] in c1:
                            c1, c2 = c2, c1
                        if v[l] in c1 and v[l - 1] in c2:
                            i1 = (c1.index(v[l]) - 3) % 4
                            i2 = (c2.index(v[l - 1]) - 1) % 4
                            if c1[i1] == c2[i2] and (i1 % 2) == (i2 % 2):
                                comm12 = c1[i1]
                                comm1v = v[l]
                                comm2v = v[l - 1]
                                crossings.append(
                                    [k, self.crossings.index(c1), self.crossings.index(c2), comm12, comm1v, comm2v])
                                break
                    if len(crossings) == num_cross:
                        return crossings
        return crossings

    def find_reidemeister_5(self, num_cross=-1):
        # num_cross is the number of crossings to be returned
        crossings = []
        for k in range(len(self.crossings)):
            c = self.crossings[k]
            for j in range(len(self.vertices)):
                v = self.vertices[j]
                if len(v) != 3:
                    continue
                for i in range(4):
                    if c[i] in v and c[i - 1] in v and abs(v.index(c[i]) - v.index(c[i - 1])) in [1, len(v) - 1]:
                        if i % 2 == 0:
                            crossings.append([j, k, i, i - 1])
                        else:
                            crossings.append([j, k, i - 1, i])
                        break
                if len(crossings) == num_cross:
                    return crossings
        return crossings

    ''' Graph manipulation '''

    def cut_chain(self, beg=-1, end=-1):
        if beg < 0:
            beg = min(list(self.coordinates.keys()))
        if end < 0:
            end = max(list(self.coordinates.keys()))
        coordinates = [[key] + self.coordinates[key] for key in range(beg, end + 1) if key in self.coordinates.keys()]
        return coordinates

    def close(self, method=Closure.TWO_POINTS, direction=0, debug=False):
        if self.closed:
            return
        if not self.coordinates:
            raise NotImplementedError('No coordinates - nothing to close (yet).')
        if not self.coordinates_c:
            self.generate_coordinates_c()
        if debug:
            print("Closure method: " + str(method))
        #for k in range(len(self.coordinates_c)):
        #    self.chain_c_close(method, direction, k)
        if len(self.coordinates_c)==1:
            self.chain_c_close(method, direction, 0)
        else:
            self.chains_c_close(method, direction)

        self.closed = True
        self.generate_coords_from_c()
        if debug:
            print(self.coordinates)
        return


    def fix_indices(self, chain):
        indices = []
        overlapping_indices = []
        to_add = []
        for k in range(len(chain)):
            atom = chain[k]
            ind = int(atom['id'])
            #indices.append(ind)
            #if ind == 0:
            #    overlapping_indices.append(k)
            if ind in indices:
                overlapping_indices.append(k)
            else:
                indices.append(ind)
        for k in range(len(overlapping_indices)-1, -1, -1):
            ind = overlapping_indices[k]
            atom = chain.pop(ind)
            atom['id'] = max(indices) + k + 1
            to_add.append(atom)
        chain = chain + list(reversed(to_add))
        return chain


    def chain_c_close(self, method=Closure.TWO_POINTS, direction=0, k=0):
        if method == Closure.MASS_CENTER:
            res, chain = close_chain_out(self.coordinates_c[k])
            chain = self.fix_indices(chain)
        elif method == Closure.ONE_POINT:
            res, chain = close_chain_1point(self.coordinates_c[k])
        elif method == Closure.TWO_POINTS:
            res, chain = close_chain_2points(self.coordinates_c[k])
        elif method == Closure.RAYS:
            res, chain = close_chain_1direction(self.coordinates_c[k])
        elif method == Closure.DIRECTION:
            res, chain = close_chain_1direction_no_random(self.coordinates_c[k], direction)
        elif method == Closure.CLOSED:
            res, chain = 0, self.coordinates_c[k]
        else:
            raise TopolyException('Unknown closing method ' + method)
        self.coordinates_c[k] = chain
        return

    def chains_c_close(self, method=Closure.TWO_POINTS, direction=0):
        if method == Closure.MASS_CENTER:
            res, chains = close_chains_out(self.coordinates_c)
            for i in range(len(self.coordinates_c)):
                 self.coordinates_c[i] = self.fix_indices(self.coordinates_c[i])
        elif method == Closure.ONE_POINT:
            res, chains = close_chains_1point(self.coordinates_c)
        elif method == Closure.TWO_POINTS:
            res, chains = close_chains_2points(self.coordinates_c)
        elif method == Closure.RAYS:
            res, chains = close_chains_1direction(self.coordinates_c)
        elif method == Closure.CLOSED:
            res, chains = 0, self.coordinates_c
        else:
            raise TopolyException('Unknown closing method ' + method)
        self.coordinates_c = chains
        return

    def reidemeister_1(self, arg_list, debug=False):
        ci, i = arg_list
        # ci is the index of the crossing to be reduced
        # i is the index of the edge in the crossing to be reduced
        # so self.crossings[ci][i] == self.crossings[ci][i-1]
        trans = {self.crossings[ci][i - 2]: self.crossings[ci][i - 3]}
        if i % 2 == 1:
            n = 1
        else:
            n = -1
        if debug:
            print("Reidemeister 1:\tRemoving crossing " + str(self.crossings[ci]) +
                  ". Updating: " + str(trans) + ". Sign " + str(n) + ".")
        self.crossings.pop(ci)
        self.update(trans)
        self.generate_orientation()
        if debug:
            print("\tResult: " + self.pdcode)
        return n

    def reidemeister_1v(self, arg_list, debug=False):
        ci, i, vi = arg_list
        # ci is the index of the crossing to be reduced
        # i is the index of the edge in the crossing to be reduced
        # vi is the index of the vertex to be removed
        # so self.crossings[ci][i] == self.crossings[ci][i-1]
        if i % 2 == 1:
            n = 1
        else:
            n = -1
        v0 = self.vertices[vi]
        v = [self.crossings[ci][i - 2], self.crossings[ci][i - 3]]
        if debug:
            print("Reidemeister 1:\tRemoving crossing " + str(self.crossings[ci]) + ". Swapping vertices: " + str(
                v0) + " -> " + str(v) + ". Sign " + str(n) + ".")
        self.crossings.pop(ci)
        self.vertices.pop(vi)
        self.vertices.append(v)
        self.update()
        self.generate_orientation()
        if debug:
            print("\tResult: " + self.pdcode)
        return n

    def reidemeister_2(self, arg_list, debug=False):
        c1, c2, comm1, comm2 = arg_list
        # c1 and c2 are the indices of the crossings to be reduced
        # comm1 and comm2 are the common edges in the crossings
        cross1 = self.crossings[c1]
        cross2 = self.crossings[c2]
        if cross1[cross1.index(comm1) - 2] == cross1[cross1.index(comm2) - 2]:
            cross2, cross1 = cross1, cross2
        v1 = [cross1[cross1.index(comm1) - 2], cross2[cross2.index(comm1) - 2]]
        v2 = [cross1[cross1.index(comm2) - 2], cross2[cross2.index(comm2) - 2]]

        if debug:
            print("Reidemeister 2:\tRemoving crossings " + str(self.crossings[c1]) + ", " +
                str(self.crossings[c2]) + ". Adding vertices: V" + str(
                    v1) + " and V" + str(v2) + ".")
        for cross in list(reversed(sorted([c1, c2]))):
            self.crossings.pop(cross)
        self.vertices.append(v1)
        self.vertices.append(v2)
        self.update()
        self.remove_double_verts()
        self.generate_orientation()

        if debug:
            print("\tResult: " + self.pdcode)
        return

    def reidemeister_2v(self, arg_list, debug=False):
        c1, c2, comm, vi = arg_list
        # c1 and c2 are the indices of the crossings to be reduced
        # comm1 and comm2 are the common edges in the crossings
        # vi is the index of vertex to be removed
        cross1 = self.crossings[c1]
        cross2 = self.crossings[c2]
        v = self.vertices[vi]
        if cross1[cross1.index(comm) - 2] == cross1[cross1.index(comm) - 2]:
            cross2, cross1 = cross1, cross2
        if v[1] in cross1:
            v = [v[1], v[0]]
        v1 = [cross1[cross1.index(comm) - 2], cross2[cross2.index(comm) - 2]]
        v2 = [cross1[cross1.index(v[0]) - 2], cross2[cross2.index(v[1]) - 2]]

        if debug:
            print("Reidemeister 2v:\tRemoving crossings " + str(self.crossings[c1]) + ", " + str(self.crossings[c2]) +
                  ", and vertex " + str(self.vertices[vi]) + ". Adding vertices: V" + str(v1) + " and V" +
                  str(v2) + ".")
        # Updating: " + str(trans) + "." + str(v1) + ' ' + str(v2))
        for cross in list(reversed(sorted([c1, c2]))):
            self.crossings.pop(cross)
        self.vertices.pop(vi)
        self.vertices.append(v1)
        self.vertices.append(v2)
        self.update()
        self.remove_double_verts()
        self.generate_orientation()
        if debug:
            print("\tResult: " + self.pdcode)
        return

    def reidemeister_3(self, arg_list, debug=False):
        c1, c2, c3, comm12, comm13, comm23 = arg_list
        # c1, c2, c3 are the indices of the crossings to be reduced
        # comm12, comm13, and comm23 are the common edges between the crossings
        cross1 = self.crossings[c1]
        cross2 = self.crossings[c2]
        cross3 = self.crossings[c3]

        # new crossings
        cn1 = [c for c in cross1]
        cn1[cross1.index(comm12) - 2] = cross2[cross2.index(comm12) - 2]
        cn1[cross1.index(comm13) - 2] = cross3[cross3.index(comm13) - 2]
        cn2 = [c for c in cross2]
        cn2[cross2.index(comm12) - 2] = cross1[cross1.index(comm12) - 2]
        cn2[cross2.index(comm23) - 2] = cross3[cross3.index(comm23) - 2]
        cn3 = [c for c in cross3]
        cn3[cross3.index(comm13) - 2] = cross1[cross1.index(comm13) - 2]
        cn3[cross3.index(comm23) - 2] = cross2[cross2.index(comm23) - 2]

        if debug:
            print("Reidemeister 3:\tRemoving crossing " + str(self.crossings[c1]) + ", " + str(self.crossings[c2]) +
                  ", " + str(self.crossings[c3]) + ". Adding: " + str(cn1) + ", " + str(cn2) + ", " + str(cn3) + ".")

        # updating the list of crossings
        for i in list(reversed(sorted([c3, c2, c1]))):
            self.crossings.pop(i)
        for c in [cn1, cn2, cn3]:
            self.crossings.append(c)
        self.update_pdcode()
        self.check_crossings_vs_orientation()
        if debug:
            print("\tResult: " + self.pdcode)
        return

    def reidemeister_4(self, arg_list, debug=False):
        vi, c1, c2, comm12, comm1v, comm2v = arg_list
        # vi, c1, and c2 are the indices of the vertex and edges to be reduced
        # comm12, comm1v, and comm2v are the edges common between the crossings and crossings and vertex

        cross1 = self.crossings[c1]
        cross2 = self.crossings[c2]
        v = self.vertices[vi]
        miss = list(set(v) - {comm1v, comm2v})[0]  # TODO generalize for large number of crossings

        if (cross1.index(comm12) % 2) == 1:  # crosing over
            c = [miss, cross2[cross2.index(comm12) - 2], comm12, cross1[cross1.index(comm12) - 2]]
        else:  # crossing under
            c = [cross2[cross2.index(comm12) - 2], comm12, cross1[cross1.index(comm12) - 2], miss]
        vn = [comm12, cross2[cross2.index(comm2v) - 2], cross1[cross1.index(comm1v) - 2]]

        # updating data
        if debug:
            print("Reidemeister 4:\tRemoving crossing " + str(self.crossings[c1]) + ", " + str(self.crossings[c2]) +
                  " and vertex " + str(self.vertices[vi]) + ". Adding crossing: " + str(c) + " and vertex " +
                  str(vn) + ".")

        for cross in list(reversed(sorted([c1, c2]))):
            self.crossings.pop(cross)
        self.vertices.pop(vi)
        self.crossings.append(c)
        self.vertices.append(vn)
        self.update_pdcode()
        self.generate_orientation()

        if debug:
            print("\tResult: " + self.pdcode)
        return

    def reidemeister_5(self, arg_list, debug=False):
        vi, ci, i, j = arg_list
        # vi and ci are indices of the vertex and the crossing to be reduced
        # i and j are the indices of the edges in the crossing adjacent to the vertex
        # i is the undercrossing, j is the uppercrossing

        vert = self.vertices[vi]
        cross = self.crossings[ci]

        # new vertex
        vn = [v for v in vert]
        vn[vn.index(cross[i])] = cross[j - 2]
        vn[vn.index(cross[j])] = cross[i - 2]
        if i < j:
            n = 1
        else:
            n = -1

        if debug:
            print("Reidemeister 5:\tRemoving crossing " + str(self.crossings[ci]) + ". Updating vertex " +
                  str(self.vertices[vi]) + "->" + str(vn) + ". Sign " + str(n) + ".")

        self.crossings.pop(ci)
        self.vertices.pop(vi)
        self.vertices.append(vn)
        self.update_pdcode()
        self.generate_orientation()

        if debug:
            print("\tResult: " + self.pdcode)
        return n

    def invert_crossing(self, crossing):
        g = deepcopy(self)
        g.crossings.append(g.crossings[crossing][1:] + [g.crossings[crossing][0]])
        g.crossings.pop(crossing)
        g.update_pdcode()
        code = g.pdcode
        del g
        return code

    def invert(self):
        g = deepcopy(self)
        for k in range(len(self.crossings)):
            g.crossings.append(self.crossings[k][1:] + [self.crossings[k][0]])
            g.crossings.pop(0)
        g.update_pdcode()
        g.check_crossings_vs_orientation()
        code = g.pdcode
        del g
        return code

    def smooth_crossing(self, crossing, smoothing):
        # Smoothings denote the connection of edges. The edges are joined by two-valent vertices.
        # The unnecessary vertices are subsequently reduced.
        g = deepcopy(self)

        if smoothing == 0:
            g.vertices.append(g.crossings[crossing])
        if smoothing == 1:
            g.vertices.append(g.crossings[crossing][:2])
            g.vertices.append(g.crossings[crossing][2:4])
        if smoothing == -1:
            g.vertices.append([g.crossings[crossing][0], g.crossings[crossing][3]])
            g.vertices.append(g.crossings[crossing][1:3])

        # cleaning
        g.crossings.pop(crossing)
        g.remove_double_verts()

        code = g.pdcode
        del g

        # TODO handle missing loops
        return code

    def contract_edge(self, edge, debug=False):
        g = deepcopy(self)
        nvert = []
        to_remove = []
        for k in range(len(g.vertices)):  # to keep the orientation
            # TODO check the list additions
            if edge in g.vertices[k]:
                to_remove.append(k)
                if nvert:
                    nvert += g.vertices[k][g.vertices[k].index(edge) + 1:] + g.vertices[k][:g.vertices[k].index(edge)]
                    break
                else:
                    nvert = g.vertices[k][g.vertices[k].index(edge) + 1:] + g.vertices[k][:g.vertices[k].index(edge)]
        for k in list(reversed(to_remove)):
            g.vertices.pop(k)
        g.vertices.append(nvert)
        g.update_pdcode()
        code = g.pdcode
        del g
        return code

    def contract_edge_vertex(self, v, c, i):
        g = deepcopy(self)
        vert = g.vertices[v]
        cross = g.crossings[c]
        vert[vert.index(cross[i])] = cross[i - 3]
        vert[vert.index(cross[i - 1])] = cross[i - 2]
        g.vertices[v] = vert
        g.crossings.pop(c)
        code = g.pdcode
        del g
        return code

    def remove_noloop_edge(self, edge, debug=False):
        g = deepcopy(self)
        for v in g.vertices:
            if edge in v:
                v.pop(v.index(edge))
        g.edges.discard(edge)
        g.remove_double_verts()
        g.update_pdcode()
        code = g.pdcode
        del g
        return code

    def remove_loop(self, v, k):
        g = deepcopy(self)
        g.vertices[v].pop(k)
        g.vertices[v].pop(k - 1)
        g.remove_double_verts()
        code = g.pdcode
        del g
        return code

    def remove_edge_vertex(self, v, c, i):
        g = deepcopy(self)
        cross = g.crossings[c]
        to_remove = list(reversed(sorted([g.vertices[v].index(cross[i]), g.vertices[v].index(cross[i - 1])])))
        for k in to_remove:
            g.vertices[v].pop(k)
        trans = {cross[i - 2]: cross[i - 3]}
        g.crossings.pop(c)
        g.update(trans)
        code = g.pdcode
        del g
        return code

    def remove_double_verts(self):
        split_double_vertices = []
        trans = {}
        for component in self.find_connected_components():
            verts = []
            other_verts = False  # if there exists any vertex with valency > 2
            for k in range(len(self.vertices) - 1, -1, -1):
                vert = self.vertices[k]
                if any(v in component for v in vert):
                    if len(vert) > 2:
                        other_verts = True
                        continue
                    verts.append(k)
            if not other_verts:
                verts = verts[:-1]
            split_double_vertices.append(verts)

        # bulding translating dictionary
        for vert_list in split_double_vertices:
            for k in vert_list:
                vert = sorted(self.vertices[k])
                if vert[1] in trans.keys():
                    trans[vert[0]] = trans[vert[1]]
                elif vert[1] in [trans[key] for key in list(trans)]:
                    for key in list(trans):
                        if trans[key] == vert[1]:
                            trans[key] = vert[0]
                            break
                elif vert[0] in trans.keys():
                    for key in list(trans):
                        if key == vert[0]:
                            trans[vert[1]] = trans[key]
                else:
                    trans[vert[1]] = vert[0]

        # removing unnecessary vertices
        for vert_list in list(reversed(sorted(split_double_vertices))):
            for vert in vert_list:
                self.vertices.pop(vert)

        # updating
        self.update(trans)
        return

    ''' simplification'''
    def reduce(self, method=ReduceMethod.KMT, steps=1000, debug=False, closed=True):
        if method == ReduceMethod.KMT:
            #print("JESTEM_graph - WAZNE ZMIANA PARAMETRU CLOSED")

            self.coordinates_c = kmt_reduction_multi(self.coordinates_c, closed)

            '''
            for k in range(len(self.coordinates_c)):
                print("PRZED ",len(self.coordinates_c[k]),"; ",end="")

                #self.coordinates_c[k] = kmt_reduction(self.coordinates_c[k], self.closed)
                self.coordinates_c[k] = kmt_reduction(self.coordinates_c[k], closed)

                print("PO ",len(self.coordinates_c[k]),"; ",end="")
            '''
 
            self.generate_coords_from_c()
        elif method == ReduceMethod.REIDEMEISTER:
            self.simplify_reidemeister(steps=steps, debug=debug)
        elif method == ReduceMethod.EASY:
            self.simplify_reidemeister_deterministic(debug=debug)
        else:
            raise TopolyException("Unknown reduction method.")
        return

    def simplify_reidemeister(self, steps=1000, debug=False):
        # returns the power from Reidemeister moves 1 and 5
        # TODO implement moves 4.2, 4.3 and 4.4 from Yamada's paper!
        n = 0
        previous = [set([tuple(x) for x in self.vertices]), set([tuple(x) for x in self.crossings])]
        n += self.simplify_reidemeister_deterministic(debug=False)
        for step in range(steps):
            changed = False
            # do a R3 move if it reduces the number of crossings or a random R3 move, which will not give some previous graph
            crossings = self.find_reidemeister_3()
            if not crossings:
                break
            done = False  # if the move was done
            for cross in crossings:
                g = deepcopy(self)
                g.reidemeister_3(cross, debug=False)
                g.simplify_reidemeister_deterministic(debug=False)
                if len(g.crossings) < len(self.crossings):
                    previous.append([set([tuple(x) for x in self.vertices]), set([tuple(x) for x in self.crossings])])
                    self.reidemeister_3(cross, debug=False)
                    n += self.simplify_reidemeister_deterministic(debug=False)
                    done = True
                    changed = True
                    break
            # if no move reduces the complexity, make a random move, which does not lead to a previously seen structure
            if not done:
                random.shuffle(crossings)
                for cross in crossings:
                    g = deepcopy(self)
                    g.reidemeister_3(cross, debug=False)
                    data = [set([tuple(x) for x in g.vertices]), set([tuple(x) for x in g.crossings])]
                    if data not in previous:
                        self.reidemeister_3(cross, debug=False)
                        previous.append(
                            [set([tuple(x) for x in self.vertices]), set([tuple(x) for x in self.crossings])])
                        changed = True
                        break
                n += self.simplify_reidemeister_deterministic(debug=False)
            if not changed:
                break
        self.check_crossings_vs_orientation()
        return n

    def simplify_reidemeister_deterministic(self, debug=False):
        n = 0
        k = len(self.crossings) + 1
        while len(self.crossings) < k:
            k = len(self.crossings)
            for arg_list in list(reversed(self.find_reidemeister_1())):
                n += 2 * self.reidemeister_1(arg_list, debug=debug)
            for arg_list in list(reversed(self.find_reidemeister_1v(num_cross=1))):
                n += 2 * self.reidemeister_1v(arg_list, debug=debug)
            for arg_list in self.find_reidemeister_2(num_cross=1):
                self.reidemeister_2(arg_list, debug=debug)
            for arg_list in self.find_reidemeister_2v(num_cross=1):
                self.reidemeister_2v(arg_list, debug=debug)
            for arg_list in self.find_reidemeister_4(num_cross=1):
                self.reidemeister_4(arg_list, debug=debug)
            for arg_list in list(reversed(self.find_reidemeister_1())):
                n += 2 * self.reidemeister_1(arg_list, debug=debug)
            for arg_list in list(reversed(self.find_reidemeister_1v(num_cross=1))):
                n += 2 * self.reidemeister_1v(arg_list, debug=debug)
            for arg_list in self.find_reidemeister_5(num_cross=1):
                n += self.reidemeister_5(arg_list, debug=debug)
        return n

    ''' Printing '''
    def print_data(self, output_type=OutputType.PDcode):
        if OutputType == OutputType.ATOMS:
            return list(self.coordinates.keys())

        result = DataParser.print_data(self.coordinates, self.arcs, self.pdcode, self.emcode, output_type, self.identifier)
        return result

    ''' Plotting '''
    def plot(self, palette=Colors.Structure):
        if not TK:
            raise TopolyException("Plotting graphs for no TK support not implemented yet.")
        fig = plt.figure()
        ax = plt.axes(projection="3d")
        for k in range(len(self.arcs)):
            arc = self.arcs[k]
            if len(self.arcs) == 1 and self.closed:
                arc.append(arc[0])
            x = np.array([float(self.coordinates[_][0]) for _ in arc])
            y = np.array([float(self.coordinates[_][1]) for _ in arc])
            z = np.array([float(self.coordinates[_][2]) for _ in arc])
            if len(self.arcs) == 1:
                # ax.scatter3D(x, y, z, cmap=cm.get_cmap(palette.get('all', 'binary'), len(z)))
                ax.scatter3D(x, y, z, c=np.array(range(len(arc))), cmap='hsv')
                ax.plot(x, y, z)
            else:
                ax.plot3D(x, y, z, cmap=cm.get_cmap(palette.get('all', 'binary'), k))
        plt.show()
        return "Plot shown"

    def code_canonical(self, code):
        edges = []
        for element in code.split(';'):
            es = re.sub('[XV\[\]]', '', element).split(',')
            for edge in es:
                if edge not in edges:
                    edges.append(edge)
        res = ''
        for element in code.split(';'):
            es = re.sub('[XV\[\]]', '', element).split(',')
            res += element[0] + '['
            for edge in es:
                res += str(edges.index(edge)) + ','
            res = res[:-1] + '];'
        return res[:-1]


''' Static methods '''


def find_path(start, end, graph):
    fringe = [(start, [])]
    while fringe:
        state, path = fringe.pop()
        if path and state == end:
            yield path
            continue
        for next_state, edge_list in graph[state]:
            if edge_list and any([edge in path for edge in edge_list]):
                continue
            if next_state == start and (len(path) == 1 or start != end):
                continue
            fringe.append((next_state, path + edge_list))
    return


def find_connections(array):
    out = []
    while len(array) > 0:
        first, rest = array[0], array[1:]
        first = set(first)
        lf = -1
        while len(first) > lf:
            lf = len(first)
            rest2 = []
            for r in rest:
                if len(first.intersection(set(r))) > 0:
                    first |= set(r)
                else:
                    rest2.append(r)
            rest = rest2
        out.append(first)
        array = rest
    return out


def cut_arc(arc):
    result = [str(arc[0])]
    k = 1
    while k < len(arc):
        consecutive = False
        while k < len(arc) and abs(arc[k]-arc[k-1]) == 1:
            consecutive = True
            k += 1
        if consecutive:
            result += ['...', str(arc[k - 1])]
            if k < len(arc):
                result += ['-', str(arc[k])]
        else:
            result += ['-', str(arc[k])]
        k += 1
    return ''.join(result)
