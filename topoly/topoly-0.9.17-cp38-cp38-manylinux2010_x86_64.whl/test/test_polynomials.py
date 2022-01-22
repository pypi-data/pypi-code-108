""" Testing the polynomials on idealized and real data.

Test by Pawel Dabrowski-Tumanski
Version from 07.04.2020
"""

from topoly import alexander, conway, jones, homfly, yamada, kauffman_bracket, kauffman_polynomial, blmho, \
    import_structure
from topoly.params import Closure
import pytest
from time import time
from datetime import datetime
import logging

# algorithms to be tested
algorithms_links = {'Jones': jones, 'Yamada': yamada, 'Kauffman Bracket': kauffman_bracket,
                    'Kauffman Polynomial': kauffman_polynomial} #, 'HOMFLY-PT': homfly, 'BLM/Ho': blmho}
algorithms_knots = {'Alexander': alexander, 'Conway': conway, 'Jones': jones, 'Yamada': yamada,
                    'Kauffman Polynomial': kauffman_polynomial, 'BLM/Ho': blmho}    #, 'HOMFLY-PT': homfly, 'Kauffman Bracket': kauffman_bracket}

# the achiral algorithms
achiral = ['Alexander', 'Conway', 'BLM/Ho']

# algorithms to be excluded in real structure calculation due to the length of calculations
exclusions = ['Kauffman Bracket']

# data for knot testing
knot_codes = ['-3_1', '+3_1', '4_1', '-5_1', '+5_1', '-6_1', '+6_1', '-6_2', '+6_2', '6_3', '-7_1', '+7_1', '-7_2',
              '+7_2', '+7_3', '-8_20', '+8_20']
knot_ideal = {'+3_1': 'data/knots/31.xyz', '-3_1': 'data/knots/m31.xyz', '4_1': 'data/knots/41.xyz',
              '+5_2': 'data/knots/52.xyz', '-5_2': 'data/knots/m52.xyz', '+6_1': 'data/knots/61.xyz',
              '-6_1': 'data/knots/m61.xyz'}
knot_curves = {('1j85', 'A'): '+3_1', ('2k0a', 'A'): '-3_1', ('5vik', 'A'): '4_1', ('2len', 'A'): '-5_2',
               ('3bjx', 'A'): '+6_1'}
unknowns = {'9_32': 'X[1,4,2,5];X[13,18,14,1];X[3,9,4,8];X[9,3,10,2];'
                    'X[7,15,8,14];X[15,11,16,10];X[5,12,6,13];X[11,17,12,16];X[17,7,18,6]'}
unknowns_dictionary = 'data/unknown_dictionary.py'
knot_data_prefix = 'data/knots/'

# data for link testing
link_codes = ['2^2_1', '4^2_1', '5^2_1', '6^2_1', '6^2_2', '6^2_3', '2^2_1#2^2_1']
link_ideal = {'2^2_1++': 'data/links/2-2_1.xyz', '4^2_1++*': 'data/links/4-2_1.xyz', '5^2_1++*': 'data/links/5-2_1.xyz',
              '6^2_1++': 'data/links/6-2_1.xyz', '6^2_2++': 'data/links/6-2_2.xyz', '6^2_3+-': 'data/links/6-2_3.xyz'}
link_curves = {'1arr': '2^2_1', '2lfk': '2^2_1'}#, '4a3x': '4^2_1'}
link_data_prefix = 'data/links/'

# data for unknots testing
unknots = {'0_1': 'V[1,1]', '0_1U0_1': 'V[1,1];V[2,2]', '0_1U0_1U0_1': 'V[1,1];V[2,2];V[3,3]',
           '0_1U0_1U0_1U0_1': 'V[1,1];V[2,2];V[3,3];V[4,4]'}

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def prepare_knot_polynomials_codes():
    polynomials = {}
    for algorithm in algorithms_knots.keys():
        polynomials[algorithm] = {}
        for code in knot_codes:
            log.info("Calculating: " + str(algorithm) + ' ' + str(code))
            data = import_structure(code)
            polynomials[algorithm][code] = algorithms_knots[algorithm](data, chiral=True)
    log.info('Results:')
    log.info('\t'.join(['{:20}'.format('Algorithm')] + ['{:>5}'.format(code) for code in knot_codes]))
    for algorithm in algorithms_knots.keys():
        log.info('\t'.join(['{:20}'.format(algorithm)] + ['{:>5}'.format(polynomials[algorithm][code])
                                                       for code in knot_codes]))
    log.info('========')
    return polynomials


