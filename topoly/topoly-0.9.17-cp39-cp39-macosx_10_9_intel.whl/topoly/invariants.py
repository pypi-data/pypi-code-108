"""
The module containing the functions for calculating the isotopy invariants starting from graphs. In particular,
it contains functions to calculate knot invariants (Jones, Alexander, HOMFLY-PT) and spatial graph invariants.

Pawel Dabrowski-Tumanski
p.dabrowski at cent.uw.edu.pl
04.09.2019

Docs:
https://realpython.com/documenting-python-code/#docstring-types

The type used here: Google


Support in PyCharm:
https://www.jetbrains.com/help/pycharm/settings-tools-python-integrated-tools.html
- change default reStructuredText to Google

Docs will be published in: https://readthedocs.org/

"""
from topoly.topoly_knot import *
from topoly.topoly_lmpoly import *
from topoly.topoly_gln import c_gln, c_gln_max, c_gln_average, c_gln_matrix
from topoly.graph import Graph
from topoly.manipulation import check_cuda, data2knotprot, data2string, data2matrix, data2dictionary, plot_matrix, matrix_dominating
from topoly.polvalues import polvalues
from topoly.params import Closure, ReduceMethod, PlotFormat, TopolyException, OutputFormat, Colors, Translate
from topoly.polynomial import polynomial as Poly
from itertools import product, combinations
import re
import os
from multiprocessing import Pool
from functools import partial
import random
import gc
from concurrent.futures.process import ProcessPoolExecutor


def find_matching_structure(data, invariant, chiral=False, external_dictionary=''):
    if not data:
        return data
    if invariant == 'Writhe':
        return data
    if type(data) is str or type(data) is Poly:
        return find_matching_knot(data, invariant, chiral=chiral, external_dictionary=external_dictionary)
    elif type(data) is dict and type(list(data.keys())[0]) is str:
        return find_point_matching(data, invariant, chiral=chiral, external_dictionary=external_dictionary)
    elif type(data) is dict and type(list(data.keys())[0]) is tuple:
        for subchain in data.keys():
            data[subchain] = find_point_matching(data[subchain], invariant, chiral=chiral, external_dictionary=external_dictionary)
    else:
        raise TopolyException("Unknown format of the data to identify the matching structure")
    return data


def find_matching_knot(data, invariant, chiral=False, external_dictionary=''):
    data = str(data)
    inverted = -1
    if '{' not in data and '|' not in data and '[' not in data and 'Too' not in data:
        inverted = ' '.join([str(-int(float(_))) for _ in data.strip().split()])
    result = polvalues[invariant].get(data, 'Unknown')
    if result == 'Unknown':
        result = polvalues[invariant].get(inverted, 'Unknown')
    if not chiral:
        result_string = re.sub('\.[1-9]*', '', re.sub('[-+*]', '', result))
        result = '|'.join(sorted(list(set(result_string.split('|')))))
    if result == 'Unknown' and external_dictionary:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("topoly_dictionary", os.path.join(os.getcwd(), external_dictionary))
            topoly_dictionary = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(topoly_dictionary)
            user_dictionary = topoly_dictionary.user_dictionary
            result = user_dictionary[invariant].get(data, 'Unknown')
        except ImportError:
            raise TopolyException("Cannot import the user defined dictionary")
    #if result == 'Unknown': result = 'Unknown (orTooManyCrossings)'
    #print("JESTEM w invariants, zakomentowalam Unknown (orTooMany...)")
    return result


def find_point_matching(data, invariant, chiral=False, external_dictionary=''):
    result = {}
    for key in data.keys():
        translated = find_matching_knot(key, invariant, chiral=chiral, external_dictionary=external_dictionary)
        if translated in result.keys():
            result[translated] = round(result[translated] + data[key], 3)
        else:
            result[translated] = data[key]
    return result


def translate_polvalues(matrix_result, invariant, translate, chiral, external_dictionary):
    translated = find_matching_structure(matrix_result, invariant, chiral=chiral,
                                         external_dictionary=external_dictionary)
    if translate == Translate.BOTH: # return both polvalue and corresponding topology
        return '{}; {}'.format(translated, matrix_result)
    elif translate == Translate.PIU: # return polvalue if unknown, topology in other cases
        if translated == 'Unknown':
            return matrix_result
        else:
            return translated
    return translated
            

def analyze_statistics(statistics, level=0):
    counter = {}
    if len(statistics) == 0:
        counter[0] = 1
    else:
        for polynomial in statistics:
            if polynomial not in counter.keys():
                counter[polynomial] = 0
            counter[polynomial] += 1
        for polynomial in counter.keys():
            counter[polynomial] = float(counter[polynomial])/len(statistics)
    return counter


def generate_identifier(subgraph):
    # TODO generalize on many arcs (theta-curves for example)
    if type(subgraph) is str:
        return subgraph
    else:
        return subgraph[0][0], subgraph[-1][0]


class Invariant(Graph):
    name = 'Invariant'
    known = {}
    communicate = ''
    level = 0
    deterministic_closures = [Closure.CLOSED, Closure.MASS_CENTER, Closure.DIRECTION]

    def calculate(self, invariant, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
                  poly_reduce=True, translate=False, external_dictionary='', chiral=False, boundaries=None,
                  hide_trivial=True, max_cross=15, matrix=True, density=1, level=0, cuda=True, matrix_plot=False,
                  plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG, output_file='', matrix_cutoff=0.48,
                  output_format=OutputFormat.Dictionary, run_parallel=False, parallel_workers=None,
                  palette=Colors.Knots, arrows=True, debug=False):

        if debug:
            print('Calculating the ' + invariant.__name__ + ' with parameters:\n' + str(locals()))
        if closure in self.deterministic_closures:
            tries = 1
        if output_file:
            matrix = True
        if matrix_plot:
            matrix = True
        if matrix and not translate:
            output_format = OutputFormat.Dictionary
        if len(self.arcs) > 1:
            matrix = False
