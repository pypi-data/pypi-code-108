""" Testing the polynomials on codes, idealized, and real spatial curves.

Test by Pawel Dabrowski-Tumanski
Version from 24.03.2020
"""

from topoly import yamada, aps, import_structure, find_loops, find_handcuffs, find_thetas, find_links, jones
from topoly.params import Closure, OutputType, Bridges
from topoly.graph import Graph
import pytest
from time import time
import logging
log = logging.getLogger()

prefix = {'ideal': 'data/spatial_graphs/', 'real': 'data/spatial_real/'}
algorithms = {'Yamada': yamada, 'APS': aps}
codes = {'Yamada': ['-t3_1', '+t3_1', 't4_1.1', 't4_1.2', 't5_1.1', 't5_1.2', '-t5_2', '+t5_2', '-t5_3', '+t5_3',
                    '-t5_4', '+t5_4', '-t5_5', '+t5_5', '-t5_6', '+t5_6', '-t5_7', '+t5_7', 't0_1#-3_1', 't0_1#+3_1',
                    '+t3_1#3+t3_1', '-t3_1#3+t3_1', '-t3_1#3+t3_1', 'h2_1.1', 'h4_1++*', 'h5_1++*', 'h6_1',
                    'h6_2.1', 'h2_1#3h2_1', 'h2_1#3t3_1', ], #h2_1.2, h4_1+-, h2_1#3h4_1
         'APS': []}
ideal = {'Yamada': {
                    ('+t3_1', ('+3_1', '0_1', '0_1')): 'pt31.xyz',
                    ('-t3_1', ('-3_1', '0_1', '0_1')): 'mt31.xyz',
                    ('t4_1.1', ('4_1', '0_1', '0_1')): 't41_1.xyz',
                    ('t4_1.2', ('4_1', '0_1', '0_1')): 't41_2.xyz',
                    ('t5_1.1', ('0_1', '0_1', '0_1')): 't51_1.xyz',
                    ('t5_1.2', ('0_1', '0_1', '0_1')): 't51_2.xyz',
                    ('-t5_2', ('-3_1', '0_1', '0_1')): 'mt52.xyz',
                    ('+t5_2', ('+3_1', '0_1', '0_1')): 'pt52.xyz',
                    ('+t5_3', ('+5_1', '0_1', '0_1')): 'pt53.xyz',
                    ('-t5_3', ('-5_1', '0_1', '0_1')): 'mt53.xyz',
                    ('-t5_4', ('-5_1', '-3_1', '0_1')): 'mt54.xyz',
                    ('+t5_4', ('+5_1', '+3_1', '0_1')): 'pt54.xyz',
                    # ('-t5_5', ('-5_2', '0_1', '0_1')): 'mt55.xyz',
                    # ('+t5_5', ('+5_2', '0_1', '0_1')): 'pt55.xyz',
                    # ('-t5_6', ('-5_2', '0_1', '0_1')): 'mt56.xyz',
                    # ('+t5_6', ('+5_2', '+0_1', '0_1')): 'pt56.xyz',
                    # ('-t5_7', ('-5_2', '-3_1', '0_1')): 'mt57.xyz',
                    # ('+t5_7', ('+5_2', '+3_1', '0_1')): 'pt57.xyz',
                    # ('t0_1#-3_1', ('-3_1', '-3_1', '0_1')): 't01Hm31.xyz',
                    # ('t0_1#+3_1', ('+3_1', '+3_1', '0_1')): 't01Hp31.xyz',
                    ('h2_1.2', ('2^2_1', '0_1', '0_1')): 'h21.xyz',
                    ('h4_1++*', ('4^2_1', '0_1', '0_1')): 'h41.xyz',
                    ('h6_1', ('0_1', '0_1', '0_1U0_1')): 'h61.xyz',
                    ('h2_1#3h2_1', ('0_1U0_1', '0_1', '0_1')): 'h21H3h21.xyz'
                    },
         'APS': {}}
random = {'Yamada': {'h2_1': 'h21.xyz', 'h4_1': 'h41.xyz', 'h5_1': 'h51.xyz', 'h6_2': 'h62.xyz',
                     'h2_1#3h2_1': 'h21H3h21.xyz', 'h2_1#3t3_1': 'h21H3t31.xyz'}, #'+t3_1': 'pt31.xyz',
                     # '-t3_1': 'mt31.xyz', '4_1.1': 't41_1.xyz', '4_1.2': 't41_2.xyz', 't0_1#-3_1': 't01Hm31.xyz',
                     # 't0_1#+3_1': 't01H31.xyz'},    # 'h6_1': 'h61.xyz',
         'APS': {}}
protein = {'Yamada': {('2lfk', 'A', ()): 'h2_1', ('3suk', 'A', ()): 'h2_1',
                      ('1aoc', 'A', ()): 't3_1', ('6f33', 'A', ()): 'h2_1#3h2_1'},
            'APS': {}}

