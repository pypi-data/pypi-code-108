from topoly import gln
from math import sqrt
import pytest
import logging

curve3 = '1 1.0 2.0 3.0\n2 2.0 2.0 5.0\n3 4.0 3. -1.\n4 -1 -1 2'
curve4 = 'chain_6T1D_A.xyz' # add_structure('6t1d.pdb', [(36,86), (87,300)], chain1='A')

prefix = 'data/lassos/'
average_tries = [10, 400]
max_densities = [1, 15]

test_data = {
    'case1': {'file1': 'lasso_01.xyz',
              'model1': '',
              'chain1': '',
              'file2': '',
              'model2': '',
              'chain2': '',
              'boundaries': [(1, 35), (36, 60)],
              'basic': -0.187,
              'avg': {10: -0.1, 400: -0.045},
              'max': {'default': {'whole': [-0.187], 'wholeCH1_fragmentCH2': [-0.225, '36-55'],
                                  'wholeCH2_fragmentCH1': [-0.205, '7-35'], 'fragments': [], 'avg': None, 'matrix': None},
                      1: {'whole': [-0.187], 'wholeCH1_fragmentCH2': [-0.225, '36-55'],
                          'wholeCH2_fragmentCH1': [-0.205, '7-35'], 'fragments': [-0.249, '7-35', '36-55'], 'avg': None, 'matrix': None},
                      15: {'whole': [-0.187], 'wholeCH1_fragmentCH2': [-0.225, '36-55'],
                           'wholeCH2_fragmentCH1': [-0.205, '7-35'], 'fragments': [-0.187, '1-35', '36-60'], 'avg': None, 'matrix': None}}},
    'case2': {'file1': '2KUM_A.pdb',
              'model1': '',
              'chain1': '',
              'file2': '',
              'model2': '',
              'chain2': '',
              'boundaries': [(9, 38), (39, 88)],
              'basic': 0.107,
              'avg': {10: 0.2, 400: 0.067},
              'max': {'default': {'whole': [0.107], 'wholeCH1_fragmentCH2': [0.872, '48-77'],
                                  'wholeCH2_fragmentCH1': [0.325, '11-34'], 'fragments': [], 'avg': None, 'matrix': None},
                      1: {'whole': [0.107], 'wholeCH1_fragmentCH2': [0.872, '48-77'],
                          'wholeCH2_fragmentCH1': [0.325, '11-34'], 'fragments': [0.877, '9-34', '49-78'], 'avg': None, 'matrix': None},
                      15: {'whole': [0.107], 'wholeCH1_fragmentCH2': [0.872, '48-77'],
                           'wholeCH2_fragmentCH1': [0.325, '11-34'], 'fragments': [0.312, '9-38', '54-69'], 'avg': None, 'matrix': None}}}
}

log = logging.getLogger()

def add_structure(file1, boundaries, model1='', chain1='', file2='', model2='', chain2=''):
    f1 = prefix + file1
    if file2:
        f2 = prefix + file2
    else:
        f2 = ''
    basic = gln(f1, chain2=f2, chain1_boundary=boundaries[0], chain2_boundary=boundaries[1],
                pdb_chain1=chain1, pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2)
    avg = {}
    for try_number in average_tries:
        avg[try_number] = gln(f1, chain2=f2, chain1_boundary=boundaries[0], chain2_boundary=boundaries[1],
                              pdb_chain1=chain1, pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2, avgGLN=True,
                              avg_tries=try_number)
    max_res = {'default': gln(f1, chain2=f2, chain1_boundary=boundaries[0], chain2_boundary=boundaries[1],
                              pdb_chain1=chain1, pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2, maxGLN=True)}
    for density in max_densities:
        max_res[density] = gln(f1, chain2=f2, chain1_boundary=boundaries[0], chain2_boundary=boundaries[1],
                               pdb_chain1=chain1, pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2, maxGLN=True,
                               max_density=density)
    result = {'file1': file1,
              'model1': model1,
              'chain1': chain1,
              'file2': file2,
              'model2': model2,
              'chain2': chain2,
              'boundaries': boundaries,
              'basic': basic,
              'avg': avg,
              'max': max_res
              }

    return result


def prepare_basic():
    results = {}
    for curve in test_data.keys():
        f1, f2 = prefix + test_data[curve]['file1'], prefix + test_data[curve]['file2']
        if f2 == prefix:
            f2 = ''
        chain1, chain2 = test_data[curve]['chain1'], test_data[curve]['chain2']
        model1, model2 = test_data[curve]['model1'], test_data[curve]['model2']
        boundaries = test_data[curve]['boundaries']
        results[curve] = gln(f1, chain2=f2, chain1_boundary=boundaries[0], 
                             chain2_boundary=boundaries[1], pdb_chain1=chain1, 
                             pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2)
        log.info(f1 + ' ' + f2 + ' ' + str(results[curve]))
    return results


