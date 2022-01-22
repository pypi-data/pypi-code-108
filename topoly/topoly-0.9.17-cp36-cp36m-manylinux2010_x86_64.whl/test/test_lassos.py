from topoly import make_surface, lasso_type
from topoly.params import DensitySurface, PrecisionSurface, SurfacePlotFormat
import pytest
import os
import logging
import sys

log = logging.getLogger()
curve3 = '1 1.0 2.0 3.0\n2 2.0 2.0 5.0\n3 4.0 3. -1.\n4 -1 -1 2'
curve4 = [[ 1,   0.000000,   0.000000,   0.000000],
          [ 2,   1.000000,   0.000000,   0.000000],
          [ 3,   1.519376,   0.854546,   0.000000],
          [ 4,   1.228102,  -0.065844,  -0.260848],
          [ 5,   0.409454,  -0.443460,  -0.693541],
          [ 6,   1.042599,  -0.117467,   0.008497],
          [ 7,   1.974961,  -0.255223,   0.342749],
          [ 8,   2.506924,  -0.063232,  -0.481966],
          [ 9,   1.931307,   0.669387,  -0.118737],
          [10,   1.702770,   1.288413,   0.632647],
          [11,   2.323304,   0.644159,   1.079721],
          [12,   2.102030,   0.066894,   0.293717],
          [13,   2.514897,   0.810465,  -0.232252],
          [14,   2.894818,   1.335749,   0.529152],
          [15,   3.817838,   1.228070,   0.898530],
          [16,   4.722993,   1.646503,   0.973420],
          [17,   4.031658,   2.350980,   1.133941],
          [18,   3.162758,   2.547533,   0.679652],
          [19,   2.460517,   1.990879,   0.235811],
          [20,   1.675851,   1.371631,   0.264641],
          [21,   0.774931,   1.018335,   0.516685],
          [22,   0.052756,   1.119516,  -0.167585],
          [23,   0.186433,   1.774806,  -0.911040],
          [24,  -0.469058,   1.036846,  -0.750581],
          [25,   0.015815,   0.897981,   0.112909],
          [26,  -0.434444,   0.923269,  -0.779631],
          [27,   0.514195,   0.834903,  -0.475863],
          [28,  -0.433468,   0.927671,  -0.170364],
          [29,  -0.776257,   0.125372,   0.318320],
          [30,  -0.062597,  -0.048650,   0.996852],
          [31,   0.203395,  -0.239104,   0.051879],
          [32,   0.487903,  -0.737077,   0.871072],
          [33,   0.657560,   0.233873,   0.702332],
          [34,   1.024857,   0.425565,  -0.207803],
          [35,   0.326788,   0.928416,   0.301942],
          [36,   1.246893,   0.967434,  -0.087781],
          [37,   1.136249,   1.480931,  -0.938709],
          [38,   0.867092,   1.462408,  -1.901627],
          [39,   1.226895,   0.896308,  -2.643295],
          [40,   0.231314,   0.881452,  -2.550573],
          [41,   0.535998,   0.999069,  -1.605409],
          [42,   0.488348,   1.990193,  -1.481303],
          [43,   0.111324,   1.928334,  -0.557167],
          [44,  -0.078468,   1.118546,  -1.112346],
          [45,  -1.004991,   1.477029,  -1.226561],
          [46,  -0.893760,   1.198590,  -0.272570],
          [47,  -0.772393,   1.287248,   0.716071],
          [48,   0.122552,   1.640242,   0.443181],
          [49,  -0.614726,   1.547179,  -0.225969],
          [50,  -0.917517,   0.855001,   0.429170],
          [51,  -1.875319,   1.123794,   0.327354],
          [52,  -2.830895,   0.935985,   0.100195],
          [53,  -2.799883,   0.945225,   1.099672],
          [54,  -3.523426,   1.529180,   0.731593],
          [55,  -2.985147,   0.969932,   1.362066],
          [56,  -2.992716,   1.877266,   0.941724],
          [57,  -3.663064,   2.136737,   1.636927],
          [58,  -4.364785,   1.900624,   2.309116],
          [59,  -4.441840,   1.815059,   3.302465],
          [60,  -3.898437,   1.012764,   3.549521]]