#        if matrix:
#            translate = True

        if translate:
            poly_reduce = True
        if matrix and len(self.arcs) > 1:
            raise TopolyException("The matrix can be calculated only for one arc for now.")
        if not boundaries or matrix:
            boundaries = []
        knot = ''

        matrix_result = self.calculate_matrix(invariant, closure=closure, tries=tries, direction=direction,
                        max_cross=max_cross, reduce_method=reduce_method, poly_reduce=poly_reduce, boundaries=boundaries,
                        matrix=matrix, density=density, level=level, cuda=cuda, run_parallel=run_parallel,
                        parallel_workers=parallel_workers, translate=translate, external_dictionary=external_dictionary,
                        chiral=chiral, hide_trivial=hide_trivial, debug=debug)

        # special case for Writhe when plotting
        if invariant.__name__ == 'WritheGraph' and matrix:
            palette = Colors.Writhe
            arrows = False
            matrix_result, minz = matrix_dominating(matrix_result)
            knot = 'all'
            matrix_cutoff = minz - 1

        # plotting the matrix
        if matrix_plot:
            plot_matrix(matrix_result, plot_ofile=plot_ofile, plot_format=plot_format, cutoff=matrix_cutoff,
                        palette=palette, arrows=arrows, knot=knot, debug=debug)

        # translating the matrix output to desired format
        if matrix:
            if output_format == OutputFormat.KnotProt:
                chain_beg = min(list(self.coordinates.keys()))
                chain_end = max(list(self.coordinates.keys()))
                matrix_result = data2knotprot(matrix_result, chain_beg, chain_end)
            elif output_format == OutputFormat.Matrix:
                matrix_result = data2matrix(matrix_result)
            else:
                matrix_result = data2dictionary(matrix_result)

        # saving output to file if necessary
        if output_file:
            with open(output_file, 'w') as myfile:
                myfile.write(data2string(matrix_result))

        # bye bye
        gc.collect()
        return matrix_result

    def calculate_matrix(self, invariant, closure=Closure.TWO_POINTS, tries=200, direction=0, max_cross=15,
                         reduce_method=ReduceMethod.KMT, poly_reduce=True, boundaries=None, hide_trivial=True,
                         matrix=True, density=1, level=0, cuda=True, run_parallel=False, parallel_workers=None,
                         translate=False, external_dictionary='', chiral=False, debug=False):

        # the case when we operate on abstract codes (closed structure, tries=1, reduction only Reidemeister etc...)
        if self.run_from_code:
            matrix_result = self.analyze_from_code(invariant, max_cross=max_cross, poly_reduce=poly_reduce, debug=debug)
            if translate:
                matrix_result = translate_polvalues(matrix_result, invariant.name, translate=translate, 
                                                    chiral=chiral, external_dictionary=external_dictionary)
            return matrix_result

        # case for links and spatial graphs - no matrix then
        if len(self.arcs) > 1:
            results = []
            for k in range(tries):
                g = invariant(self.init_data)
                g.close(method=closure, direction=direction, debug=debug)
                g.parse_closed()
                results.append(g.calc_point(max_cross=max_cross, poly_reduce=poly_reduce, debug=debug))
            matrix_result = analyze_statistics(results)

            if translate:
                matrix_result = translate_polvalues(matrix_result, invariant.name, translate=translate, 
                                                    chiral=chiral, external_dictionary=external_dictionary)
            if tries == 1:
                matrix_result = list(matrix_result.keys())[0]
            return matrix_result

        # special case for knots and CUDA and Alexander - to be removed when every algorithm is optimized for CUDA
        if matrix and cuda and invariant.__name__ == 'AlexanderGraph' and check_cuda():
            g = invariant([[key] + self.coordinates[key] for key in self.coordinates.keys()])
            matrix_result = g.calc_cuda(closure=closure, tries=tries, direction=direction, reduce=reduce_method,
                       density=density, level=level, debug=debug, translate=translate, max_cross=max_cross)
            g = None
            return matrix_result

        # regular case from coordinates - the structure needs to be closed and reduced
        matrix_result = {}
        subgraphs = self.generate_subchain(matrix=matrix, density=density, boundaries=boundaries)
        matrix_result = self.analyze_points(invariant, subgraphs, matrix_result, closure=closure,
                    reduce_method=reduce_method, direction=direction, max_cross=max_cross, tries=tries,
                    hide_trivial=hide_trivial, poly_reduce=poly_reduce, run_parallel=run_parallel,
                    parallel_workers=parallel_workers, debug=debug)
        additional = self.find_additional(invariant, matrix_result, density, level)
        if additional:
            matrix_result = self.analyze_points(invariant, additional, matrix_result, closure=closure,
                reduce_method=reduce_method, direction=direction, max_cross=max_cross, tries=tries,
                hide_trivial=hide_trivial, poly_reduce=poly_reduce, run_parallel=run_parallel,
                parallel_workers=parallel_workers, debug=debug)

        if translate:
            matrix_result = translate_polvalues(matrix_result, invariant.name, translate=translate, 
                                                chiral=chiral, external_dictionary=external_dictionary)
        if tries == 1:
            if not matrix_result:
                return '0_1'
            for key in matrix_result:
                if len(matrix_result[key].keys()) > 0:
                    matrix_result[key] = list(matrix_result[key].keys())[0]
        if not matrix and not boundaries and len(matrix_result.keys()) > 0:
            matrix_result = list(matrix_result.values())[0]

        return matrix_result

    def generate_subchain(self, matrix=False, density=1, boundaries=[], debug=False):
        chain_beg = min(list(self.coordinates.keys()))
        chain_end = max(list(self.coordinates.keys()))
        subgraphs = []

        if boundaries:
            subgraphs = [(max(chain_beg, x), min(chain_end, y)) for x, y in boundaries]
        elif not matrix:
            return [(chain_beg, chain_end)]
        else:
            for subchain_end in range(chain_end, chain_beg - 1, -density):
                for subchain_beg in range(chain_beg, subchain_end - 4, density):
                    subgraphs.append((subchain_beg, subchain_end))
        return subgraphs

    def find_additional(self, invariant, matrix_results, density=1, level=0, debug=False):
        additional = []
        central_points = []

        # trivial case
        if density == 1:
            return additional

        chain_beg = min(list(self.coordinates.keys()))
        chain_end = max(list(self.coordinates.keys()))

        # searching for subchains, which were identified as non-trivial
        for subchain in matrix_results.keys():
            knots = matrix_results[subchain]
            if type(knots) is not dict:
                continue
            for polval in knots.keys():
                #knot = find_matching_knot(polval,invariant.name)
                if polval == '0_1':
                    continue
                elif knots[polval] > level:
                    central_points.append(subchain)
                    break

        # for each non-trivial point calculate its surrounding
        for point in central_points:
            horizontal_beg = min([k for k in range(point[0] - density, point[0] + 1) if k >= chain_beg])
            horizontal_end = max([k for k in range(point[0], point[0] + density +1) if k <= chain_end])
            vertical_beg = min([k for k in range(point[1] - density, point[1]+ 1) if k >= chain_beg])
            vertical_end = max([k for k in range(point[1], point[1] + density + 1) if k <= chain_end])
            for subchain in product(range(horizontal_beg, horizontal_end + 1), range(vertical_beg, vertical_end + 1)):
                additional.append((min(subchain),max(subchain)))

        return list(set(additional))

    def analyze_from_code(self, invariant, max_cross=15, poly_reduce=True, debug=False):
        g = invariant(self.pdcode)
        result = g.calc_point(max_cross=max_cross, poly_reduce=poly_reduce, debug=debug)
        g = None
        if debug:
            print(result + '\n---')
        return result

    def analyze_points(self, invariant, subgraphs, matrix_result, closure=Closure.TWO_POINTS,
                       reduce_method=ReduceMethod.KMT, direction=0, max_cross=15, tries=200, poly_reduce=True,
                       hide_trivial=True, run_parallel=True, parallel_workers=None, debug=False):

        if run_parallel:
            single_point = partial(self.analyze_single_point, invariant=invariant, closure=closure, reduce_method=reduce_method,
                                   direction=direction, max_cross=max_cross, tries=tries, poly_reduce=poly_reduce,
                                   debug=debug)
            if not parallel_workers:
                parallel_workers = os.cpu_count() or 1
            if debug:
                print("Multiprocessing, using " + str(parallel_workers) + " workers.")
            pool = Pool(processes=parallel_workers)
            
            for ident, result in pool.imap_unordered(single_point, subgraphs, chunksize=4):
                matrix_result[ident] = result
                if debug:
                    print(ident, ": Statistics after " + str(tries) + " tries", matrix_result[ident], '\n===')
            pool.close()
            pool.join()
        else:
            for subgraph in subgraphs:
                ident, result = self.analyze_single_point(subgraph, invariant=invariant, closure=closure,
                                reduce_method=reduce_method, direction=direction, max_cross=max_cross, tries=tries,
                                poly_reduce=poly_reduce, debug=debug)

                matrix_result[ident] = result
                if debug:
                    print(ident, ": Statistics after " + str(tries) + " tries", matrix_result[ident], '\n===')

        # removing trivial
        if hide_trivial:
            to_remove = []
            for ident in matrix_result:
                if matrix_result[ident] in [{'1': 1.0}, {'{ 0 } | 1': 1.0}, {'[[1]]': 1.0}]:
                    to_remove.append(ident)
            for ident in to_remove:
                matrix_result.pop(ident)

        return matrix_result

    def analyze_single_point(self, subgraph, invariant=None, closure=Closure.TWO_POINTS, reduce_method=ReduceMethod.KMT,
                             direction=0, max_cross=15, tries=200, poly_reduce=True, debug=False):

        results = []
        if type(subgraph) is str:
            subchain = subgraph
        else:
            subchain_beg, subchain_end = subgraph
            subchain = super().cut_chain(beg=subchain_beg, end=subchain_end)
        ident = generate_identifier(subchain)

        for k in range(tries):
            if debug:
                print('Subchain: ' + str(ident) + '; Try: ' + str(k + 1))
            g = invariant(subchain)
            if not g.run_from_code:
                g.close(method=closure, direction=direction, debug=debug)
                g.reduce(method=reduce_method, debug=debug)
                g.parse_closed()

            results.append(g.calc_point(max_cross=max_cross, poly_reduce=poly_reduce, debug=debug))

            g = None
            if debug:
                print(results[-1] + '\n---')
        result = analyze_statistics(results)
        return ident, result

    def print_communicate(self):
        com1 = ''
        com2 = ''
        if self.level > 0:
            for _ in range(self.level - 1):
                com1 += '|  '
                com2 += '|  '
            com1 += '|->'
            com2 += '|  '
        com1 += self.communicate + self.pdcode
        print(com1)
        return com2


