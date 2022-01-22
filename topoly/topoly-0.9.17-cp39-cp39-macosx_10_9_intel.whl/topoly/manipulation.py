#!/usr/bin/python3
# -*- coding: utf-8 -*- 

"""
The module containing the functions to manipulate the results.
Includes transforming the codes, printing, importing, simplification, and plotting functions.

Pawel Dabrowski-Tumanski
p.dabrowski at cent.uw.edu.pl
27.06.2019
Refactoring by p.rubach at cent.uw.edu.pl
17.01.2020

Docs:
https://realpython.com/documenting-python-code/#docstring-types

The type used here: Google


Support in PyCharm:
https://www.jetbrains.com/help/pycharm/settings-tools-python-integrated-tools.html
- change default reStructuredText to Google

Docs will be published in: https://readthedocs.org/

"""

import re
import ctypes
import numpy as np
import os

from topoly.params import TopolyException, OutputType, Bridges
from topoly.plotting import Reader, KnotMap
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.Polypeptide import is_aa
from collections import Sequence
from itertools import chain, count
from scipy import ndimage
from itertools import combinations
from Bio import BiopythonWarning
import warnings
warnings.simplefilter('ignore', BiopythonWarning)

def list2dictionary(matrix, knot='', beg=0):
    result = {}
    for k in range(len(matrix)):
        line = matrix[k]
        for l in range(len(line)):
            ident = (k + beg, l + beg)
            if line[l] != 0:
                result[ident] = {knot: line[l]}     # line[l] = matrix[k][l] = data[ident+beg]
    return result


def merge_dictionaries(dict1, dict2):
    result = {}
    for ident in list(set(dict1.keys()) | set(dict2.keys())):
        result[ident] = dict1.get(ident, {}).update(dict2.get(ident, {}))
    return result


def knotprot2dictionary(data):
    result = {}
    lines = data.split('\n')
    result = {}
    for line in lines:
        if len(line) < 2 or 'HEAD' in line or 'UNKNOT' in line or line[0] == '#':
            continue
        d = line.strip().split()
        for i in range(2, len(d)-2):
            ident = (int(d[0]), int(d[1]))
            for knot in d[i].split(','):
                if knot == '0' or knot == '0_1':
                    continue
                probability = 0.9 - (i - 2) * 0.03
                if ident not in result.keys():
                    result[ident] = {}
                result[ident][knot] = round(probability,3)
    # the deterministic case
    if all([len(list(result[ident].keys())) == 1 for ident in result.keys()]) and all([list(result[ident].values())[0] >= 0.9 for ident in result.keys()]):
        for ident in result.keys():
            result[ident] = list(result[ident].keys())[0]
    return result


def strdict2dictionary(data):
    result = {}
    for line in data.splitlines():
        L = line.strip().split()
        if len(L) == 2:
            ident, knot_data = line.strip().split()
            ident = tuple([int(_) for _ in ident.split(',')])
            ident_data = {}
            for knot in knot_data.split(';'):
                knot_type, prob = knot.split(':')
                prob = float(prob)
                ident_data[knot_type] = prob
            result[ident] = ident_data

        else:
#Line = {(0, 68): {'1': 0.45, '1 -3 1': 0.45, '0': 0.05, '2 -5 2': 0.05}, (0, 48): {'1': 0.75, '1 -3 1': 0.2, '1 -1 1': 0.05}, (0, 28): {'1': 0.9, '1 -1 1': 0.1}, (20, 68): {'1': 0.9, '1 -3 1': 0.1}, (40, 68): {'1': 0.9, '1 -1 1': 0.1}}
            L = line[1:-2].split("}, ")
            for punkt in L:
                # punkt = "(0, 68): {'1': 0.45, '1 -3 1': 0.45, '0': 0.05, '2 -5 2': 0.05"
                ides, knot_data = punkt.split(": {")
                ides = ides[1:-1].split(", ")
                ident = (int(ides[0]), int(ides[1]))
                ident_data = {}
                for knot in knot_data.split(", "):
                    # knot = "'1 -3 1': 0.45"
                    poly, prob = knot.split(": ")
                    poly = poly[1:-1]
                    prob = float(prob)
                    ident_data[poly] = prob
                result[ident] = ident_data    

    return result


def data2dictionary(data, knot='', beg=0):
    if type(data) is dict:
        if data:
            key = list(data.keys())[0]
            if type(data[key]) is not list:
                return data
        result = {}
        for knot in data.keys():
            knot_dict = list2dictionary(data[knot], knot=knot, beg=beg)
            result = merge_dictionaries(result, knot_dict)
        return result
    elif type(data) is list:
        result = list2dictionary(data, knot=knot, beg=beg)
        return result
    elif type(data) is str and ':' in data:
        return strdict2dictionary(data)
    elif type(data) is str:
        return knotprot2dictionary(data)
    else:
        raise TopolyException("Unknown forma of the matrix")