loops = {('theta_handcuff.pdb', 1, Bridges.SSBOND): [{'code': 'V[0,2];X[1,0,2,1]', 'topology': '0_1', 'atoms': 22},
                                                     {'code': 'V[0,2];X[1,0,2,1]', 'topology': '0_1', 'atoms': 21},
                                                     {'code': 'V[0,2];X[1,0,2,1]', 'topology': '0_1', 'atoms': 21},
                                                     {'code': 'V[0,2];X[1,0,2,1]', 'topology': '0_1', 'atoms': 11}]}

thetas = {'theta_handcuff.pdb': {}}
handcuffs = {'theta_handcuff.pdb': {}}
links = {'theta_handcuff.pdb': {}}


# preparing data for Yamada polynomial testing
def prepare_codes():
    polynomials = {}
    for algorithm in algorithms.keys():
        polynomials[algorithm] = {}
        for code in codes[algorithm]:
            log.info("Calculating " + str(algorithm) + ' ' + str(code))
            data = import_structure(code)
            polynomials[algorithm][code] = algorithms[algorithm](data, chiral=True)
    log.info('Results:')
    for algorithm in algorithms.keys():
        k = 0
        while k < len(codes[algorithm]):
            comm = '\t'.join(['{:20}'.format('Algorithm')] + ['{:>5}'.format(code)
                                                              for code in codes[algorithm][k:k+10]])
            log.info(comm)
            log.info('\t'.join(['{:20}'.format(algorithm)] + ['{:>5}'.format(polynomials[algorithm][code])
                                                           for code in codes[algorithm][k:k+10]]))
            separator = ''.join(['_' for k in range(len(comm.expandtabs()))])
            log.info(separator)
            k += 10
    log.info('========')
    return polynomials


def prepare_ideal():
    polynomials = {}
    for algorithm in algorithms.keys():
        for curve, knots in ideal[algorithm].keys():
            polynomials[curve] = {}
            log.info("Calculating " + str(algorithm) + ' ' + str(curve))
            structure = prefix['ideal'] + ideal[algorithm][(curve, knots)]
            polynomials[curve]['whole'] = algorithms[algorithm](structure, closure=Closure.CLOSED, chiral=True)
            polynomials[curve]['detail'] = []
            for loop in find_loops(structure, arc_bridges=0, output='generator'):
                res = jones(loop, chiral=True, closure=Closure.CLOSED)
                if type(res) is dict and not res:
                    res = '0_1'
                polynomials[curve]['detail'].append(res)
            for link in find_links(structure, arc_bridges=0, output='generator'):
                polynomials[curve]['detail'].append(jones(link, closure=Closure.CLOSED))
            polynomials[curve]['detail'] = tuple(polynomials[curve]['detail'])
    log.info('Results:')
    for algorithm in algorithms.keys():
        for curve, knot in ideal[algorithm].keys():
            log.info(algorithm + ' ' + str(curve) + ' calculated: ' + str(polynomials[curve]['whole']) + ' links: ' + str(polynomials[curve]['detail']))
    log.info('========')
    return polynomials


def prepare_random():
    polynomials = {}
    times = {}
    for algorithm in algorithms.keys():
        polynomials[algorithm] = {}
        times[algorithm] = {}
        for f in random[algorithm].keys():
            log.info("Calculating " + str(algorithm) + ' ' + str(f))
            t0 = time()
            polynomials[algorithm][f] = algorithms[algorithm](prefix['real'] + random[algorithm][f],
                                                              closure=Closure.CLOSED, max_cross=25)
            times[algorithm][f] = time() - t0
    log.info('Results:')
    for algorithm in algorithms.keys():
        log.info('\t'.join(['{:20}'.format('Algorithm')] + ['{:>18}'.format(f)
                                                         for f in list(random[algorithm].keys())]))
        line = ['{:20}'.format(algorithm)] + \
               ['{:18}'.format(str(polynomials[algorithm][f]) + ' (' + str(round(times[algorithm][f], 3)) + 's)')
                for f in random[algorithm].keys()]
        log.info('\t'.join(line))
    log.info('========')
    return polynomials


def prepare_protein():
    polynomials = {}
    times = {}
    for algorithm in algorithms.keys():
        polynomials[algorithm] = {}
        times[algorithm] = {}
        for pdb, chain, bridges in protein.keys():
            log.info("Calculating " + str(algorithm) + ' ' + str(pdb) + ' ' + str(bridges))
            t0 = time()
            polynomials[algorithm][pdb] = algorithms[algorithm](prefix['real'] + pdb + '.pdb', tries=50,
                                                                      max_cross=25)
            times[algorithm][pdb] = time() - t0
    log.info('Results:')
    for algorithm in algorithms.keys():
        for pdb, chain, bridges in list(protein.keys()):
            log.info('\t'.join(['{:20}'.format(algorithm), pdb, chain] +
                            [str(polynomials[algorithm][pdb]) + ' (' + str(round(times[algorithm][pdb], 3)) + 's)']))
    log.info('========')
    return polynomials