class AlexanderGraph(Invariant):
    name = 'Alexander'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short().split('|')[-1].strip()
        return str(result)

    def point(self, max_cross=15, debug=False):
        code = self.pdcode
        if len(code.split(';')) > max_cross:
            return Poly(0)

        # Analyzing known
        if code in super().known[__class__.name].keys():
            coefs = super().known[__class__.name][code]
            #print("WANDA, point(), znany pdcode, coefs =", coefs)
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + str(coefs))

        elif not self.coordinates:
            super().known['Conway'] = {}
            g = ConwayGraph(self.pdcode)
            result = g.point(debug=debug)
            result = result({'z': 't**0.5-t**-0.5'})
            return result

        else:
            p_red = calc_alexander_poly(self.coordinates_c[0],max_cross=max_cross)
            #print("WANDA, point(), nieznany pdcode, policzony poly =", str(p_red), end="")
            if debug:
                print("Coefficients obtained: " + str(p_red))
            # TODO is it the right condition?
            if not p_red:
                #p_red = '1' #JESTEM ZMIANA!!!!
                p_red = '0'
            if type(p_red) is int:
                coefs = [p_red]
            else:
                coefs = p_red.split()
            if int(coefs[0]) < 0:
                coefs = [str(-int(_)) for _ in coefs]
            super().known[__class__.name][code] = coefs

        p = Poly('0')
        for k in range(len(coefs)):
            power = k - int((len(coefs)-1)/2)
            p += Poly(coefs[k]) * Poly('x**' + str(power))

        return p

    def calc_cuda(self, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce=ReduceMethod.KMT,
                       density=1, level=0, debug=False, translate=True, max_cross=15):
        matrix = find_alexander_fingerprint_cuda(self.coordinates_c[0], density, level, closure, tries, 1 if translate else 0, max_cross)
        #dict_matrix = {}
        #if ("{" in matrix and ":" in matrix): dict_matrix = eval(matrix)
        #else: dict_matrix = matrix
        #return data2dictionary(dict_matrix)
        return data2dictionary(matrix)


class JonesGraph(Invariant):
    name = 'Jones'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short()
        return str(result)

    def point(self, max_cross=15, debug=False):
        """ The basic method to calculate the Jones polynomial for closed structure. Its input data is the PD code."""

        # simplifying the graph, returns the number of 1st Reidemeister moves performed
        n = self.simplify_reidemeister(debug=False)

        if len(self.crossings) > max_cross:
            return Poly(0)

        # TODO moze te funkcje mozna gdzies wywalic?
        self.generate_orientation()
        self.check_crossings_vs_orientation()

        if debug:
            self.shift = super().print_communicate()
            print(self.shift + "After simplification: " + self.pdcode + '\tn=' + str(n))

        # Check if the structure is in the known cases
        known_case = self.analyze_known(debug=debug)
        if known_case:
            return known_case

        # Treating split sum
        subgraphs = self.find_disjoined_components()
        if len(subgraphs) > 1:
            return self.analyze_split_graphs(subgraphs, n, debug=debug)

        # Reducing crossing by skein relation
        if len(self.crossings) > 0:
            return self.make_skein(n, debug=debug)

        # No crossing, no vertex = empty graph
        super().known[__class__.name][self.pdcode] = Poly('1')
        res = Poly('1')
        if debug:
            print(self.shift + "Empty graph. Result " + str(res))
        return res

    def make_skein(self, n, debug=False):
        """Performing the Jones skein relation on a random crossing k."""
        k = random.randint(0, len(self.crossings) - 1)
        sign = self.find_crossing_sign(k)

        # The coefficients in skein relation. The exact coefficients depend on the sign of the crossing.
        smoothing_coefficient = Poly(str(sign)) * Poly('t**0.5-t**-0.5') * Poly('t**' + str(sign))
        invert_coefficient = Poly('t**' + str(2 * sign))

        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[k]) + " by skein relation. It is " +
                  str(sign) + " crossing.")

        # smoothing the crossing
        smoothed_graph = JonesGraph(self.smooth_crossing(k, sign))
        smoothed_graph.communicate = '(' + str(smoothing_coefficient) + ')*'
        smoothed_graph.level = self.level + 1
        smoothed_result = smoothed_graph.point(debug=debug)

        # inverting the crossing
        inverted_graph = JonesGraph(self.invert_crossing(k))
        inverted_graph.communicate = '(' + str(invert_coefficient) + ')*'
        inverted_graph.level = self.level + 1
        inverted_result = inverted_graph.point(debug=debug)

        super().known[__class__.name][self.pdcode] = smoothing_coefficient * smoothed_result + \
                                                     invert_coefficient * inverted_result
        res = super().known[__class__.name][self.pdcode]

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def analyze_split_graphs(self, subgraphs, n, debug=False):
        """Iteration over the subgraphs."""
        if debug:
            print(self.shift + "It's a split graph: " + '; '.join(subgraphs))

        super().known[__class__.name][self.pdcode] = Poly('1')
        for k in range(len(subgraphs)):
            subgraph = subgraphs[k]
            partial_graph = JonesGraph(subgraph)
            partial_graph.level = self.level + 1
            partial_result = partial_graph.point(debug=debug)
            super().known[__class__.name][self.pdcode] *= partial_result
            if k != len(subgraphs) - 1:
                super().known[__class__.name][self.pdcode] *= Poly('-t**0.5-t**-0.5')
                partial_graph.communicate = ' * (-t**0.5-t**-0.5) '
            else:
                partial_graph.communicate = ' * '
        res = super().known[__class__.name][self.pdcode]

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def analyze_known(self, debug=False):
        """Analyzing known structures."""
        result = ''

        # Checking in the dictionary known:
        if self.pdcode in super().known[__class__.name].keys() and super().known[__class__.name][self.pdcode]:
            res = super().known[__class__.name][self.pdcode]
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + str(res))
            result = res

        # Checking if its a circle
        elif len(self.vertices) == 1 and not self.crossings:
            super().known[__class__.name][self.pdcode] = Poly('1')
            res = super().known[__class__.name][self.pdcode]
            if debug:
                print(self.shift + "It's a circle.")
            result = res

        # Checking if its a split sum of two circles
        if len(self.vertices) == 2 and not self.crossings:
            super().known[__class__.name][self.pdcode] = Poly('-t**0.5-t**-0.5')
            res = super().known[__class__.name][self.pdcode]
            if debug:
                print(self.shift + "It's a split sum of two circles.")
            result = res

        return result