def matrix_dominating(data):
    indices = [9999, -9999]
    minz = 9999
    for ident in data.keys():
        indices = [min(indices[0], ident[0]), max(indices[1], ident[1])]
    result = [[0 for k in range(indices[1]-indices[0]+1)] for l in range(indices[1]-indices[0]+1)]
    for ident in data.keys():
        mav_val, prob = 0, 0
        for value in data[ident].keys():
            if data[ident][value] > prob:
                prob = data[ident][value]
                max_val = float(value)
            result[ident[0]-indices[0]][ident[1]-indices[0]] = max_val
            minz = min(minz, max_val)
    return result, minz


def data2matrix(data):
    if type(data) is list:
        return data
    elif type(data) is str:
        data = data2dictionary(data)
    knots = set()
    indices = [9999, -9999]
    for ident in data:
        if type(data[ident]) is dict:
            knots |= set(data[ident].keys())
        else:
            knots |= {data[ident]}
        indices = [min(indices[0], ident[0]), max(indices[1], ident[1])]
    result = {}
    for knot in list(knots):
        result[knot] = [[0 for k in range(indices[1]-indices[0]+1)] for l in range(indices[1]-indices[0]+1)]
    for ident in data.keys():
        if type(data[ident]) is dict:
            for knot in data[ident].keys():
                result[knot][ident[0]-indices[0]][ident[1]-indices[0]] = data[ident][knot]
        else:
            result[data[ident]][ident[0] - indices[0]][ident[1] - indices[0]] = 1
    return result


def data2knotprot(data, beg=0, end=0, knot=''):
    if type(data) is list:
        data = data2dictionary(data, beg=beg, knot=knot)
    elif type(data) is str:
        return data
    elif type(data) is dict:
        key = list(data.keys())[0]
        if type(data[key]) is list:
            data = data2dictionary(data, beg=beg)
    indices = [element for ident in list(data.keys()) for element in ident]
    if beg <= 0:
        beg = min(indices)
    if end <= beg:
        end = max(indices)
    res = '# ' + str(beg) + ' ' + str(end) + ' >90 >87 >84 >81 >78 >75 >72 >69 >66 >63 >60 >57 >54 >51 >48 >45 >42 ' \
                                             '>39 >36 >33 >30 >27 >24 >21 >18 >15 >12 >9 >6 >3 >0 IN ' + str(beg) + \
          ' ' + str(end) + '\n'
    for key in sorted(data.keys()):
        res_line = list(key) + [0 for _ in range(32)] + list(key)
        knot = data[key]
        if type(knot) is dict:
            for k in knot.keys():
                if k == 'empty set':
                    continue
                ind = 32-int(min(100*knot[k], 90)/3)
                if res_line[ind] == 0:
                    res_line[ind] = k
                else:
                    res_line[ind] += ';' + k
        else:
            res_line[2] = knot
        res += ' '.join([str(_) for _ in res_line]) + '\n'
    return res


def data2string(matrix_result):
    if type(matrix_result) is dict:
        result = ''
        for subchain in matrix_result.keys():
            line_res = str(subchain[0]) + ',' + str(subchain[1]) + ' '
            if type(matrix_result[subchain]) is dict:
                for knot in matrix_result[subchain].keys():
                    line_res += knot + ':' + str(matrix_result[subchain][knot]) + ';'
            result += line_res[:-1] + '\n'
        return result[:-1]
    elif type(matrix_result) is list:
        result = '\n'.join([' '.join([_ for _ in line]) for line in matrix_result])
        return result
    else:
        return matrix_result


def plot_matrix(matrix, plot_ofile="KnotFingerPrintMap", plot_format="png", palette=None, arrows=True,
                cutoff=0.48, gridsize_cutoff=100, knot='', debug=False):
    if type(matrix) is str and os.path.isfile(matrix):
        with open(matrix, 'r') as myfile:
            data = myfile.read()
    else:
        data = matrix

    if debug:
        print("Initialization matrix plot")
    knotmap_data = Reader(data, cutoff=cutoff, knot=knot)
    unique_knots = knotmap_data.getUniqueKnots()
    knots_size = len(unique_knots)
    if len(unique_knots) == 0:
        raise TopolyException("Nothing to draw. Cowardly refuses to draw empty matrix.")

    knotmap = KnotMap(patches=knots_size, protstart=knotmap_data.seq_start, protlen=knotmap_data.seq_end,
                      rasterized=True, arrows=arrows, gridsize_cutoff=gridsize_cutoff)

    for knot in unique_knots:
        if debug:
            print("Adding patch for knot " + str(knot))
        patch = knotmap_data.getKnot(knot)
        knotmap.add_patch(patch, palette=palette)

    knotmap.saveFile(plot_ofile, plot_format=plot_format)
    knotmap.close()
    return "Matrix saved as " + plot_ofile + "." + plot_format