def prepare_knot_polynomials_ideal():
    polynomials = {}
    for algorithm in algorithms_knots.keys():
        polynomials[algorithm] = {}
        for curve in knot_ideal.keys():
            log.info("Calculating" + ' ' + str(algorithm) + ' ' + str(curve))
            polynomials[algorithm][curve] = algorithms_knots[algorithm](knot_ideal[curve], closure=Closure.CLOSED,
                                                                        chiral=True)
    log.info('Results:')
    log.info('\t'.join(['{:20}'.format('Algorithm')] + ['{:>5}'.format(code) for code in list(knot_ideal.keys())]))
    for algorithm in algorithms_knots.keys():
        log.info('\t'.join(['{:20}'.format(algorithm)] + ['{:>5}'.format(polynomials[algorithm][curve]) for curve in
                                                       list(knot_ideal.keys())]))
    log.info('========')
    return polynomials


def prepare_knot_polynomials_real():
    polynomials = {}
    times = {}
    for algorithm in algorithms_knots.keys():
        if algorithm in exclusions:
            continue
        polynomials[algorithm] = {}
        times[algorithm] = {}
        for pdb, chain in knot_curves.keys():
            t0 = time()
            log.info("Calculating " + str(algorithm) + ' ' + str(pdb) + ' ' + str(chain))
            polynomials[algorithm][pdb] = algorithms_knots[algorithm](knot_data_prefix + pdb + '.pdb', tries=100,
                                                                      chiral=True, max_cross=25)
            times[algorithm][pdb] = time() - t0
    log.info('Results:')
    for algorithm in algorithms_knots.keys():
        if algorithm in exclusions:
            continue
        for pdb, chain in list(knot_curves.keys()):
            log.info('\t'.join(['{:20}'.format(algorithm), pdb + ' ' + chain] +
                            [str(polynomials[algorithm][pdb]) + ' (' + str(round(times[algorithm][pdb], 3)) + 's)']))
    log.info('========')
    return polynomials


def prepare_knot_unknown_polynomials(dictionary=''):
    polynomials = {}
    for algorithm in algorithms_knots.keys():
        polynomials[algorithm] = {}
        for knot in unknowns.keys():
            log.info("Calculating " + str(algorithm) + ' ' + str(knot) + ' dictionary: ' + str(dictionary))
            polynomials[algorithm][knot] = algorithms_knots[algorithm](unknowns[knot], chiral=True,
                                                   translate = True, external_dictionary=dictionary)
    return polynomials


def prepare_link_polynomials_codes():
    polynomials = {}
    for algorithm in algorithms_links.keys():
        polynomials[algorithm] = {}
        for code in link_codes:
            log.info("Calculating " + str(algorithm) + ' ' + str(code))
            data = import_structure(code)
            polynomials[algorithm][code] = algorithms_links[algorithm](data)

    log.info('Results:')
    log.info('\t'.join(['{:20}'.format('Algorithm')] + ['{:>5}'.format(code) for code in link_codes]))
    for algorithm in algorithms_links.keys():
        log.info('\t'.join(['{:20}'.format(algorithm)] + ['{:>5}'.format(polynomials[algorithm][code])
                                                       for code in link_codes]))
    log.info('========')
    return polynomials


def prepare_link_polynomials_ideal():
    polynomials = {}
    for algorithm in algorithms_links.keys():
        if algorithm in exclusions:
            continue
        polynomials[algorithm] = {}
        for curve in link_ideal.keys():
            log.info("Calculating " + str(algorithm) + ' ' + str(curve))
            polynomials[algorithm][curve] = algorithms_links[algorithm](link_ideal[curve], closure=Closure.CLOSED,
                                                                        chiral=True)
    log.info('Results:')
    log.info('\t'.join(['{:20}'.format('Algorithm')] + ['{:>5}'.format(code) for code in list(link_ideal.keys())]))
    for algorithm in algorithms_links.keys():
        if algorithm in exclusions:
            continue
        log.info('\t'.join(['{:20}'.format(algorithm)] + ['{:>5}'.format(polynomials[algorithm][curve]) for curve in
                                                       list(link_ideal.keys())]))
    log.info('========')
    return polynomials


def prepare_link_polynomials_real():
    polynomials = {}
    times = {}
    for algorithm in algorithms_links.keys():
        if algorithm in exclusions:
            continue
        polynomials[algorithm] = {}
        times[algorithm] = {}
        for pdb in link_curves.keys():
            t0 = time()
            log.info("Calculating " + str(algorithm) + ' ' + str(pdb))
            polynomials[algorithm][pdb] = algorithms_links[algorithm](link_data_prefix + pdb + '.xyz',
                                                                      tries=50, max_cross=25)
            times[algorithm][pdb] = time() - t0
            log.info("Done " + str(algorithm) + ' ' + str(pdb) + ' ' + "in: " + str(round(times[algorithm][pdb], 3)))

    log.info('Results:')
    for algorithm in algorithms_links.keys():
        if algorithm in exclusions:
            continue
        for pdb in list(link_curves.keys()):
            log.info('\t'.join(['{:20}'.format(algorithm), pdb] +
                            [str(polynomials[algorithm][pdb]) + ' (' + str(round(times[algorithm][pdb], 3)) + 's)']))
    log.info('========')
    return polynomials