class YamadaGraph(Invariant):
    name = 'Yamada'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short().split('|')[-1].strip()
        return str(result)

    def point(self, max_cross=15, debug=False):
        """ The basic method to calculate the Yamada polynomial for closed structure. Its input data is the PD code."""

        # simplifying the graph, returns the number of 1st Reidemeister moves performed
        n = self.simplify_reidemeister(debug=False)
        if len(self.crossings) > max_cross:
            return Poly(0)
# TODO Poly(0) oznacza w tym przypadku TooManyCrossings - i tak jest wpisane w slowniku we wszystkich wielomianach poza Yamada; w Yamadzie odpowiadaja temu najprostsze kajdanusie...


        # TODO moze te funkcje mozna gdzies wywalic?
        self.generate_orientation()
        self.check_crossings_vs_orientation()

        if debug:
            self.shift = super().print_communicate()
            print(self.shift + "After simplification: " + self.pdcode + '\tn=' + str(n))

        # Check if the structure is in the known cases
        known_case = self.analyze_known(n, debug=debug)
        if isinstance(known_case, Poly):
            return known_case

        # Treating split sum
        subgraphs = self.find_disjoined_components()
        if len(subgraphs) > 1:
            return self.analyze_split_graphs(subgraphs, n, debug=debug)

        # Reducing crossing - there are two ways, first better in terms of efficiency than the second
        if len(self.crossings) > 0:
            for k in range(len(self.crossings)):
                inverted_graph = YamadaGraph(self.invert_crossing(k))
                inverted_graph.simplify_reidemeister()
                if len(inverted_graph.crossings) < len(self.crossings):
                    # the skein-like relation
                    return self.make_skein(k, n, debug=debug)
            else:
                # removing of the first (0) crossing
                return self.remove_crossing(0, n, debug=debug)

        # Edges reduction:
        edges = self.find_noloop_edges()
        if len(edges) > 0:  # than len(self.vertices) >= 2
            return self.reduce_edges(n, edges, debug=debug)

        # No crossing, no vertex = empty graph
        super().known[__class__.name][self.pdcode] = Poly('1')
        res = Poly('1')
        if debug:
            print(self.shift + "Empty graph. Result " + str(res))
        return res

    def analyze_known(self, n, debug=False):
        """Analyzing known structures."""
        result = ''
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        # checking the dictionary of already calculated polynomials
        if self.pdcode in super().known[__class__.name].keys() and super().known[__class__.name][self.pdcode]:
            res = super().known[__class__.name][self.pdcode] * factor
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + '(' + str(res) + ')')
            result = res

        # bouquet of circles - number of circles in bouquet = len(set(graph.vertices[0]))
        elif len(self.vertices) == 1 and not self.crossings:
            n_circles = len(set(self.vertices[0]))
            super().known[__class__.name][self.pdcode] = Poly(-1) * Poly('-x-1-x^-1') ** n_circles
            res = super().known[__class__.name][self.pdcode] * factor
            if debug:
                print(self.shift + "It's a bouquet of " + str(n_circles) + " circles.\n" +
                      self.shift + "Result " + self.communicate + '(' + str(res) + ')')
            result = res

        # trivial theta or trivial handcuff
        elif len(self.vertices) == 2 and not self.crossings and len(self.vertices[1]) == 3:
            if set(self.vertices[0]) == set(self.vertices[1]):  # trivial theta
                super().known[__class__.name][self.pdcode] = Poly('-x^2-x-2-x^-1-x^-2')
                res = super().known[__class__.name][self.pdcode] * factor
                if debug:
                    print(self.shift + "It's a trivial theta.\n" + self.shift + "Result " + self.communicate +
                          '(' + str(res) + ')')
                result = res

            elif len(set(self.vertices[0]) & set(self.vertices[1])) == 1:  # trivial handcuff
                super().known[__class__.name][self.pdcode] = Poly('0')
                res = super().known[__class__.name][self.pdcode]
                if debug:
                    print(self.shift + "It's a trivial handcuff graph.\n" + self.shift + "Result " +
                          '(' + str(res) + ')')
                result = res

        else:    # other simplifying cases
            for v in range(len(self.vertices)):
                vert = self.vertices[v]
                if len(vert) > 3:
                    for k in range(len(vert)):
                        if vert[k] == vert[k - 1]:
                            # bouquet with one loop
                            if debug:
                                print(self.shift + "Removing loop.")
                            removed_loop_graph = YamadaGraph(self.remove_loop(v, k))
                            removed_loop_graph.level = self.level + 1
                            removed_loop_graph.communicate = ' * '
                            removed_loop_result = removed_loop_graph.point(debug=debug)

                            super().known[__class__.name][self.pdcode] = Poly('-1') * Poly('x+1+x^-1') * removed_loop_result
                            res = super().known[__class__.name][self.pdcode] * factor
                            if debug:
                                print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
                            result = res
        return result

    def analyze_split_graphs(self, subgraphs, n, debug=False):
        """Iteration over the subgraphs."""

        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(self.shift + "It's a split graph: " + '; '.join(subgraphs))

        super().known[__class__.name][self.pdcode] = Poly('1')
        for subgraph in subgraphs:
            partial_graph = YamadaGraph(subgraph)
            partial_graph.level = self.level + 1
            partial_graph.communicate = ' * '
            partial_result = partial_graph.point(debug=debug)
            super().known[__class__.name][self.pdcode] *= partial_result

        res = super().known[__class__.name][self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def make_skein(self, k, n, debug=False):
        """Performing the Yamada skein-like relation on a crossing k."""

        # The coefficients in skein relation.
        smooth_positive_coefficient = Poly('x-x^-1')
        smooth_negative_coefficient = -Poly('x-x^-1')
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[k]) + " by skein relation.")

        # "positive" smooth of the crossing
        smoothed_positive = YamadaGraph(self.smooth_crossing(k, 1))
        smoothed_positive.communicate = '(' + str(smooth_positive_coefficient) + ')*'
        smoothed_positive.level = self.level + 1
        smoothed_positive_result = smoothed_positive.point(debug=debug)

        # "negative" smooth of the crossing
        smoothed_negative = YamadaGraph(self.smooth_crossing(k, -1))
        smoothed_negative.communicate = '(' + str(smooth_negative_coefficient) + ')*'
        smoothed_negative.level = self.level + 1
        smoothed_negative_result = smoothed_negative.point(debug=debug)

        # inverting the crossing
        inverted_graph = YamadaGraph(self.invert_crossing(k))
        inverted_graph.communicate = ' + '
        inverted_graph.level = self.level + 1
        inverted_result = inverted_graph.point(debug=debug)

        super().known[__class__.name][self.pdcode] = smooth_positive_coefficient * smoothed_positive_result + \
                                       smooth_negative_coefficient * smoothed_negative_result + \
                                       inverted_result
        res = factor * super().known[__class__.name][self.pdcode]

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def remove_crossing(self, crossing_index, n, debug=False):
        """Removing the crossing crossing_index with introduction of new vertex."""

        # The coefficients in skein relation.
        smooth_positive_coefficient = Poly('x')
        smooth_negative_coefficient = Poly('x^-1')
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[crossing_index]) + " by skein relation.")

        # "positive" smooth of the crossing
        smoothed_positive = YamadaGraph(self.smooth_crossing(crossing_index, 1))
        smoothed_positive.communicate = '(' + str(smooth_positive_coefficient) + ')*'
        smoothed_positive.level = self.level + 1
        smoothed_positive_result = smoothed_positive.point(debug=debug)

        # "negative" smooth of the crossing
        smoothed_negative = YamadaGraph(self.smooth_crossing(crossing_index, -1))
        smoothed_negative.communicate = '(' + str(smooth_negative_coefficient) + ')*'
        smoothed_negative.level = self.level + 1
        smoothed_negative_result = smoothed_negative.point(debug=debug)

        # vertex introduction
        new_vertex = YamadaGraph(self.smooth_crossing(crossing_index, 0))
        new_vertex.communicate = ' + '
        new_vertex.level = self.level + 1
        new_vertex_result = new_vertex.point(debug=debug)

        super().known[__class__.name][self.pdcode] = smooth_positive_coefficient * smoothed_positive_result + \
                                     smooth_negative_coefficient * smoothed_negative_result + \
                                     new_vertex_result
        res = super().known[__class__.name][self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def reduce_edges(self, n, edges, debug=False):
        """Reducing the first no-loop edge."""
        factor = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))     # factor coming from the Reidemeister I and V moves

        if debug:
            print(self.shift + "Reducing noloop edge " + str(edges[0]) + ".")

        # graph with removed no-loop edge
        removed_edge = YamadaGraph(self.remove_noloop_edge(edges[0]))
        removed_edge.level = self.level + 1
        removed_edge_result = removed_edge.point(debug=debug)

        # graph with contracted edge
        contracted_edge = YamadaGraph(self.contract_edge(edges[0]))
        contracted_edge.level = self.level + 1
        contracted_edge.communicate = ' + '
        contracted_edge_result = contracted_edge.point(debug=debug)

        super().known[__class__.name][self.pdcode] = removed_edge_result + contracted_edge_result
        res = super().known[__class__.name][self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res


class HomflyGraph(Invariant):
    name = 'HOMFLY-PT'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if not poly_reduce:
            result = self.make_poly_explicit(result)
        return str(result)

    def truncate_bytes(s, maxlen=128, suffix=b'...'):
        # type: (bytes, int, bytes) -> bytes
        if maxlen and len(s) >= maxlen:
            return s[:maxlen].rsplit(b' ', 1)[0] + suffix
        return s

    def point(self, max_cross=15, debug=False):
        if any([len(vert) > 2 for vert in self.vertices]):
            raise TopolyException("The HOMFLY-PT polynomial cannot be used on spatial graphs.")
        # Analyzing known structures
        if self.emcode in super().known[__class__.name].keys():
            result = super().known[__class__.name][self.emcode]
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + str(result))
        else:
            code = self.emcode
            if len(self.vertices) > 0:
                code = self.remove_double_vertices()
            code = code.replace(';', '\n')
            if len(code.split('\n')) > max_cross:
                return '0'
            if not code:
                result = '[[1]]'
            else:
                result = lmpoly(code).replace('\n', '|')
            result = self.add_missing_components(result, code)
            super().known[__class__.name][code] = result
        return result

    def add_missing_components(self, result, code):
        found_components, needed_components = self.number_of_components(code)
        diff = needed_components - found_components
        if diff == 0:
            return result
        else:
            poly = self.make_poly_explicit(result)
            for k in range(diff):
                poly *= Poly('-1') * Poly('l + l**-1') * Poly('m**-1')
            return poly.print_short()

    def make_poly_explicit(self, poly):
        # the method is not strictly static, as it depends on the implicit variables (l,m) of the HOMFLY-PT polynomial
        result = Poly(0)
        rows = poly.split('|')
        m0 = len(rows)
        for m in range(len(rows)):
            row = rows[m]
            if row[0] == '[' and row[-1] == ']' and (len(row.split()) > 1 or row[1] == '['):
                m0 = m
                row = row[1:-1]
            terms = row.split()
            row_poly = Poly(0)
            l0 = len(terms)
            for l in range(len(terms)):
                term = terms[l]
                if '[' in term:
                    l0 = l
                    term = term[1:-1]
                row_poly += Poly(term) * Poly('l**' + str(l))
            result += row_poly * Poly('l**-' + str(l0) + 'm**' + str(m))
        result = result * Poly('m**-' + str(m0))
        return result

    def remove_double_vertices(self):
        newcode = []
        trans = {}
        letters = {-1: 'dcba', 1: 'badc'}
        signs = {-1: '-', 1: '+'}
        for element in self.pdcode.split(';'):
            if element[0] == 'V':
                edges = element.strip('V[]').split(',')
                trans[int(edges[0])] = int(edges[1])
                trans[int(edges[1])] = int(edges[0])
        for k in range(len(self.crossings)):
            crossing = self.crossings[k]
            sign = self.find_crossing_sign(k)
            crossing_trans = []
            for e in range(len(crossing)):
                edge = trans.get(crossing[e], crossing[e])
                for l in range(len(self.crossings)):
                    if l == k:
                        if edge in crossing[:e]:
                            newind = crossing[:e].index(edge)
                        elif edge in crossing[e + 1:]:
                            newind = crossing[e + 1:].index(edge) + e + 1
                        else:
                            continue
                        crossing_trans.append(
                            str(l + 1) + letters[self.find_crossing_sign(l)][newind])
                        break
                    if edge in self.crossings[l]:
                        crossing_trans.append(str(l + 1) + letters[self.find_crossing_sign(l)][
                            self.crossings[l].index(edge)])
                        break
            if sign > 0:
                crossing_trans = crossing_trans[2:] + crossing_trans[:2]
            crossing_trans = list(reversed(crossing_trans))
            newcode.append(str(k + 1) + signs[sign] + ''.join(crossing_trans))
        newcode = ';'.join(newcode)
        return newcode

    def number_of_components(self, code=None):
        needed = len(self.find_disjoined_components())
        found = max(len(re.findall('V', code)), 1)
        return found, needed