def find_spots_centers(matrix, gap_size=0, spot_size=20, cutoff=0.48):
    spots = {}
    if type(matrix) is str and os.path.isfile(matrix):
        with open(matrix, 'r') as myfile:
            data = myfile.read()
    else:
        data = matrix
    maps, knots, limits = divide_matrix_into_knots(data, cutoff)
    for k in range(len(maps)):
        map = maps[k]
        minX, maxX = limits[k]
        spot_knot = find_spots_single_knot(map, minX, maxX, gap_size=gap_size, spot_size=spot_size)
        if spot_knot:
            spots[knots[k]] = spot_knot
    return spots


def divide_matrix_into_knots(matrix, cutoff=0.48):
    maps = []
    knots = {}
    limits = []
    invert_knots = []
    if type(matrix) is not dict:
        matrix = data2dictionary(matrix)
    for ident in matrix:
        point = matrix[ident]
        if type(point) is dict:
            knot_types = list(point.keys())
        else:
            knot_types = [point]
        for knot in knot_types:
            if type(point) is dict and point[knot] < cutoff:
                continue
            if knot not in knots:
                knots[knot] = len(maps)
                maps.append([])
                limits.append([999999, -999999])
                invert_knots.append(knot)
            maps[knots[knot]].append(ident)
            limits[knots[knot]][0] = min(limits[knots[knot]][0], ident[0])
            limits[knots[knot]][1] = max(limits[knots[knot]][1], ident[1])
    return maps, invert_knots, limits


def find_spots_single_knot(map, minX, maxX, gap_size=0, spot_size=20):
    centers = []
    graph = prepare_graph_from_map(map, minX, maxX, gap_size)
    components = get_all_connected_groups(graph)
    for component in components:
        if len(component) < spot_size:
            continue
        image, minX, minY = make_image(component)
        distances = ndimage.distance_transform_edt(image)
        centers.append(find_center(distances, minX, minY))
    return centers


def prepare_graph_from_map(map, minX, maxX, gap_size):
    graph = {}
    for k in range(minX, maxX + 1):
        for l in range(minX, k):
            if (l, k) not in map:
                continue
            to_add = set()
            for s in range(1, gap_size+2):
                if (l, k-s) in map:
                    to_add.add((l, k-s))
                if (l-s, k) in map:
                    to_add.add((l-s, k))
                if (l, k+s) in map:
                    to_add.add((l, k + s))
                if (l+s, k) in map:
                    to_add.add((l+s, k))
            if to_add:
                graph[(l, k)] = to_add
    return graph


def get_all_connected_groups(graph):
    already_seen = set()
    result = []
    for node in graph:
        if node not in already_seen:
            connected_group, already_seen = get_connected_group(graph, node, already_seen)
            result.append(connected_group)
    return result


def get_connected_group(graph, node, already_seen):
    result = []
    nodes = {node}
    while nodes:
        node = nodes.pop()
        already_seen.add(node)
        nodes = (nodes | graph[node]) - already_seen
        result.append(node)
    return result, already_seen


def make_image(component):
    Xs = [x for x, y in component]
    Ys = [y for x, y in component]
    maxX = max(Xs)
    minX = min(Xs)
    maxY = max(Ys)
    minY = min(Ys)
    res = np.zeros((maxX - minX + 3, maxY - minY + 3))
    for el in component:
        res[el[0] + 1 - minX, el[1] + 1 - minY] = 1
    return res, minX, minY


def find_center(ar, minX, minY):
    result = np.where(ar == np.amax(ar))
    listOfCoords = list(zip(result[0] + minX - 1, result[1] + minY - 1))
    if listOfCoords:
        return listOfCoords[0]
    else:
        return []


def depth(seq):
    for level in count():
        if not seq:
            return level
        seq = list(chain.from_iterable(s for s in seq if isinstance(s, Sequence)))


def check_cuda():
    """
    It's a port of https://gist.github.com/f0k/0d6431e3faa60bffc788f8b4daa029b1
    Author: Jan Schlüter
    """
    libnames = ('libcuda.so', 'libcuda.dylib', 'cuda.dll')
    CUDA_SUCCESS = 0
    for libname in libnames:
        try:
            cuda = ctypes.CDLL(libname)
        except OSError:
            return False
        else:
            break
    else:
        return False

    nGpus = ctypes.c_int()
    result = cuda.cuInit(0)
    if result != CUDA_SUCCESS:
        return False
    result = cuda.cuDeviceGetCount(ctypes.byref(nGpus))
    if result != CUDA_SUCCESS:
        return False
    return True


def check_close(arcs):
    # checking if the structure has any tail, i.e. the vertex of valency < 2
    ends = {}
    #print("JESTEM w manipulation, check_close(), arcs: ",arcs)
    for arc in arcs:
        if arc[0] not in ends.keys():
            ends[arc[0]] = 0
        if arc[-1] not in ends.keys():
            ends[arc[-1]] = 0
        ends[arc[0]] += 1
        ends[arc[-1]] += 1
    for key in ends.keys():
        if ends[key] < 2:
            return False
    return True


