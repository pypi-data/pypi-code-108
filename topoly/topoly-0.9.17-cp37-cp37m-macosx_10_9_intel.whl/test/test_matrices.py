""" Testing the matrix creation and drawing.

Test by Pawel Dabrowski-Tumanski
Version from 19.02.2020
"""

#!/usr/bin/python3
import os
import pytest
from topoly.topoly_knot import find_knots
from topoly import plot_matrix, translate_matrix, gln, find_spots, alexander, conway, jones, homfly, yamada, \
    kauffman_bracket, kauffman_polynomial, blmho, writhe
from topoly.params import Closure, OutputFormat, PlotFormat, Translate
from topoly.manipulation import check_cuda
import time

import logging

matrix_cutoff = 0.25    # the cutoff for matrix comparison
matrix_output_file = '2efv_matrix_tmp'
plot_ofile_protein = 'tmp_2efv_matrix'
output_data_file = 'tmp_matrix_1j85_knotprot'
spots_ofile = 'tmp_spots'
cutoffs = [0.48, 0.6, 0.9]
expected_file = 'data/KNOTS_2efv_A'
gln_codes = {'2lfk': [(24, 51), (52, 69)], '3suk': [(39, 76), (79, 138)]}
algorithms = {'Alexander': alexander, 'Conway': conway, 'Jones': jones, 'Yamada': yamada,
              'Kauffman Polynomial': kauffman_polynomial, 'BLM/Ho': blmho,
              'Writhe': writhe} #'HOMFLY-PT': homfly

log = logging.getLogger()

def read_knotprot_matrix(matrix_file):
    data = {}
    with open(matrix_file, 'r') as myfile:
        for line in myfile.readlines():
            if line[0] == '#':
                continue
            if 'UNKNOT' in line:
                return data
            d = line.split()
            ident = (int(d[0]), int(d[1]))
            data[ident] = {}
            for i in range(2, 30):
                for knot in d[i].split(','):
                    if knot == '0' or knot == '0_1':
                        continue
                    probability = 0.9 - (i - 2) * 0.03
                    data[ident][knot] = probability
    return data


def compare_output(dict1, dict2, cutoff=matrix_cutoff):
    difference = {}
    idents_all = list(set(dict1.keys()) | set(dict2.keys()))
    for ident in idents_all:
        if type(dict1.get(ident, {})) is dict:
            knots1 = set(dict1.get(ident, {}).keys())
        else:
            knots1 = set([dict1[ident]])
        if type(dict2.get(ident, {})) is dict:
            knots2 = set(dict2.get(ident, {}).keys())
        else:
            knots2 = set([dict2[ident]])
        knots_all = list(knots1 | knots2)
        for knot in knots_all:
            if type(dict1.get(ident, {})) is dict:
                v1 = dict1.get(ident, {}).get(knot, 0)
            else:
                v1 = 1
            if type(dict2.get(ident, {})) is dict:
                v2 = dict2.get(ident, {}).get(knot, 0)
            else:
                v2 = 1
            diff = abs(v1-v2)
            if diff > cutoff:
                if ident not in difference.keys():
                    difference[ident] = {}
                difference[ident][knot] = diff
    return difference

@pytest.mark.skip
@pytest.mark.cuda
def test_knotnet_directly():
    log.info("Testing matrix calculation directly with Alexander polynomial.")
    if not check_cuda():
        log.info("No CUDA deteted. Skipping.")
        return
    in_file = 'data/knots/2efv.xyz'
    ret = find_knots(in_file.encode('utf-8'), matrix_output_file.encode('utf-8'), 2, closure=2)
    print('finished find_knots')
    log.debug('knot_net result: ' + str(ret))
    print(str(ret))
    data = read_knotprot_matrix(matrix_output_file)
    log.debug('knot_net read matrix: ' + str(data))
    expected = read_knotprot_matrix(expected_file)
    differences = compare_output(data, expected)
    if differences:
        log.info('Differences: ' + str(differences))
    assert differences == {}
    assert ret == False
    log.info("========\n")
    return


# @pytest.mark.skip
def test_matrix_format():
    log.info("Testing different formats of matrix production with Conway polynomial.")
    result_matrix = conway('data/knots/1j85.pdb', matrix=True, closure=Closure.CLOSED,
                           matrix_format=OutputFormat.Matrix, translate=Translate.YES)
    result_dictionary = conway('data/knots/1j85.pdb', matrix=True, closure=Closure.CLOSED,
                               matrix_format=OutputFormat.Dictionary, translate=Translate.YES)
    result_knotprot = conway('data/knots/1j85.pdb', matrix=True, closure=Closure.CLOSED,
                             matrix_format=OutputFormat.KnotProt, translate=Translate.YES)
    conway('data/knots/1j85.pdb', matrix=True, closure=Closure.CLOSED, matrix_format=OutputFormat.KnotProt,
           matrix_filename=output_data_file, translate=Translate.YES)
    with open(output_data_file, 'r') as myfile:
        result_string = myfile.read()
    log.info('knots found in matrix: ' + str(list(result_matrix.keys())))
    print('knots found in matrix: ' + str(list(result_matrix.keys())))
    assert list(result_matrix.keys()) == ['3_1']

    # KnotProt output
    translated_result = translate_matrix(result_knotprot, output_format=OutputFormat.Dictionary)
    diff_dict_knot = compare_output(result_dictionary, translated_result)
    log.info('KnotProt output.')
    if diff_dict_knot != {}:
        log.info('Differences: ' + str(diff_dict_knot))
    assert diff_dict_knot == {}

    # Matrix output
    translated_result = translate_matrix(result_matrix.get('3_1', [[]]), output_format=OutputFormat.Dictionary,
                                         knot='3_1', beg=1)
    diff_dict_knot = compare_output(result_dictionary, translated_result)
    log.info('Matrix output.')
    if diff_dict_knot != {}:
        log.info('Differences: ' + str(diff_dict_knot))
    assert diff_dict_knot == {}

    # String output
    translated_result = translate_matrix(result_string, output_format=OutputFormat.Dictionary)
    diff_dict_knot = compare_output(result_dictionary, translated_result)
    log.info('String output.')
    if diff_dict_knot != {}:
        log.info('Differences: ' + str(diff_dict_knot))
    assert diff_dict_knot == {}
    log.info("========\n")
    return