class ConwayGraph(Invariant):
    name = 'Conway'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short().split('|')[-1].strip()
        return str(result)

    def point(self, max_cross=15, debug=False):
        """ The basic method to calculate the Conway polynomial for closed structure, using the skein relation.
        The methods input is the PD code."""
        # simplifying the graph, returns the number of 1st Reidemeister moves performed
        n = self.simplify_reidemeister(debug=False)
        if len(self.crossings) > max_cross:
            return Poly(0)

        if debug:
            self.shift = super().print_communicate()
            print(self.shift + "After simplification: " + self.pdcode + '\tn=' + str(n))

        # Check if the structure is in the known cases
        known_case = self.analyze_known(debug=debug)
        if known_case:
            return known_case

        # Treating split sum
        subgraphs = self.find_disjoined_components()
        if len(subgraphs) > 1:
            return Poly(0)

        # Reducing crossing by skein relation
        if len(self.crossings) > 0:
            return self.make_skein(n, debug=debug)

        # No crossing, no vertex = empty graph
        super().known[__class__.name][self.pdcanonical] = Poly('1')
        res = Poly('1')
        if debug:
            print(self.shift + "Empty graph. Result " + str(res))
        return res

    def analyze_known(self, debug=False):
        """Analyzing known structures."""
        result = ''

        # Checking in the dictionary known:
        if self.pdcanonical in super().known[__class__.name].keys() and super().known[__class__.name][self.pdcanonical]:
            res = super().known[__class__.name][self.pdcanonical]
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + str(res))
            result = res

        # Checking if its a circle
        elif len(self.vertices) == 1 and not self.crossings:
            super().known[__class__.name][self.pdcanonical] = Poly('1')
            res = super().known[__class__.name][self.pdcanonical]
            if debug:
                print(self.shift + "It's a circle.")
            result = res

        # Checking if its a split sum of two circles
        if len(self.vertices) == 2 and not self.crossings:
            super().known[__class__.name][self.pdcanonical] = Poly(0)
            res = super().known[__class__.name][self.pdcanonical]
            if debug:
                print(self.shift + "It's a split sum of two circles.")
            result = res

        return result

    def make_skein(self, n, debug=False):
        """Performing the Conway skein relation on a random crossing k."""
        k = random.randint(0, len(self.crossings) - 1)
        sign = self.find_crossing_sign(k)

        # The coefficients in skein relation. The exact coefficients depend on the sign of the crossing.
        smoothing_coefficient = Poly(str(sign)) * Poly('z')
        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[k]) + " by skein relation. It is " +
                  str(sign) + " crossing. Arc orientations: " + str(self.orientation))

        # smoothing the crossing
        smoothed_code = self.smooth_crossing(k, sign)
        if debug:
            print(self.shift + "Smoothed crossing: " + smoothed_code)
        smoothed_graph = ConwayGraph(smoothed_code)
        smoothed_graph.communicate = '(' + str(smoothing_coefficient) + ')*'
        smoothed_graph.level = self.level + 1
        smoothed_result = smoothed_graph.point(debug=debug)

        # inverting the crossing
        inverted_code = self.invert_crossing(k)
        if debug:
            print(self.shift + "Inverted crossing: " + inverted_code)
        inverted_graph = ConwayGraph(inverted_code)
        inverted_graph.communicate = ' + '
        inverted_graph.level = self.level + 1
        inverted_result = inverted_graph.point(debug=debug)

        super().known[__class__.name][self.pdcanonical] = smoothing_coefficient * smoothed_result + inverted_result
        res = super().known[__class__.name][self.pdcanonical]

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res