def prepareArcsFromBreaks(coordinates, breaks, bridges):
    # preparing the arcs including the information in breaks and bridges
    if not breaks:
        breaks = []
    if not bridges:
        bridges = []
    beg = min(list(coordinates.keys()))
    end = max(list(coordinates.keys()))
    bridging_atoms = [atom for bridge in bridges for atom in bridge]
    arcs = []
    arc = []
    for k in range(beg, end + 1):
        if k == beg or k == end or k not in breaks + bridging_atoms:
            arc.append(k)
        elif k != beg and k != end and k in bridging_atoms:
            arc.append(k)
            arcs.append(arc)
            arc = [k]
        else:
            #arc.append(k)   #WANDA: if we were here, it would mean that k was in breaks, thus we do not want add it to an arc?
            #arcs.append(arc)
            if arc: arcs.append(arc)

            arc = []
    arcs.append(arc)
    arcs += [list(bridge) for bridge in bridges]
    return arcs


class DataAnalyzer:
    def __init__(self, data):
        self.data = data


class PDcodeDataParser(DataAnalyzer):
    def read(self):
        data = {'coordinates': {},
                'emcode': '',
                'pdcode': re.sub('\n', ';', self.data),
                'arcs': [],
                'closed': True,
                'breaks': [],
                'bridges': []}
        return data


class EMcodeDataParser(DataAnalyzer):
    def read(self):
        data = {'coordinates': {},
                'emcode': re.sub('\n', ';', self.data),
                'pdcode': '',
                'closed': True,
                'arcs': [],
                'breaks': [],
                'bridges': []}
        return data


class DictDataParser(DataAnalyzer):
    def read(self, bridges, breaks):
        coordinates = self.data
        arcs = prepareArcsFromBreaks(coordinates, breaks, bridges)

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': [],
                'bridges': [list(bridge) for bridge in bridges]}
        return data


class ListDataParser(DataAnalyzer):
    def read(self, bridges, breaks):
        if depth(self.data) == 3 and len(self.data[0][0]) == 4:
            return self.readArcsFourDim(bridges, breaks)
        elif depth(self.data) == 3 and len(self.data[0][0]) == 3:
            return self.readArcsThreeDim(bridges, breaks)
        elif depth(self.data) == 2 and len(self.data[0]) == 4:
            return self.readChainFourDim(bridges, breaks)
        elif depth(self.data) == 2 and len(self.data[0]) == 3:
            return self.readChainThreeDim(bridges, breaks)
        else:
            raise TypeError('Unrecognized format of the coordinate list. The input is expected as arcs = list of atoms,'
                            ' or list of arcs. The atoms are expected as 3 or 4 element lists.')

    def readArcsFourDim(self, bridges, breaks):
        indices = []
        coordinates = {}
        arcs = []
        # TODO Najlepiej by bylo dodac warning jak ponizej:
        # if bridges or breaks:
        #     WARNING: "The structure is completely determined by the coordinates. Disregarding the additional
        # information on bridges or breaks."
        for arc in self.data:
            arc_indices = []
            for atom in arc:
                try:
                    index = int(atom[0])
                    coords = [float(x) for x in atom[1:]]

                    #if there is already atom with the same coordinates we take its index
                    list_coords_val = list(coordinates.values())
                    if (coords in list_coords_val):
                        pos = list_coords_val.index(coords)
                        index = list(coordinates.keys())[pos]

                    #if there is already atom with the same index but different coords, we give new index to the current one
                    if (index in coordinates) and (coordinates[index] != coords):
                            index = max(coordinates)+1

                    coordinates[index] = coords
                    arc_indices.append(index)
                # TODO czy taka jest praktyka na wyjasnienie, skad moze pochodzic blad?
                except ValueError:
                    raise ValueError("The coordinates given in wrong format.")
            arcs.append(arc_indices)

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': [],
                'bridges': []}
        return data

    def readArcsThreeDim(self, bridges, breaks):
        indices = []
        coordinates = {}
        arcs = []
        # TODO Najlepiej by bylo dodac warning jak ponizej:
        # if bridges or breaks:
        #     WARNING: "The structure is completely determined by the coordinates. Disregarding the additional
        # information on bridges or breaks."
        for arc in self.data:
            arc_indices = []
            for atom in arc:
                pointer = ' '.join([str(x) for x in atom])
                if pointer in indices:
                    ind = indices.index(pointer)
                else:
                    ind = len(indices)
                    indices.append(pointer)
                try:
                    coordinates[ind] = [float(x) for x in atom]
                    arc_indices.append(ind)
                # TODO czy taka jest praktyka na wyjasnienie, skad moze pochodzic blad?
                except ValueError:
                    raise ValueError("The coordinates given in wrong format.")
            arcs.append(arc_indices)

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': [],
                'bridges': []}
        #print("JESTEM manipulation, coordinates = ",coordinates)
        return data

    def readChainFourDim(self, bridges, breaks):
        # reading the coordinates
        arc_indices = []
        coordinates = {}
        #print("JESTEM w manipulation, ListDataParser, dostane dane-indeksy: ", [x[0] for x in self.data])
        for atom in self.data:
            try:
                    index = int(atom[0])
                    coords = [float(x) for x in atom[1:]]

                    #if there is already atom with the same coordinates we take its index
                    list_coords_val = list(coordinates.values())
                    if (coords in list_coords_val):
                        pos = list_coords_val.index(coords)
                        index = list(coordinates.keys())[pos]

                    #if there is already atom with the same index but different coords, we give new index to the current one
                    if (index in coordinates) and (coordinates[index] != coords):
                            index = max(coordinates)+1

                    coordinates[index] = coords
                    arc_indices.append(index)
            # TODO czy taka jest praktyka na wyjasnienie, skad moze pochodzic blad?
            except ValueError:
                raise ValueError("The coordinates given in wrong format.")

        arcs = [arc_indices]
        if breaks or bridges:
             arcs = prepareArcsFromBreaks(coordinates, breaks, bridges)

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': breaks,
                'bridges': [list(bridge) for bridge in bridges]}
        return data

    def readChainThreeDim(self, bridges, breaks):
        # reading the coordinates
        coordinates = {}
        indices = []
        arc_indices = []
        for atom in self.data:
            pointer = ' '.join(str(atom))
            if pointer in indices:
                ind = indices.index(pointer)
            else:
                ind = len(indices)
                indices.append(pointer)
            try:
                coordinates[ind] = [float(x) for x in atom]
                arc_indices.append(ind)
            # TODO czy taka jest praktyka na wyjasnienie, skad moze pochodzic blad?
            except ValueError:
                raise ValueError("The coordinates given in wrong format.")

        arcs = [arc_indices]
        if breaks or bridges:
            arcs = prepareArcsFromBreaks(coordinates, breaks, bridges)

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': breaks,
                'bridges': [list(bridge) for bridge in bridges]}
        return data