epsilon = 5 #results can differ with 5% and test will be passed - since some randomness in algorithms, and changes in EPS value (comparison of numbers, rounding to 0, etc)
surface_plot_formats = {'VMD': 1, 'JSMOL': 2, 'MATHEMATICA': 4}
smooth_parameters = [10, 20, 50]
reduction_pattern = [(5, 3, 3), (0, 3, 3), (0, 0, 0)]
extensions = {'VMD': '.tcl', 'JSMOL': '.jms', 'MATHEMATICA': '.m'}

os_type = sys.platform

lassos = {
    'curve1': {'data': 'data/lassos/lasso_01.xyz',
               'bridges': [[1, 35], [5, 50]],
               'basic': {(1, 35): 'L0', (5, 50): 'L0'},
               'detailed': {(1, 35): {'class': 'L0', 'beforeN': [], 'beforeC': [], 'crossingsN': [], 'crossingsC': [],
                                      'Area': 12.3505, 'loop_length': 35.9428, 'Rg': 2.06739, 'smoothing_iterations': 0},
                            (5, 50): {'class': 'L0', 'beforeN': ['+1', '-2', '+3'], 'beforeC': [], 'crossingsN': [],
                                      'crossingsC': [], 'Area': 20.0585, 'loop_length': 48.3356, 'Rg': 2.06739,
                                      'smoothing_iterations': 0}},
               'surface': {'VMD': {(1, 35): 'data/lassos/surface_lasso_01.xyz_1_35_VMD.tcl',
                                   (5, 50): 'data/lassos/' + os_type + '/surface_lasso_01.xyz_5_50_VMD.tcl'},
                           'JSMOL': {(1, 35): 'data/lassos/surface_lasso_01.xyz_1_35_JSMOL.jms',
                                     (5, 50): 'data/lassos/' + os_type  + '/surface_lasso_01.xyz_5_50_JSMOL.jms'},
                           'MATHEMATICA': {(1, 35): 'data/lassos/surface_lasso_01.xyz_1_35_MATHEMATICA.m',
                                           (5, 50): 'data/lassos/' + os_type  + '/surface_lasso_01.xyz_5_50_MATHEMATICA.m'}},
               'reduction': {(5, 3, 3): {(1, 35): 'L0', (5, 50): 'L0'},
                             (0, 3, 3): {(1, 35): 'L0', (5, 50): 'L0'},
                             (0, 0, 0): {(1, 35): 'L0', (5, 50): 'L+3N'}},
               'smooth': {10: {(1, 35): 'L0', (5, 50): 'L0'},
                          20: {(1, 35): 'L0', (5, 50): 'L0'},
                          50: {(1, 35): 'L0', (5, 50): 'L0'}}},
    'curve2': {'data': 'data/lassos/2KUM_A.pdb',
               'bridges': [[9, 38], [10, 53]],
               'basic': {(9, 38): 'L0', (10, 53): 'L0'},
               'detailed': {(9, 38): {'class': 'L0', 'beforeN': [], 'beforeC': ['-44', '+53'], 'crossingsN': [],
                                      'crossingsC': [], 'Area': 396.805, 'loop_length': 114.782, 'Rg': 11.95,
                                      'smoothing_iterations': 0},
                            (10, 53): {'class': 'L0', 'beforeN': [], 'beforeC': ['+53'], 'crossingsN': [],
                                       'crossingsC': [], 'Area': 465.492, 'loop_length': 169.482, 'Rg': 11.95,
                                       'smoothing_iterations': 0}},
               'surface': {'VMD': {(9, 38): 'data/lassos/surface_2KUM_A.pdb_9_38_VMD.tcl',
                                   (10, 53): 'data/lassos/surface_2KUM_A.pdb_10_53_VMD.tcl'},
                           'JSMOL': {(9, 38): 'data/lassos/surface_2KUM_A.pdb_9_38_JSMOL.jms',
                                     (10, 53): 'data/lassos/surface_2KUM_A.pdb_10_53_JSMOL.jms'},
                           'MATHEMATICA': {(9, 38): 'data/lassos/surface_2KUM_A.pdb_9_38_MATHEMATICA.m',
                                           (10, 53): 'data/lassos/surface_2KUM_A.pdb_10_53_MATHEMATICA.m'}},
               'reduction': {(5, 3, 3): {(9, 38): 'L-2C', (10, 53): 'L0'},
                             (0, 3, 3): {(9, 38): 'L-2C', (10, 53): 'L0'},
                             (0, 0, 0): {(9, 38): 'L-2C', (10, 53): 'L+1C'}},
               'smooth': {10: {(9, 38): 'L0', (10, 53): 'L0'},
                          20: {(9, 38): 'L0', (10, 53): 'L0'},
                          50: {(9, 38): 'L0', (10, 53): 'L0'}}}
}