''' actual test'''
# @pytest.mark.skip
def test_codes():
    log.info("Testing the polynomials on abstract codes")
    polynomials = prepare_codes()
    for algorithm in algorithms.keys():
        for code in codes[algorithm]:
            assert code in polynomials[algorithm][code].split('|')
    return


# @pytest.mark.skip
def test_ideal():
    log.info("Testing the polynomials on idealized structures")
    polynomials = prepare_ideal()
    for algorithm in algorithms.keys():
        for curve, knots in ideal[algorithm].keys():
            assert polynomials[curve]['whole'] == curve
            assert set(polynomials[curve]['detail']) == set(knots)
    return


# @pytest.mark.skip
def test_random():
    log.info("Testing the polynomials on random structures")
    polynomials = prepare_random()
    for algorithm in algorithms.keys():
        for f in random[algorithm].keys():
            expected = random[algorithm][f]
            if type(polynomials[algorithm][f]) is dict:
                result = polynomials[algorithm][f].get(expected, 0)
                assert result == expected
    return


@pytest.mark.skip
def test_protein():
    log.info("Testing the polynomials on protein structures")
    polynomials = prepare_protein()
    for algorithm in algorithms.keys():
        for pdb, chain, bridges in random[algorithm].keys():
            expected = random[algorithm][(pdb, chain, bridges)]
            result = polynomials[algorithm][pdb].get(expected, 0)
            assert result == expected
    return


@pytest.mark.skip
def test_identifiers():
    log.info("Testing the identifiers assigned to the graph")
    return


@pytest.mark.skip
def test_find_loops():
    log.info("Testing the find_loops methods")
    for f, n, bridges in loops.keys():
        log.info("Testing file " + f)
        result = []
        for loop in find_loops(prefix['ideal'] + f, output_type=OutputType.XYZ, output='generator', arc_bridges=0):
            atoms = len(loop.split('\n'))
            g = Graph(loop)
            g.closed = True
            g.parse_closed()
            g.reduce()
            code = g.pdcode
            topology = jones(code)
            result.append({'code': code, 'topology': topology, 'atoms': atoms})
        log.info("\tFound loops: ")
        for loop in result:
            log.info('\t' + str(loop))
            print(loop)
        assert result == loops[(f, n, bridges)]


@pytest.mark.skip
def test_find_links():
    log.info("Testing the find_links methods")
    for f in links.keys():
        log.info("Testing file " + f)
        n_links = 0
        for link in find_links(prefix['ideal'] + f, output_type=OutputType.PDcode, output='generator'):
            log.info(str(link) + " in? " + str(list(links[f].keys())))
            assert link in links[f].keys()
            result = jones(link)
            assert result == links[f][link]
            n_links += 1
        assert n_links == links[f]['sum']
        for link in find_links(prefix['ideal'] + f, output_type=OutputType.XYZ, output='generator'):
            result = jones(link, closure=Closure.CLOSED)
            log.info(str(result) + " in? " + str(list(links[f].values())))
            assert result in links[f].values()
    return


@pytest.mark.skip
def test_find_thetas():
    log.info("Testing the find_thetas methods")
    for f in thetas.keys():
        log.info("Testing file " + f)
        n_thetas = 0
        for theta in find_links(prefix['ideal'] + f, output_type=OutputType.PDcode, output='generator'):
            log.info(str(theta) + " in? " + str(list(thetas[f].keys())))
            assert theta in thetas[f].keys()
            result = yamada(theta)
            assert result == thetas[f][theta]
            n_thetas += 1
        assert n_thetas == thetas[f]['sum']
        for theta in find_thetas(prefix['ideal'] + f, output_type=OutputType.XYZ, output='generator'):
            result = yamada(theta, closure=Closure.CLOSED)
            log.info(str(result) + " in? " + str(list(thetas[f].values())))
            assert result in thetas[f].values()
    return


@pytest.mark.skip
def test_find_handcuffs():
    log.info("Testing the find_handcuffs methods")
    for f in handcuffs.keys():
        log.info("Testing file " + f)
        n_handcuffs = 0
        for handcuff in find_handcuffs(prefix['ideal'] + f, output_type=OutputType.PDcode, output='generator'):
            log.info(str(handcuff) + " in? " + str(list(handcuffs[f].keys())))
            assert handcuff in handcuffs[f].keys()
            result = yamada(handcuff)
            assert result == handcuffs[f][handcuff]
            n_handcuffs += 1
        assert n_handcuffs == handcuffs[f]['sum']
        for handcuff in find_handcuffs(prefix['ideal'] + f, output_type=OutputType.XYZ, output='generator'):
            result = yamada(handcuff, closure=Closure.CLOSED)
            log.info(str(result) + " in? " + str(list(handcuffs[f].values())))
            assert result in handcuffs[f].values()
    return


if __name__ == '__main__':
    test_codes()
    test_ideal()
    test_random()
    # test_protein()
    # test_identifiers()
    # test_find_loops()
    # test_find_links()
    # test_find_thetas()
    # test_find_handcuffs()
