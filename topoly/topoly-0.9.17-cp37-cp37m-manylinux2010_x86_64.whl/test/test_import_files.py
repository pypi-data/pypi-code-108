""" Testing the import of the data.

Test by Pawel Rubach and Pawel Dabrowski-Tumanski
Version from 17.02.2020
"""

import os
import shutil
import urllib
import pytest
import logging
from topoly.topoly_preprocess import chain_read, close_chain_2points
from topoly.params import Bridges


from topoly.graph import Graph

INPUT_FOLDER = '/tmp'
proteins = [('6i7s', 'A'), ('1j85', 'A'), ('4wlr', 'A'), ('3bjx', 'A')]
file_types = ['cif', 'pdb', 'nxyz']

bridges_expected = {'1a8e':
        {'all': [[9, 48], [19, 39], [118, 194], [137, 331], [158, 174], [161, 179], [171, 177], [227, 241], [63, 95],
                 [188, 63], [249, 63], [188, 95], [249, 95], [249, 188]],
         'ssbond': [[9, 48], [19, 39], [118, 194], [137, 331], [158, 174], [161, 179], [171, 177], [227, 241]],
         'ion': [[63, 95], [188, 63], [249, 63], [188, 95], [249, 95], [249, 188]],
         'covalent': []},

                    '1rpb':
        {'all': [[1, 13], [7, 19], [1, 9]],
         'ssbond': [[1, 13], [7, 19]],
         'ion': [],
         'covalent': [[1, 9]]}}


PDB_URL = "http://files.rcsb.org/download/{0}.{1}"
#KNOTPROT_URL = "https://knotprot.cent.uw.edu.pl/chains/{0}/{2}/chain.xyz.txt"

download_urls = {'cif': PDB_URL, 'pdb': PDB_URL}

log = logging.getLogger()


def download_if_not_exist(url, filename, dir=INPUT_FOLDER):
    file = os.path.join(dir, filename)
    if not os.path.isfile(file) or os.path.getsize(file) == 0:
        f = urllib.request.urlopen(url)
        fw = open(file, "wb")
        fw.write(f.read())
        fw.close()
        f.close()
    return file


# Setup test - download input files
def setup_module():
    for prot in proteins:
        for f_type in file_types:
            if f_type in download_urls.keys():
                download_if_not_exist(download_urls[f_type].format(prot[0], f_type, prot[1]), prot[0] + '.' + f_type)
        shutil.copyfile(os.path.join('data/import/', prot[0] + '_' + prot[1] + '.xyz'),
                        os.path.join(INPUT_FOLDER, prot[0] + '.nxyz'))


def import_coords_for_prot(protein):
    from Bio import BiopythonWarning
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', BiopythonWarning)
        res = {}
        prev = None
        for f_type in file_types:
            log.info(f_type)
            file = os.path.join(INPUT_FOLDER, protein[0] + '.' + f_type)
            res[f_type] = str(Graph(file, chain=protein[1]).coordinates)
            #log.info(res[f_type])
            if prev:
                assert res[f_type] == prev


# @pytest.mark.skip
def test_chain_read_and_close():
    log.info("Testing chain reading and closing with direct C approach")
    in_file = 'data/t31_numbered_cut.xyz'
    log.info("Reading chain from: " + str(in_file))
    chain, unable = chain_read(in_file.encode('utf-8'))
    log.debug("Got: " + str(chain))
    assert unable == False
    assert chain[1]['A']['x'] == 0.0780421837759
    assert chain[1]['A']['z'] == 0.0776457135308

    res, chain_out = close_chain_2points(chain)
    assert res == 0
    assert len(chain_out) > 37
    return


# @pytest.mark.skip
def test_import_coords():
    log.info("Testing importing coordinates")
    setup_module()
    for prot in proteins:
        log.info(prot)
        import_coords_for_prot(prot)
    return


# @pytest.mark.skip
def test_bridges():
    log.info("Testing different bridges types")
    bridges = {}
    for code in bridges_expected.keys():
        bridges[code] = {}
        for bridge_type in ['all', 'ssbond', 'ion', 'covalent']:
            bridges[code][bridge_type] = Graph('data/spatial_graphs/' + code + '.pdb', bridges_type=bridge_type).bridges
    log.info("Results:")
    log.info(str(bridges))
    assert bridges == bridges_expected
    return


# @pytest.mark.skip
def test_printing():
    log.info("Testing printing the coordinates")
    return


# @pytest.mark.skip
def test_arcs():
    log.info("Testing reading the files with more than one arc.")
    return


if __name__ == '__main__':
    setup_module()
    test_chain_read_and_close()
    test_import_coords()
    test_bridges()
    test_printing()
    test_arcs()