def add_lasso(f, bridges):
    lasso_data = {}
    lasso_data['data'] = f
    lasso_data['bridges'] = bridges
    lasso_data['basic'] = lasso_type(f, bridges)
    lasso_data['detailed'] = lasso_type(f, bridges, more_info=True)
    lasso_data['reduction'] = {}
    for reduction in reduction_pattern:
        lasso_data['reduction'][reduction] = lasso_type(f, bridges, min_dist=reduction)
    lasso_data['surface'] = {}
    for plot_type in surface_plot_formats.keys():
        lasso_data['surface'][plot_type] = {}
        for bridge in bridges:
            output = '_'.join([f, str(bridge[0]), str(bridge[1]), plot_type])
            lasso_data['surface'][plot_type][tuple(bridge)] = 'surface_' + output + extensions[plot_type]
            lasso_type(f, bridge, pic_files=surface_plot_formats[plot_type], output_prefix=output)
    lasso_data['smooth'] = {}
    for s_value in smooth_parameters:
        lasso_data['smooth'][s_value] = lasso_type(f, bridges, smooth=s_value)
    return lasso_data


def diff_files(f1, f2):
    with open(f1, 'r') as file1:
        with open(f2, 'r') as file2:
            diff = set(file1).difference(file2) # we check if everything in file2 is also in file1
    diff.discard('\n')
    return diff


# MATHEMATICA:
#l40=Line[{{-0.415745,2.25063,-0.240674},{-1.13092,1.81916,0.309202}}];
# gtr=Graphics3D[{Opacity[.8], EdgeForm[{Thickness[0.002]}], RGBColor[.6, .6, .6],Polygon[{{{1,0,0},{0.977748,0.104372,0.0264233},{0.503094,0.0776025,0.101267}},{{0,0,0},{1,0,0},{0.503094,0.0776025,0.101267}},{{0.725648,0.961629,0},{0.840572,0.585187,0.0264233},{1,0,0}},{{1,0,0},{0.840572,0.585187,0.0264233},{0.977748,0.104372,0.0264233}}, ...
# JSMOL:
#draw polygon2 [{0.725648 0.961629 0} {0.840572 0.585187 0.0264233} {1 0 0}];
# TCL:
#draw triangle {1 0 0} {0.977748 0.104372 0.0264233} {0.503094 0.0776025 0.101267}

def diff_list_numbers(l1,l2):
    if len(l1)!=len(l2): return True
    for i in range(len(l1)):
        if l1[i]==l2[i]: continue
        if 100.*abs(l1[i]-l2[i])/max(l1[i],l2[i]) > epsilon: return True
    return False 