def prepare_unknots():
    polynomials = {}
    for algorithm in algorithms_links.keys():
        polynomials[algorithm] = {}
        for unknot in unknots.keys():
            polynomials[algorithm][unknot] = algorithms_links[algorithm](unknots[unknot])
    log.info('Results')
    log.info('\t\t'.join(['{:20}'.format('Algorithm')] + list(unknots.keys())))
    for algorithm in algorithms_links.keys():
        log.info('\t\t'.join(['{:20}'.format(algorithm)] + [polynomials[algorithm][unknot] for unknot in unknots.keys()]))
    log.info('========')
    return polynomials


''' actual test'''
# @pytest.mark.skip
def test_knots_from_codes():
    log.info("Testing the polynomials on abstract codes")
    polynomials = prepare_knot_polynomials_codes()
    for algorithm in algorithms_knots.keys():
        for code in knot_codes:
            if algorithm not in achiral:
                assert code in polynomials[algorithm][code].split('|')
            else:
                assert code.replace('-', '').replace('+', '') in polynomials[algorithm][code].split('|')
    return


# @pytest.mark.skip
def test_knots_ideal_curves():
    log.info("Testing the polynomials on idealized data")
    polynomials = prepare_knot_polynomials_ideal()
    for algorithm in algorithms_knots.keys():
        for curve in knot_ideal.keys():
            if algorithm not in achiral:
                assert polynomials[algorithm][curve] == curve
            else:
                assert polynomials[algorithm][curve] == curve.replace('-', '').replace('+', '')
    return


# @pytest.mark.skip
def test_knots_real_data():
    log.info("Testing the polynomials on real structures")
    polynomials = prepare_knot_polynomials_real()
    for algorithm in algorithms_knots.keys():
        if algorithm in exclusions:
            continue
        for pdb, chain in knot_curves.keys():
            expected = knot_curves[(pdb, chain)]
            if algorithm in achiral:
                expected = expected.replace('-', '').replace('+', '')
            result = polynomials[algorithm][pdb].get(expected, 0)
            if result < 0.5:
                log.info("Warning! Structure " + pdb + ' (' + chain + '), knot ' + expected + ' with probability ' +
                      str(result) + ' in algorithm ' + algorithm)
            assert result > 0
    return


# @pytest.mark.skip
def test_unknown_knot():
    log.info("Testing the knots with unknown polynomials")
    polynomials = prepare_knot_unknown_polynomials()
    polynomials_known = prepare_knot_unknown_polynomials(dictionary=unknowns_dictionary, )
    for algorithm in algorithms_knots.keys():
        for knot in unknowns.keys():
            #assert polynomials[algorithm][knot] == 'Unknown (orTooManyCrossings)'
            assert polynomials[algorithm][knot] == 'Unknown'
            assert polynomials_known[algorithm][knot] == knot
    return


# @pytest.mark.skip
def test_links_from_codes():
    log.info("Testing the polynomials for links on codes")
    polynomials = prepare_link_polynomials_codes()
    for algorithm in algorithms_links.keys():
        for code in link_codes:
            assert code in polynomials[algorithm][code].split('|')
    return


# @pytest.mark.skip
def test_links_ideal_curves():
    log.info("Testing the polynomials for links on ideal structures")
    polynomials = prepare_link_polynomials_ideal()
    for algorithm in algorithms_links.keys():
        if algorithm in exclusions:
            continue
        for curve in link_ideal.keys():
            assert curve in polynomials[algorithm][curve].split('|')
    return


# @pytest.mark.skip
def test_links_real_data():
    log.info("Testing the polynomials for links on real structures")
    polynomials = prepare_link_polynomials_real()
    for algorithm in algorithms_links.keys():
        if algorithm in exclusions:
            continue
        for pdb in link_curves.keys():
            expected = link_curves[pdb]
            if expected == '2^2_1' and algorithm == 'Yamada':
                expected = '2^2_1|7^2_7'
            result = polynomials[algorithm][pdb].get(expected, 0)
            if result < 0.5:
                log.info("Warning! Structure " + pdb + ', links ' + expected + ' with probability ' +
                      str(result) + ' in algorithm ' + algorithm)
            assert result > 0
    return


# @pytest.mark.skip
def test_unknots():
    log.info("Testing the recognition of unknots")
    polynomials = prepare_unknots()
    for algorithm in algorithms_links.keys():
        for unknot in unknots.keys():
            assert polynomials[algorithm][unknot] == unknot
    return


if __name__ == '__main__':
    test_knots_from_codes()
    test_knots_ideal_curves()
    test_knots_real_data()
    test_unknown_knot()
    test_links_from_codes()
    test_links_ideal_curves()
    # test_links_real_data()
    test_unknots()