class KauffmanBracketGraph(Invariant):
    name = 'Kauffman bracket'

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short().split('|')[-1].strip()
        return str(result)

    def point(self, max_cross=15, b='A**-1', d='-A**2-A**-2', debug=False):
        """ The basic method to calculate the Kauffman bracket for closed structure. Its input data is the PD code.
        The user may substitute different value of the parameters b and d in the Kauffman Bracket definition
        instead of the regular ones."""

        res = Poly('0')
        n = len(self.crossings)
        if n > max_cross:
            return Poly(0)

        # calculating the polynomial value as the iteration of smoothings.
        for state in product([-1, 1], repeat=n):
            g = KauffmanBracketGraph(self.pdcode)
            for smooth in state:
                g = KauffmanBracketGraph(g.smooth_crossing(0, smooth))
            smooth_a = Poly('A**' + str(int((n + sum(state))/2)))
            smooth_b = Poly('B**' + str(int((n - sum(state))/2)))
            separate_parts = Poly('d**' + str(len(g.vertices)-1))
            term_res = smooth_a * smooth_b * separate_parts
            if debug:
                print("State: " + str(state) + ". Result: " + str(term_res))
            res += term_res
        res = res({'B': b, 'd': d})
        return res


class WritheGraph(Invariant):
    name = 'Writhe'

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        return str(self.point(debug=debug))

    def point(self, debug=False):
        res = sum([self.find_crossing_sign(k) for k in range(len(self.crossings))])
        return res


class KauffmanPolynomialGraph(Invariant):
    name = 'Kauffman polynomial'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short(two_vars=True)
        return str(result)

    def point(self, max_cross=15, debug=False):
        self.simplify_reidemeister(debug=debug)
        if len(self.crossings) > max_cross:
            return Poly(0)

        writhe = WritheGraph(self.pdcode).point()
        res = Poly('a**' + str(-writhe))
        g = Kauffman2VariableGraph(self.pdcode)
        res *= g.point(max_cross=max_cross, debug=debug)
        return res