def diff_files2(f1, f2):
    fl1, fl2 = open(f1,"r"), open(f2,"r")
    lines1, lines2 = [l for l in fl1.readlines() if l!='\n'], [l for l in fl2.readlines() if l!='\n']
    fl1.close()
    fl2.close()
    if len(lines1) != len(lines2):
        print("DIFF len:",len(lines1),len(lines2))
        return True
    for i in range(len(lines1)):
        l1,l2 = lines1[i],lines2[i] 
        if "=Line[{{" in l1:
            if "=Line[{{" not in l2: return True
            [r1, r2] = [ l.split('{{', 1)[1].split('}}',1)[0].split('},{')  for l in [l1,l2] ]    #r1 = ['-0.415745,2.25063,-0.240674','-1.13092,1.81916,0.309202']
            [r1, r2] = [ [float(x) for x in r[0].split(",")+r[1].split(",")]  for r in [r1,r2] ]  #r1 = [-0.415745,2.25063,-0.240674,-1.13092,1.81916,0.309202]
            if diff_list_numbers(r1,r2):
                print("DIFF lines:\n",l1,"\n",l2) 
                return True
        elif "gtr=Graphics3D" in l1:
            if "gtr=Graphics3D" not in l2: return True
            [r1, r2] = [ l.split('Polygon[{{{')[1].split('}}}]')[0].split('}},{{')  for l in [l1,l2] ]  	   #r1 = ['1,0,0},{2,3,4},{5,0,1', '1,3,0},{4,3,1},{3,10,12', ...]
            [r1, r2] = [ [float(x) for t in r for P in t.split('},{') for x in P.split(",")]  for r in [r1,r2] ]   #r1 = [1,0,0,2,3,4,5,0,1,4,3,1,3,10,12,...]
            if diff_list_numbers(r1,r2):
                print("DIFF lines with gtr") 
                return True
        elif "draw polygon" in l1:
            if "draw polygon" not in l2: return True
            [r1, r2] = [ l.split('[{')[1].split('}]')[0].split('} {')  for l in [l1,l2] ]  #r1 = ['0.725648 0.961629 0', '0.840572 0.585187 0.0264233', '1 0 0']
            [r1, r2] = [ [float(x) for t in r for x in t.split()]  for r in [r1,r2] ]       
            if diff_list_numbers(r1,r2):
                print("DIFF lines:\n",l1,"\n",l2) 
                return True
        elif "draw triangle" in l1:
            if "draw triangle" not in l2: return True
            [r1, r2] = [ l.split('{',1)[1].split('} {')  for l in [l1,l2] ]  #r1 = ['0.725648 0.961629 0', '0.840572 0.585187 0.0264233', '1 0 0}']
            r1[2], r2[2] = r1[2].split('}')[0], r2[2].split('}')[0]
            [r1, r2] = [ [float(x) for t in r for x in t.split()]  for r in [r1,r2] ]       
            if diff_list_numbers(r1,r2):
                print("DIFF lines:\n",l1,"\n",l2) 
                return True

    return False
    


def prepare_lassos_bridges():
    return


def prepare_lassos_basic():
    lasso_data = {}
    for lasso in lassos.keys():
        lasso_data[lasso] = lasso_type(lassos[lasso]['data'], lassos[lasso]['bridges'])
        log.info(str(lassos[lasso]['data']) + ' ' + str(lassos[lasso]['bridges']) + ' ' + str(lasso_data[lasso]))
    return lasso_data


def prepare_lassos_detailed():
    lasso_data = {}
    for lasso in lassos.keys():
        lasso_data[lasso] = lasso_type(lassos[lasso]['data'], lassos[lasso]['bridges'],
                                       more_info=True)
        log.info(str(lassos[lasso]['data']) + ' ' + str(lassos[lasso]['bridges']) + ' ' + str(lasso_data[lasso]))
    return lasso_data


def prepare_lassos_reduction():
    lasso_data = {}
    for lasso in lassos.keys():
        lasso_data[lasso] = {}
        for reduction in reduction_pattern:
            lasso_data[lasso][reduction] = lasso_type(lassos[lasso]['data'], lassos[lasso]['bridges'],
                                                      min_dist=reduction)
            log.info(str(lassos[lasso]['data']) + ' ' + str(lassos[lasso]['bridges'])  + ' ' + str(reduction) + ' ' + str(lasso_data[lasso][reduction]))
    return lasso_data


def prepare_lassos_surfaces():
    lasso_data = {}
    for lasso in lassos.keys():
        lasso_data[lasso] = {}
        for plot_type in surface_plot_formats.keys():
            lasso_data[lasso][plot_type] = {}
            for bridge in lassos[lasso]['bridges']:
                name = lassos[lasso]['data'].split('/')[-1]
                output = '_'.join(['tmp', name, str(bridge[0]), str(bridge[1]), plot_type])
                lasso_data[lasso][plot_type][tuple(bridge)] = 'surface_' + output + extensions[plot_type]
                lasso_type(lassos[lasso]['data'], bridge, pic_files=surface_plot_formats[plot_type],
                           output_prefix=output)
    return lasso_data


def prepare_lassos_smoothing():
    lasso_data = {}
    for lasso in lassos.keys():
        lasso_data[lasso] = {}
        for s_value in smooth_parameters:
            lasso_data[lasso][s_value] = lasso_type(lassos[lasso]['data'], lassos[lasso]['bridges'],
                                                    smooth=s_value)
            log.info(str(lassos[lasso]['data']) + ' ' + str(lassos[lasso]['bridges'])  + ' ' + str(s_value)  + ' ' + str(lasso_data[lasso][s_value]))
    return lasso_data