class NxyzDataParser(DataAnalyzer):
    def read(self, breaks, bridges):
        coordinates = {}
        arcs = []
        arc = []
        for line in self.data.splitlines():
            if len(line) == 0:
                continue
            try:
                int(line.split()[0])
                first_int = True
            except ValueError:
                first_int = False
            if first_int:
                try:
                    coords = line.strip().split()
                    index = int(coords[0])

                    if (index in coordinates) and (coordinates[index] != [float(x) for x in coords[1:]]):
                            index = max(coordinates)+1

                    coordinates[index] = [float(x) for x in coords[1:]]
                    arc.append(index)
                # TODO czy taka jest praktyka na wyjasnienie, skad moze pochodzic blad?
                except ValueError:
                    raise ValueError("The coordinates given in wrong format.")
            else:
                if arc:
                    arcs.append(arc)
                    arc = []
            # TODO sprawdzic metode na kajdanusiach - Pawel D.

        if arcs and arc:
            arcs.append(arc)
        elif not arcs and (breaks or bridges):
            arcs = prepareArcsFromBreaks(coordinates, breaks, bridges)
        elif not arcs and not breaks and not bridges:
            arcs = [arc]

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': breaks,
                'bridges': [list(bridge) for bridge in bridges]}
        return data

    def print_arcs(self, arcs):
        result = ''
        for arc in arcs:
            for atom in arc:
                result += str(atom) + ' ' + ' '.join([str(_) for _ in self.data[atom]]) + '\n'
            result += 'X\n'
        return result[:-3]


class MathematicaDataParser(DataAnalyzer):
    def read(self):
        coordinates = {}
        arcs = []
        indices = []
        arc_coords = self.data.strip('"{}\n').split('}}","{{')
        for arc in arc_coords:
            arc_list = []
            atoms = arc.strip().replace('}}"','').split('}, {')
            for atom in atoms:
                pointer = atom.replace(',', '')
                if pointer in indices:
                    ind = indices.index(pointer)
                else:
                    ind = len(indices)
                    indices.append(pointer)
                arc_list.append(ind)
                coordinates[ind] = [float(_.replace('*^', 'E')) for _ in pointer.split()]
            arcs.append(arc_list)
            # TODO sprawdzic jak bedzie dzialac na kajdanusiach - Pawel D.

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': [],
                'bridges': []}
        return data

    def print_arcs(self, arcs):
        result = ''
        for arc in arcs:
            result += '"{'
            for atom in arc:
                result += '{' + ', '.join([str(_) for _ in self.data[atom]]) + '}, '
            result = result[:-2] + '}",'
        return result[:-1]