class Kauffman2VariableGraph(WritheGraph):
    name = 'Kauffman two variable polynomial'
    level = 0
    communicate = ''
    shift = ''

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short()
        return str(result)

    def point(self, max_cross=15, debug=False):
        """ The basic method to calculate the Kauffman two-variable polynomial for closed structure.
        Its input data is the PD code."""

        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}

        # simplifying the graph, returns the number of 1st Reidemeister moves performed
        n = int(self.simplify_reidemeister(debug=False)/2)
        if len(self.crossings) > max_cross:
            return Poly(0)

        # TODO moze te funkcje mozna gdzies wywalic?
        self.generate_orientation()
        self.check_crossings_vs_orientation()

        if debug:
            self.shift = super().print_communicate()
            print(self.shift + "After simplification: " + self.pdcode + '\tn=' + str(n))

        # Check if the structure is in the known cases
        known_case = self.analyze_known(n, debug=debug)
        if known_case:
            return known_case

        # Treating split sum
        subgraphs = self.find_disjoined_components()
        if len(subgraphs) > 1:
            return self.analyze_split_graphs(subgraphs, n, debug=debug)

        # Reducing crossing by skein relation
        if len(self.crossings) > 0:
            return self.make_skein(n, debug=debug)

        # No crossing, no vertex = empty graph
        super().known[__class__.name][self.pdcode] = Poly('1')
        res = Poly('1')
        if debug:
            print(self.shift + "Empty graph. Result " + str(res))
        return res

    def analyze_known(self, n, debug=False):
        """Analyzing known structures."""
        result = ''
        factor = Poly('a^' + str(n))    # factor coming from the Reidemeister I move

        # Checking in the dictionary known:
        if self.pdcode in super().known[__class__.name].keys() and super().known[__class__.name][self.pdcode]:
            res = super().known[__class__.name][self.pdcode] * factor
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + str(res))
            result = res

        # Checking if its a circle
        elif len(self.vertices) == 1 and not self.crossings:
            super().known[__class__.name][self.pdcode] = Poly('1')
            res = super().known[__class__.name][self.pdcode] * factor
            if debug:
                print(self.shift + "It's a circle.")
            result = res

        # Checking if its a split sum of two circles
        if len(self.vertices) == 2 and not self.crossings:
            super().known[__class__.name][self.pdcode] = Poly('a+a**-1-z') * Poly('z**-1')
            res = super().known[__class__.name][self.pdcode] * factor
            if debug:
                print(self.shift + "It's a split sum of two circles.")
            result = res

        return result

    def analyze_split_graphs(self, subgraphs, n, debug=False):
        """Iteration over the subgraphs."""
        if debug:
            print(self.shift + "It's a split graph: " + '; '.join(subgraphs))

        factor = Poly('a^' + str(n))    # factor coming from the Reidemeister I move

        super().known[__class__.name][self.pdcode] = Poly('1')
        for k in range(len(subgraphs)):
            subgraph = subgraphs[k]
            partial_graph = Kauffman2VariableGraph(subgraph)
            partial_graph.level = self.level + 1
            partial_graph.communicate = ' * '
            partial_result = partial_graph.point(debug=debug)
            super().known[__class__.name][self.pdcode] *= partial_result
            if k != len(subgraphs) - 1:
                super().known[__class__.name][self.pdcode] *= Poly('a+a**-1-z')*Poly('z**-1')
                partial_graph.communicate = ' * (a+a**-1-z)*(z**-1) '
            else:
                partial_graph.communicate = ' * '
        res = super().known[__class__.name][self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res

    def make_skein(self, n, debug=False):
        """Performing the two variable Kauffman Polynomial skein relation on a random crossing k."""
        k = random.randint(0, len(self.crossings) - 1)
        sign = self.find_crossing_sign(k)
        factor = Poly('a^' + str(n))    # factor coming from the Reidemeister I move

        # The coefficients in skein relation. The exact coefficients depend on the sign of the crossing.
        positive_smooth_coefficient = Poly('z')
        negative_smooth_coefficient = Poly('z')

        if debug:
            print(self.shift + "Reducing crossing " + str(self.crossings[k]) + " by skein relation. It is " +
                  str(sign) + " crossing.")

        # positive smoothing
        positive_smooth = Kauffman2VariableGraph(self.smooth_crossing(k, 1))
        positive_smooth.communicate = '(' + str(positive_smooth_coefficient) + ')*'
        positive_smooth.level = self.level + 1
        positive_smooth_result = positive_smooth.point(debug=debug)

        # negative smoothing
        negative_smooth = Kauffman2VariableGraph(self.smooth_crossing(k, -1))
        negative_smooth.communicate = '(' + str(negative_smooth_coefficient) + ')*'
        negative_smooth.level = self.level + 1
        negative_smooth_result = negative_smooth.point(debug=debug)

        # inverting the crossing
        inverted_graph = Kauffman2VariableGraph(self.invert_crossing(k))
        inverted_graph.communicate = ' - '
        inverted_graph.level = self.level + 1
        inverted_result = inverted_graph.point(debug=debug)

        super().known[__class__.name][self.pdcode] = positive_smooth_coefficient * positive_smooth_result + \
                                     negative_smooth_coefficient * negative_smooth_result - \
                                     inverted_result

        res = super().known[__class__.name][self.pdcode] * factor

        if debug:
            print(self.shift + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
        return res


class BlmhoGraph(Invariant):
    name = 'BLM/Ho'

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short()
        return str(result)

    def point(self, max_cross=15, debug=False):
        g = Kauffman2VariableGraph(self.pdcode)
        res = g.point(max_cross=max_cross, debug=debug)
        res = res({'a': 1, 'z': 'x'})
        if debug:
            print('After substitution: ' + str(res))
        return res


class ApsGraph(Invariant):
    name = 'APS'

    def calc_point(self, max_cross=15, poly_reduce=True, debug=False):
        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}
        result = self.point(max_cross=max_cross, debug=debug)
        if poly_reduce:
            result = result.print_short()
        return str(result)

    def point(self, max_cross=15, debug=False):
        """ The basic method to calculate the APS bracket for the closed structure.
        Its input data is the PD code."""


        if __class__.name not in super().known.keys():
            super().known[__class__.name] = {}

        # simplifying the graph, returns the number of 1st Reidemeister moves performed
        # n = int(self.simplify_reidemeister(debug=False)/2)
        if len(self.crossings) > max_cross:
            return Poly(0)

        # TODO moze te funkcje mozna gdzies wywalic?
        self.generate_orientation()
        self.check_crossings_vs_orientation()

        if debug:
            self.shift = super().print_communicate()
            # print(self.shift + "After simplification: " + self.pdcode + '\tn=' + str(n))

        # Check if the structure is in the known cases
        known_case = self.analyze_known(debug=debug)
        if known_case:
            return known_case

        # Removing the colored edges
        vertices_pairs = self.find_pairs()
        if vertices_pairs:
            res = self.remove_vertex_pair(vertices_pairs[0], debug=debug)

        # Calculating the Kauffman bracket
        else:
            kauffman_part = KauffmanBracketGraph(self.pdcode)
            res = kauffman_part.point(debug=debug)

        return res

    def analyze_known(self, debug=False):
        # Checking in the dictionary known:
        result = ''
        if self.pdcode in super().known[__class__.name].keys() and super().known[__class__.name][self.pdcode]:
            res = super().known[__class__.name][self.pdcode]
            if debug:
                print(self.shift + 'Known case.\n' + self.shift + "Result " + self.communicate + str(res))
            result = res
        return result

    def find_pairs(self):
        pairs = []
        for edge in self.edge_colors.keys():
            if self.edge_colors[edge] != edge:
                for v1, v2 in combinations(self.vertices, 2):
                    if edge in v1 and edge in v2:
                        pairs.append([v1, v2, edge])
        return pairs

    def remove_vertex_pair(self, pair, debug=False):
        c_coefficient = Poly('S') - Poly('-A**2-A**-2')*Poly('P')
        d_coefficient = Poly('P') - Poly('-A**2-A**-2')*Poly('S')

        c_graph = ApsGraph(self.smooth_edge(pair, 1))
        c_graph.communicate = ' C* '
        c_graph.level = self.level + 1
        c_result = c_graph.point(debug=debug)

        d_graph = ApsGraph(self.smooth_edge(pair, -1))
        d_graph.communicate = ' D* '
        d_graph.level = self.level + 1
        d_result = d_graph.point(debug=debug)
        print("d_result: ", d_result)
        print("c_result: ", c_result)

        super().known[__class__.name][self.pdcanonical] = c_coefficient * c_result + d_coefficient * d_result
        res = super().known[__class__.name][self.pdcanonical]
        return res

    def smooth_edge(self, pair, sign):
        code = ''
        vertices = [vert for vert in self.vertices if vert not in pair]
        if sign == 1:
            v1 = [pair[0][pair[0].index(pair[2]) - 2], pair[0][pair[0].index(pair[2]) - 1]]
            v2 = [pair[1][pair[1].index(pair[2]) - 1], pair[1][pair[1].index(pair[2]) - 2]]
        else:
            v1 = [pair[0][pair[0].index(pair[2]) - 2], pair[1][pair[1].index(pair[2]) - 1]]
            v2 = [pair[0][pair[0].index(pair[2]) - 1], pair[1][pair[1].index(pair[2]) - 2]]
        vertices += [v1, v2]
        for vert in vertices:
            code += 'V[' + ','.join([str(x) for x in vert]) + '];'
        for cross in self.crossings:
            code += 'X[' + ','.join([str(x) for x in cross]) + '];'
        g = Graph(code[:-1])
        g.remove_double_verts()
        return g.pdcode


class GlnGraph(Graph):
    name = 'GLN'

    def calculate(self, chain2=None, boundary=(-1, -1), boundary2=(-1, -1), matrix=False, avgGLN=False, maxGLN=False, 
        max_density=-1, avg_tries=200, matrix_plot=False, matrix_plot_format=PlotFormat.PNG,
        plot_ofile="GLN_map", output_file='', output_format=OutputFormat.Matrix, precision=3,
        chain2_id=None, model2=None, bridges_chain2=[], breaks_chain2=[], debug=False):

        if not validate_input(chain2, boundary, boundary2):
            raise TopolyException("Too few data. You have to specify either two chains (with chain2 parameter), or "
                                  "mutually exclusive boundaries (with boundary and boundary2 parameters)")
        arc1 = [[key] + self.coordinates[key] for key in self.coordinates.keys()]
        if chain2:
            g = Graph(chain2, chain=chain2_id, model=model2, bridges=bridges_chain2, breaks=breaks_chain2)
            arc2 = [[key] + g.coordinates[key] for key in g.coordinates.keys()]
        else:
            arc2 = [[key] + self.coordinates[key] for key in self.coordinates.keys()]

        if matrix_plot or output_file:
            matrix = True

        if not (matrix or avgGLN or maxGLN): #basic mode
            if debug:
                print("Calculating the simple GLN value.")
            return round(c_gln(arc1, arc2, boundary[0], boundary[1], boundary2[0], boundary2[1]), precision)

        result = {'whole': [], 'wholeCH1_fragmentCH2': [], 'wholeCH2_fragmentCH1': [], 'fragments': [], 'avg': None, 'matrix': None}

        if maxGLN:
            if debug:
                print("Calculating the maximal GLN value.")
            value = list(reversed(c_gln_max(arc1, arc2, boundary[0], boundary[1], boundary2[0], boundary2[1], max_density,
                                            precision).decode('utf-8').split()))
            current = ''
            while value:
                element = value.pop()
                if element == 'wh:':
                    current = 'whole'
                elif element == 'max_wh_comp1:':
                    current = 'wholeCH1_fragmentCH2'
                elif element == 'max_wh_comp2:':
                    current = 'wholeCH2_fragmentCH1'
                elif 'maxTotalDense' in element:
                    current = 'fragments'
                elif 'shorter' in element:
                    current = ''
                else:
                    if current:
                        gln_value = element.replace(',','-').strip('()')
                        if gln_value[-1] == '-': gln_value = gln_value[:-1]
                        if not result[current]:
                            result[current].append(float(gln_value))
                        else:
                            result[current].append(gln_value)

        if avgGLN:
            if debug:
                print("Calculating the average GLN value on " + str(avg_tries) + " tries.")
            result['avg'] = round(c_gln_average(arc1, arc2, boundary[0], boundary[1], boundary2[0], boundary2[1], avg_tries),
                         precision)
            if not result['whole']:
                result['whole'] = round(c_gln(arc1, arc2, boundary[0], boundary[1], boundary2[0], boundary2[1]), precision)

        if matrix:
            if debug:
                print("Calculating the GLN matrix.")
            matrix = c_gln_matrix(arc1, arc2, boundary[0], boundary[1], boundary2[0], boundary2[1])

            for i, j in product(range(len(matrix)), range(len(matrix))):
                matrix[i][j] = round(matrix[i][j], precision)

            if matrix_plot:
                if debug:
                    print("Plotting the matrix.")
                plot_matrix(matrix, plot_ofile=plot_ofile, plot_format=matrix_plot_format, palette=Colors.GLN, arrows=False,
                            cutoff=-10, gridsize_cutoff=20, debug=debug)
            if output_format == OutputFormat.Dictionary:
                matrix = data2dictionary(matrix)
            elif output_format == OutputFormat.KnotProt:
                matrix = data2knotprot(matrix, 0, len(matrix))
            if output_file:
                with open(output_file, 'w') as myfile:
                    myfile.write(str(matrix))
            result['matrix'] = matrix
            if not result['whole']:
                result['whole'] = round(c_gln(arc1, arc2, boundary[0], boundary[1], boundary2[0], boundary2[1]), precision)

        return result


def validate_input(chain2, boundary, boundary2):
    if chain2:
        return True
    if boundary[0] < boundary[1] < boundary2[0] < boundary2[1]:
        return True
    if boundary2[0] < boundary2[1] < boundary[0] < boundary[1]:
        return True
    return False