@pytest.mark.skip
def test_matrix_plot_cutoff():
    log.info("Testing matrix plotting with different cutoffs for Conway polynomial.")
    sizes = []
    for cutoff in cutoffs:
        log.info('Cutoff: ' + str(cutoff))
        ofile = 'tmp_map_cutoff_' + str(cutoff)
        conway('data/knots/1j85.pdb', tries=10, map_filename=ofile, matrix_map=True, map_cutoff=cutoff, translate=Translate.YES)
        assert os.path.isfile('tmp_map_cutoff_' + str(cutoff) + '.png')
        sizes.append(os.path.getsize(ofile + '.png'))

    log.info("Sizes:\t", ', '.join([str(cutoff) + ' ' + str(size) for cutoff, size in zip(cutoffs, sizes)]))

    for k in range(len(sizes)-1):
        assert sizes[k] >= sizes[k+1]

    log.info("========\n")
    return


# @pytest.mark.skip
def test_matrix_plot_polynomials():
    logging.basicConfig(level=logging.INFO)
    log.info("Testing matrix plotting with different polynomials.")
    times = {}

    for algorithm in algorithms.keys():
        log.info(algorithm)
        t0 = time.time()
        ofile = 'matrix_' + algorithm.replace('/', '')
        algorithms[algorithm]('data/knots/1j85.pdb', tries=3, map_filename=ofile, matrix_map=True, translate=Translate.YES, parallel_workers=1)
        times[algorithm] = time.time() - t0
        time.sleep(7)   # some multiprocessing bug!
    log.info("Times:")
    for algorithm in algorithms.keys():
        assert os.path.getsize('matrix_' + algorithm.replace('/', '') + '.png') > 0
        log.info(algorithm + ' ' + str(times[algorithm]))
    log.info("========\n")
    return


# @pytest.mark.skip
def test_matrix_plot_formats():
    log.info("Testing matrix plotting formats.")
    data = conway('data/knots/1j85.pdb', tries=1, matrix=True)
    for plot_format in dir(PlotFormat):
        if '_' in plot_format:
            continue
        log.info(plot_format)
        ofile = '1j85_matrix'
        plot_matrix(data, map_fileformat=plot_format, map_filename=ofile)
        assert os.path.getsize(ofile + '.' + plot_format) > 0
    log.info("========\n")
    return


# @pytest.mark.skip
def test_gln_matrix():
    log.info("Testing GLN matrix plotting.")
    for code in gln_codes.keys():
        log.info(code)
        f = 'data/' + code + '.pdb'
        bridges = gln_codes[code]
        plot_ofile = 'tmp_GLN_plot_' + code
        gln(f, chain1_boundary=bridges[0], chain2_boundary=bridges[1], 
            matrix_map=True, map_filename=plot_ofile)
        assert os.path.isfile(plot_ofile + '.png')
    log.info("========\n")
    return


# @pytest.mark.skip
def test_plamkas():
    log.info("Testing finding spots.")
    result = alexander('data/composite.xyz', matrix_map=True, closure=Closure.CLOSED, 
                       translate=Translate.YES, cuda=False, map_filename=spots_ofile)
    spots = find_spots(result)
    log.info("Found: " + str(spots))
    assert set(spots.keys()) == {'3_1', '3_1#3_1|8_20'}
    assert len(spots['3_1']) == 2
    assert len(spots['3_1#3_1|8_20']) == 1
    log.info("========\n")
    return


def clean():
    try:
        os.remove(matrix_output_file)
        os.remove(output_data_file)
        os.remove(spots_ofile)
        for cutoff in cutoffs:
            os.remove('tmp_map_cutoff_' + str(cutoff) + '.png')
        os.remove(plot_ofile_protein + '.png')
        for code in gln_codes.keys():
            os.remove('tmp_GLN_plot_' + code + '.png')
        for algorithm in algorithms.keys():
            ofile = 'matrix_' + algorithm.replace('/', '')
            os.remove(ofile + '.png')
        for plot_format in dir(PlotFormat):
            if '_' in plot_format:
                continue
            os.remove('1j85_matrix.' + plot_format)
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    #test_knotnet_directly()
    test_matrix_format()
    #test_matrix_plot_cutoff()
    #test_matrix_plot_polynomials()
    #test_matrix_plot_formats()
    #test_gln_matrix()
    #test_plamkas()
    clean()