class PdbDataParser(DataAnalyzer):
    def __init__(self, data, model=None, chain=None, bridges_type=Bridges.SSBOND):
        self.data = data
        self.model = model
        self.chain = chain
        self.bridges_type = bridges_type
        self.ion_bridges = []

    def select_chain(self, structure):
        if not self.model and len(structure.get_list()) > 0:
            model = structure.get_list()[0]
        elif structure.has_id(self.model):
            model = structure[self.model]
        else:
            raise TopolyException('Selected model: ' + str(self.model) + ' does not exist in file: ' + str(self.data))
        if not self.chain and len(model.get_list()) > 0:
            self.chain = model.get_list()[0].get_id()
            return model.get_list()[0]
        elif model.has_id(self.chain):
            return model[self.chain]
        else:
            raise TopolyException('Selected chain: ' + str(self.chain) + ' does not exist in file: ' + str(self.data) +
                                  ' in model: ' + str(model.getid()))

    def identify_bridges(self):
        bridges_ion, bridges_covalent = [], []
        pdb_structure = PDBParser().get_structure('The name', self.data)
        chain = self.select_chain(pdb_structure)

        # extracting the covalent connections
        for bridge in self.ion_bridges:
            if abs(bridge[0]-bridge[1]) == 1:
                continue
            res1, res2 = '', ''
            for res in chain.get_list():
                if res.id[1] == bridge[0]:
                    res1 = res
                if res.id[1] == bridge[1]:
                    res2 = res
            if is_aa(res1) and is_aa(res2):
                bridges_covalent.append(bridge)

        # extracting the ion bridges
        for bridge1, bridge2 in combinations(self.ion_bridges, 2):
            external = list(set(bridge1) ^ set(bridge2))
            connecting = list(set(bridge1) & set(bridge2))
            if len(external) == 2 and len(connecting) == 1:
                res1, res3 = '', ''
                for res in chain.get_list():
                    if res.id[1] == external[0]:
                        res1 = res
                    if res.id[1] == external[1]:
                        res3 = res
                if is_aa(res1) and is_aa(res3) and abs(external[0]-external[1]) != 1:
                    bridges_ion.append(external)
        return bridges_ion, bridges_covalent

    def read(self):
        coordinates = {}
        bridges_disulfide = []
        pdb_structure = PDBParser().get_structure('The name', self.data)
        chain = self.select_chain(pdb_structure)
        for residue in chain.get_list():
            if residue.has_id("CA") and residue.id[0].strip() == '':
                ca = residue["CA"]
                coordinates[residue.id[1]] = list(ca.get_coord())
        with open(self.data, 'r') as myfile:
            data = myfile.read()
            for line in data.splitlines():
                if line[0:6] == 'SSBOND':
                    if line[15:17].strip() == self.chain and line[29:31].strip() == self.chain:
                        bridges_disulfide.append([int(line[17:21].strip()), int(line[31:35].strip())])
                elif line[0:4] == 'LINK':
                    if line[21:23].strip() == self.chain and line[51:53].strip() == self.chain:
                        self.ion_bridges.append([int(line[22:26]), int(line[52:56])])
                else:
                    continue

        bridges_ion, bridges_covalent = self.identify_bridges()

        if self.bridges_type == Bridges.ALL:
            bridges = bridges_disulfide + bridges_ion + bridges_covalent
        elif self.bridges_type == Bridges.COVALENT:
            bridges = bridges_covalent
        elif self.bridges_type == Bridges.ION:
            bridges = bridges_ion
        else:
            bridges = bridges_disulfide

        arcs = prepareArcsFromBreaks(coordinates, [], bridges)

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': [],
                'bridges': [list(bridge) for bridge in bridges]}
        return data

    def print_arcs(self, arcs):
        result = ''
        for arc in arcs:
            for atom in arc:
                x, y, z = self.data[atom]
                result += "ATOM  {:>5d}  CA  ALA A{:>4d}    {:>8.3f}{:>8.3f}{:>8.3f}  1.00  1.00           C\n".format(
                          atom, atom, x, y, z)
        return result[:-1]