def prepare_max():
    results = {}
    for curve in test_data.keys():
        f1, f2 = prefix + test_data[curve]['file1'], prefix + test_data[curve]['file2']
        if f2 == prefix:
            f2 = ''
        chain1, chain2 = test_data[curve]['chain1'], test_data[curve]['chain2']
        model1, model2 = test_data[curve]['model1'], test_data[curve]['model2']
        boundaries = test_data[curve]['boundaries']
        max_res = {'default': gln(f1, chain2=f2, chain1_boundary=boundaries[0], chain2_boundary=boundaries[1],
                                  pdb_chain1=chain1, pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2, maxGLN=True)}
        log.info(f1 + ' ' + f2 + ' ' + "density: default" + ' ' + str(max_res['default']))

        for density in max_densities:
            max_res[density] = gln(f1, chain2=f2, chain1_boundary=boundaries[0], chain2_boundary=boundaries[1],
                                   pdb_chain1=chain1, pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2, maxGLN=True,
                                   max_density=density)
            log.info(f1 + ' ' + f2 + " density " + str(density) + ' ' + str(max_res[density]))

        results[curve] = max_res
    return results


def prepare_avg():
    results = {}
    for curve in test_data.keys():
        f1, f2 = prefix + test_data[curve]['file1'], prefix + test_data[curve]['file2']
        if f2 == prefix:
            f2 = ''
        chain1, chain2 = test_data[curve]['chain1'], test_data[curve]['chain2']
        model1, model2 = test_data[curve]['model1'], test_data[curve]['model2']
        boundaries = test_data[curve]['boundaries']
        avg = {}
        for try_number in average_tries:
            avg[try_number] = gln(f1, chain2=f2, chain1_boundary=boundaries[0], chain2_boundary=boundaries[1],
                                  pdb_chain1=chain1, pdb_model1=model1, pdb_chain2=chain2, pdb_model2=model2, avgGLN=True,
                                  avg_tries=try_number)
            log.info(f1 + ' ' + f2 + " density " + ' ' + str(try_number) + ' ' + str(avg[try_number]['avg']))

        results[curve] = avg
    return results


def similar_values(v1,v2,prop=0.1,eps=0.0001):
#returns true if v1 is in [0.9*v2 -eps, 1.1*v2 +eps] '''
    if prop<0 or prop>1: prop=0.1
    similar = False
    if v1>=0 and v1>=(1-prop)*v2-eps and v1<=(1+prop)*v2+eps: similar=True
    if v1<=0 and v1>=(1+prop)*v2-eps and v1<=(1-prop)*v2+eps: similar=True
    return similar


''' Actual testing '''
# @pytest.mark.skip
def test_gln_basic():
    log.info("Testing the basic GLN functionality")
    results = prepare_basic()
    for curve in test_data.keys():
        #assert results[curve] == test_data[curve]['basic']
        #assert similar_values(results[curve], test_data[curve]['basic']), f"Different basic GLN values for curve {curve}: {results[curve]}, {test_data[curve]['basic']}"
        assert similar_values(results[curve], test_data[curve]['basic'])
    return



# @pytest.mark.skip
def test_gln_max_mode():
    log.info("Testing the 'max' mode in GLN function")
    results = prepare_max()
    for curve in test_data.keys():
        for max_density in test_data[curve]['max'].keys():
            #assert results[curve][max_density] == test_data[curve]['max'][max_density]
            assert similar_values(results[curve][max_density]['whole'][0], test_data[curve]['max'][max_density]['whole'][0]) and similar_values(results[curve][max_density]['wholeCH1_fragmentCH2'][0], test_data[curve]['max'][max_density]['wholeCH1_fragmentCH2'][0]) and similar_values(results[curve][max_density]['wholeCH2_fragmentCH1'][0], test_data[curve]['max'][max_density]['wholeCH2_fragmentCH1'][0])
    return


# @pytest.mark.skip
def test_gln_avg_mode():
    log.info("Testing the 'avg' mode in GLN function")
    results = prepare_avg()
    for curve in test_data.keys():
        for avg in test_data[curve]['avg'].keys():
            epsilon = 20/sqrt(avg)           # this is a really coarse condition. Maybe there may be a better one?
            # epsilon = 2/sqrt(avg)         # Wanda's test condition
            assert abs(results[curve][avg]['avg'] - test_data[curve]['avg'][avg]) < epsilon
    return


if __name__ == '__main__':
    test_gln_basic()
    test_gln_max_mode()
    test_gln_avg_mode()