def prepare_make_surfaces():
    return


''' Actual testing '''
# unfinished test - prepare_lasso_bridges function is unfinished
@pytest.mark.skip
def test_lasso_identify_bridges():
    log.info("Testing the bridges identification")
    lasso_data = prepare_lassos_bridges()
    for lasso in lassos.keys():
        assert lasso_data[lasso] == lassos[lasso]['bridges']
    return


# @pytest.mark.skip
def test_lasso_basic():
    log.info("Testing the lasso basic output")
    lasso_data = prepare_lassos_basic()
    for lasso in lassos.keys():
        assert lasso_data[lasso] == lassos[lasso]['basic']
    return


# @pytest.mark.skip
def test_lasso_detailed():
    log.info("Testing the lasso detailed output")
    lasso_data = prepare_lassos_detailed()
    #for lasso in ['curve2']: 
    for lasso in lassos.keys():
        for bridge in lassos[lasso]['bridges']:
            for key in lasso_data[lasso][tuple(bridge)].keys():
                if key in ['Area', 'Rg']:
                    diff = abs(lasso_data[lasso][tuple(bridge)][key] -
                               lassos[lasso]['detailed'][tuple(bridge)].get(key, 0))
                    higher = max(lasso_data[lasso][tuple(bridge)][key],
                               lassos[lasso]['detailed'][tuple(bridge)].get(key, 0))
                    #print("JESTEM:",lasso,bridge,key,diff,higher,100*diff/higher)
                    assert 100*diff/higher < epsilon
                else:
                    assert lasso_data[lasso][tuple(bridge)][key] == lassos[lasso]['detailed'][tuple(bridge)].get(key,'')
    return


# @pytest.mark.skip
def test_lasso_reduction():
    log.info("Testing the lasso output dependence on reduction")
    lasso_data = prepare_lassos_reduction()
    for lasso in lassos.keys():
        for reduction in reduction_pattern:
            assert lasso_data[lasso][reduction] == lassos[lasso]['reduction'][reduction]
    return


# @pytest.mark.skip
def test_lasso_surface_files():
    log.info("Testing the creation of the lasso surface files")
    lasso_data = prepare_lassos_surfaces()
    for lasso in lassos.keys():
        name = lassos[lasso]['data'].split('/')[-1]
        for bridge in lassos[lasso]['bridges']:
            for plot_type in surface_plot_formats.keys():
                #print("JESTEM test_lasso_surface_files, PLIKI TRZEBA POROWNYWAC INACZEJ, akceptujac jakies roznice...")

                assert diff_files(lasso_data[lasso][plot_type][tuple(bridge)],
                                  lassos[lasso]['surface'][plot_type][tuple(bridge)]) == set()
                os.remove(lasso_data[lasso][plot_type][tuple(bridge)])
            try:
                os.remove('_'.join(['tmp', name, str(bridge[0]), str(bridge[1]), 'VMD']) + '.pdb')
            except:
                pass
    return


# @pytest.mark.skip
def test_lasso_smoothing():
    log.info("Testing the lasso smoothing")
    lasso_data = prepare_lassos_smoothing()
    for lasso in lassos.keys():
        for s_value in smooth_parameters:
            assert lasso_data[lasso][s_value] == lassos[lasso]['smooth'][s_value]
    return

# unfinished test - prepare_make_surface is unfinished
@pytest.mark.skip
def test_make_surfaces():
    log.info("Testing the creation of the lasso surface files with make_surface")
    lasso_data = prepare_make_surfaces()
    for lasso in lassos.keys():
        for bridge in lassos[lasso]['bridges']:
            for surface_type in surface_plot_formats:
                assert diff_files(lasso_data[lasso][bridge][surface_type],
                                  lassos[lasso]['surface'][surface_type][bridge]) == set()
    return


if __name__ == '__main__':
    # test_lasso_identify_bridges()

    test_lasso_basic()
    test_lasso_detailed()
    test_lasso_reduction()
    test_lasso_surface_files()
    test_lasso_smoothing()
    # test_make_surfaces()