class MMCIFDataParser(PdbDataParser):
    def clean_bridges_ion(self, bridges_ion):
        bridges = []
        for bridge1, bridge2 in combinations(bridges_ion, 2):
            external = list(set(bridge1[:2]) ^ set(bridge2[:2]))
            connecting = list(set(bridge1[:2]) & set(bridge2[:2]))
            res1 = bridge1[2 + ((bridge1.index(connecting[0]) - 2) + 1) % 2]
            res3 = bridge2[2 + ((bridge2.index(connecting[0]) - 2) + 1) % 2]
            if len(external) == 2 and len(connecting) == 1 and is_aa(res1) and is_aa(res3) and abs(external[0]-external[1]) != 1:
                bridges.append(external)
        return bridges

    def read(self):
        bridges_disulfide = []
        bridges_ion = []
        bridges_covalent = []
        coordinates = {}
        mmcif_dict = MMCIF2Dict(self.data)
        entry_id = mmcif_dict['data_'] if 'data_' in mmcif_dict.keys() else mmcif_dict['_entry.id'][0]
        cif_structure = MMCIFParser().get_structure(entry_id, self.data)
        for residue in self.select_chain(cif_structure).get_list():
            if residue.has_id("CA") and residue.id[0].strip() == '':
                ca = residue["CA"]
                coordinates[residue.id[1]] = list(ca.get_coord())
        ssbond_conn = mmcif_dict.get('_struct_conn.conn_type_id')
        chain_1_conn = mmcif_dict.get('_struct_conn.ptnr1_auth_asym_id')
        chain_2_conn = mmcif_dict.get('_struct_conn.ptnr2_auth_asym_id')
        if ssbond_conn:
            for idx, x in enumerate(ssbond_conn):
                if chain_1_conn[idx].strip() == self.chain and chain_2_conn[idx].strip() == self.chain:
                    if x == 'disulf':
                        bridges_disulfide.append([int(mmcif_dict['_struct_conn.ptnr1_auth_seq_id'][idx]),
                                    int(mmcif_dict['_struct_conn.ptnr2_auth_seq_id'][idx])])
                    elif x == 'covale':
                        bridges_covalent.append([int(mmcif_dict['_struct_conn.ptnr1_auth_seq_id'][idx]),
                                                  int(mmcif_dict['_struct_conn.ptnr2_auth_seq_id'][idx])])
                    elif x == 'metalc':
                        bridges_ion.append([int(mmcif_dict['_struct_conn.ptnr1_auth_seq_id'][idx]),
                                    int(mmcif_dict['_struct_conn.ptnr2_auth_seq_id'][idx]),
                                    mmcif_dict['_struct_conn.ptnr1_label_comp_id'][idx],
                                    mmcif_dict['_struct_conn.ptnr2_label_comp_id'][idx]])

        bridges_ion = self.clean_bridges_ion(bridges_ion)

        if self.bridges_type == Bridges.ALL:
            bridges = bridges_disulfide + bridges_ion + bridges_covalent
        elif self.bridges_type == Bridges.COVALENT:
            bridges = bridges_covalent + bridges_disulfide
        elif self.bridges_type == Bridges.ION:
            bridges = bridges_ion
        else:
            bridges = bridges_disulfide

        arcs = prepareArcsFromBreaks(coordinates, [], bridges)

        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': [],
                'bridges': [list(bridge) for bridge in bridges]}
        return data

    def print_arcs(self, arcs):
        result = ''
        for arc in arcs:
            for atom in arc:
                x, y, z = self.data[atom]
                result += "ATOM   {:<4d}C CA  . ALA A 1 {:<4d}? {:<8.3f}{:<8.3f}{:<8.3f}1.00  1.00 ? {:<4d}ALA A CA  " \
                          "1\n".format(atom, atom, x, y, z, atom)
        return result[:-1]


class PsfDataParser(DataAnalyzer):
    def read(self, breaks, bridges):
        coordinates = {}
        arcs = []
        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': breaks,
                'bridges': [list(bridge) for bridge in bridges]}
        return data

    def print_arcs(self, arcs):
        bond1, bond2 = None, None
        indexes = []
        bonds = []
        i = 0

        for arc in arcs:
            for atom in arc:
                bond2 = bond1
                bond1 = atom
                if bond1 and bond2:
                    bonds.append((bond2, bond1))
                if atom not in indexes:
                    indexes.append(atom)
            bond2 = bond1
            bond1 = None

        result = """\n                    PSF CMAP\n\n                        {:>4d}  !NATOM\n""".format(len(indexes))
        for index in indexes:
            result += ' {:>7d} A {:>7d}  GLY  CA  CA   0.000  1.000      0\n'.format(index, index)
        result += '\n    {:>4d} !NBOND: bonds\n'.format(len(bonds))
        for bond in bonds:
            i += 1
            result += ' {:>7d} {:>7d}'.format(bond[0], bond[1])
            if i % 4 == 0:
                result += '\n'
        return result


class XyzDataParser(DataAnalyzer):
    def read(self, breaks, bridges):
        coordinates = {}
        arcs = []
        indices = []
        arc = []
        for line in self.data.splitlines():
            if len(line) == 0:
                continue
            try:
                float(line.split()[0])
                first_float = True
            except ValueError:
                first_float = False
                # TODO Najlepiej by bylo dodac warning jak ponizej:
                # if bridges or breaks:
                #     WARNING: "The structure is completely determined by the input data. Disregarding the additional
                # information on bridges or breaks."
            if first_float:
                if line.strip() in indices:
                    ind = indices.index(line.strip())
                else:
                    ind = len(indices)
                    indices.append(line.strip())
                try:
                    coordinates[ind] = [float(x) for x in line.strip().split()]
                    arc.append(ind)
                # TODO czy taka jest praktyka na wyjasnienie, skad moze pochodzic blad?
                except ValueError:
                    raise ValueError("The coordinates given in wrong format.")
            else:
                if arc:
                    arcs.append(arc)
                    arc = []
        if arc and arc not in arcs:
            arcs.append(arc)
            # TODO sprawdzic metode na kajdanusiach - Pawel D.
        # preparing the data to return
        data = {'coordinates': coordinates,
                'emcode': '',
                'pdcode': '',
                'closed': check_close(arcs),
                'arcs': arcs,
                'breaks': breaks,
                'bridges': [list(bridge) for bridge in bridges]}
        return data

    def print_arcs(self, arcs):
        result = ''
        for arc in arcs:
            for atom in arc:
                try:
                    result += ' '.join([str(_) for _ in self.data[atom]]) + '\n'
                except KeyError:
                    continue
            result += 'X\n'
        return result[:-3]


class DataParser:
    format_dict = {
        'xyz': XyzDataParser,
        'nxyz': NxyzDataParser,
        'list': ListDataParser,
        'pdb': PdbDataParser,
        'cif': MMCIFDataParser,
        'mathematica': MathematicaDataParser,
        'pdcode': PDcodeDataParser,
        'emcode': EMcodeDataParser,
        'dict': DictDataParser
    }

    @classmethod
    def list_formats(cls):
        return cls.format_dict.keys()

    @classmethod
    def read_format(cls, data, orig_input, chain, model, bridges, breaks, bridges_type, debug):
        if isinstance(data, list):
            if debug:
                print("Recognized format as list.")
            return ListDataParser(data).read(bridges, breaks)
        elif isinstance(data, dict):
            if debug:
                print("Recognized format as dict.")
            return DictDataParser(data).read(bridges, breaks)
        elif not isinstance(data, str):
            raise TypeError('Unknown type of input data. Expected string or list.')

        lines = data.split('\n')
        first_line = lines[0]
        first_atom_line = ''
        for k in range(len(lines)):
            if lines[k][:4] == 'ATOM':
                first_atom_line = lines[k]
                break

        characters = set(re.split("[^a-zA-Z]+", data)) - {'V', ''}
        if len(lines) >= 3 and len(lines[2]) > 0 and lines[2].startswith('_entry.id'):
            if debug:
                print("Recognized format as CIF file.")
            # TODO Najlepiej by bylo dodac warning jak ponizej:
            # if bridges or breaks:
            #     WARNING: "The structure is completely determined by the input data. Disregarding the additional
            # information on bridges or breaks."
            return MMCIFDataParser(orig_input, chain=chain).read()
        elif first_atom_line and len(first_atom_line) < 81:
            if debug:
                print("Recognized format as PDB file.")
            # TODO Najlepiej by bylo dodac warning jak ponizej:
            # if bridges or breaks:
            #     WARNING: "The structure is completely determined by the input data. Disregarding the additional
            # information on bridges or breaks."
            return PdbDataParser(orig_input, chain=chain, model=model, bridges_type=bridges_type).read()
        elif '{' in data:
            if debug:
                print("Recognized format as Mathematica file.")
            # TODO Najlepiej by bylo dodac warning jak ponizej:
            # if bridges or breaks:
            #     WARNING: "The structure is completely determined by the input data. Disregarding the additional
            # information on bridges or breaks."
            return MathematicaDataParser(data).read()
        elif 'X[' in data or 'V[' in data:
            if debug:
                print("Recognized format as PD code.")
            return PDcodeDataParser(data).read()
        elif characters == {'a', 'b', 'c', 'd'}:
            if debug:
                print("Recognized format as EM code.")
            return EMcodeDataParser(data).read()
        elif len(first_line.split()) == 4 and first_line.split()[0].isdigit():
            return NxyzDataParser(data).read(breaks, bridges)
        else:
            return XyzDataParser(data).read(breaks, bridges)

    # TODO dodac wypisywanie PDB, PSF i MMCIF
    @classmethod
    def print_data(cls, coordinates, arcs, pdcode, emcode, output_type, ident):
        if output_type == OutputType.PDcode:
            return pdcode
        elif output_type == OutputType.ATOMS:
            return list(coordinates.keys())
        elif output_type == OutputType.EMcode:
            return emcode
        elif output_type == OutputType.NXYZ:
            return NxyzDataParser(coordinates).print_arcs(arcs)
        elif output_type == OutputType.PDB:
            return PdbDataParser(coordinates).print_arcs(arcs)
        elif output_type == OutputType.Mathematica:
            return MathematicaDataParser(coordinates).print_arcs(arcs)
        elif output_type == OutputType.MMCIF:
            return MMCIFDataParser(coordinates).print_arcs(arcs)
        elif output_type == OutputType.PSF:
            return PsfDataParser(coordinates).print_arcs(arcs)
        elif output_type == OutputType.IDENT:
            return ident
        elif output_type == OutputType.XYZ:
            return XyzDataParser(coordinates).print_arcs(arcs)
        else:
            raise TopolyException("Unknown output format (got " + str(output_type) + ")!")
