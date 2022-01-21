"""
default and example parameters
this is also data structure to intermediate between gui and
marlowe control data
"""

from .. import scon

from .. import axis
from .. import vpar

version = 0

# 7.1.2
modl_original = {
    'file': [None] * 5,  # (None|String)*5
    # 'rdnml':[False]*6, # (T|F)*6
    'metric': 1,  # (1|2)
    'tram': True,  # (T|F)
    # 'surfce':0, # (0|1|2|3|[6...]) almost similar to Int
    # 'klay':1, # (..|-1|0|1|..<scon.NLAY)
    #   this is derived from len(xtal.layer)
    'nm': 4,  # [0, scon.MEHL]
    'lorg': 2,  # (0|...|8)
    'ichan': [100, 100, 10, 5],  # [Int]*4
    'delta': [2e-6, 0.01, 1e-3, 0.999350],  # [Double]*4
    # 'tim':[True]*7 # [(T|F)]*7
}

modl_default = {
    'file': [None] * 5,  # (None|String)*5
    # 'rdnml':[False]*6, # (T|F)*6
    'metric': 1,  # (1|2)
    'tram': True,  # (T|F)
    # 'surfce':0, # (0|1|2|3|[6...]) almost similar to Int
    # 'klay':1, # (..|-1|0|1|..<scon.NLAY)
    #   this is derived from len(xtal.layer)
    'nm': 4,  # [0, scon.MEHL]
    'lorg': 2,  # (0|...|8)
    'ichan': [100, 100, 10, 5],  # [Int]*4
    'delta': [2e-6, 0.01, 1e-3, 0.999350],  # [Double]*4
    # 'tim':[True]*7 # [(T|F)]*7
}

modl_example = {
    'file': ['aaa', 'bbb', None, 'ddd'],  # (None|String)*5
    # 'rdnml':[True]*6, # (T|F)*6
    'metric': 2,  # (1|2)
    'tram': False,  # (T|F)
    # 'surfce':3, # (0|1|2|3|[6...]) almost similar to Int
    # 'klay':4, # (..|-1|0|1|..<scon.NLAY)
    'nm': 3,  # [0, scon.MEHL]
    'lorg': 4,  # (0|...|8)
    'ichan': [1000, 1000, 100, 50],  # [Int]*4
    'delta': [2e-5, 0.001, 1e-4, 0.0999350],  # [Double]*4
    # 'tim':[False]*7 # [(T|F)]*7
}

# &ATOM record
atom_elem_default = {'type': 'H', 'z': 1, 'w': 1.004, 'equit': 4.5, 'inel': 4}
atom_tbl_default = []

atom_default = {
    # no atom data
    'atomtbl': atom_tbl_default,
    'lox': 0,
    # 'ebnd': [0.0, 0.0, 0.0], moved to site_elem
    # 'lock': moved to site_elem
    # 'dist': should be moved to site_elem
    'lbnd': 3
    # 'dbnd': ???
}

atom_elem_example = {'type': 'C', 'z': 6.0, 'w': 12.0, 'equit': 4.5, 'inel': 4}
atom_tbl_example = [
    {'type': 'H', 'z': 1, 'w': 1.004, 'equit': 3.1, 'inel': 1},
    {'type': 'C', 'z': 6.0, 'w': 12.0, 'equit': 4.5, 'inel': 4}]


atom_example = {
    'atomtbl': atom_tbl_example,
    'lox': 1,
    # 'ebnd': [0.1, 5.0, 0.0], moved to site_elem
    'lbnd': 0
}

# &SURF
surf_default = {
    'surfce': 0,
    'lyme': 1,
    'sides': [1.0, 1.0, 1.0],
    'rsrf': [-0.5, -0.5, -0.5],
    'edge': [100, 100]}

surf_example = {
    'surfce': 3,
    'lyme': 2,
    'sides': [2.0, 3.0],
    'rsrf': [-0.5, 0.3],
    'edge': [200, 300]}

# XTAL.rz and atom.lock, order
site_elem_default = {
    'rz': [0, 0, 0],
    'lock': 1,
    'ebnd': [0.0, 0.0, 0.0]
}

# XTAL.rz and atom.lock, order
site_elem_example = {
    'rz': [0.25, 0.25, 0.25],
    'lock': -1,
    'order': [0.5, 0.25, 0, 0, 0, 0.25],
    'ebnd': [0.1, 5.0, 0.0]
}

layer_surfopt_default = {
    'depth': 1e10,
    'origin': [0.0, 0.0, 0.0],
    'lo': 1
}

layer_surfopt_example = {
    'depth': 100,
    'origin': [1.0, 2.0, 3.0],
    'lo': 2
}

xtal_layer_elem_default = {
    'alat': [0, 0, 0, 90, 90, 90],
    'centre': 1,
    'dmax': 1.0,
    'poly': 0,
    'axis': axis.param_default,
    'site': [],
}

xtal_layer_elem_example = {
    'alat': [2.0, 3, 5, 90, 90, 90],
    'centre': 6,
    'dmax': 0.75,
    'poly': 1,
    'site': [
        {'rz': [0, 0, 0], 'lock':1, 'ebnd': [0.1, 5.0, 0.0]},
        {'rz': [0.25, 0.25, 0.25], 'lock':-1,
         'order':[0, 0.75, 0, 0, 0, 0.25],
         'ebnd': [4.0, 0, 4.0]}],
    'surfopt': layer_surfopt_example
}

xtal_layer_default = []

xtal_layer_example = [
    {'alat': [3.6150, 3.6150, 3.6150, 90, 90, 90],
     'centre':6, 'dmax':1.0, 'poly':0,
     'site':[
        {'rz': [0, 0, 0], 'lock':1},
        {'rz': [0.25, 0.25, 0.25], 'lock':-1,
         'order':[0, 0.75, 0, 0, 0, 0.25]}],
     'surfopt': layer_surfopt_example}]

# &XTAL
xtal_default = {
    'quit': False,
    'news': 1,
    'unit': 1,
    'base': 1.0,
    'layer': xtal_layer_default
}

xtal_example = {
    'quit': True,
    'news': 2,
    'unit': -1,
    'base': 3.0,
    'layer': xtal_layer_example
}

# &SIZE
size_body_default = {
    'rb': [0.5, 1.0],
    'xilim': [0.025, 0.0, 0.025, scon.root],
    # xilim(1) and (3) are operated in nm unit.
    # But they are translated in BASE unit
    # for marlowe input data.
    'slice': 0.0,
    'step': scon.sent,
    'lifo': True
}

size_body_example = {
    'rb': [0.75, 0.75],
    'xilim': [0.1, 0.01, 0.1, 0.001],
    'slice': 1.0,
    'step': 0.5,
    'lifo': False
}

size_default = None

size_example = size_body_example

# outp
outp_inform_original = [False] * 8
outp_inform_default = [True] * 6 + [False] * 2
outp_inform_example = [True, False, True, True, False, False, False, False]

outp_original = {
    'drng': [0.25, 0.25, 2.5],
    'lcs': [3, scon.llcs],
    'trace': [0, 0, 0],
    'look': 0,
    'grex': False,
    'inform': outp_inform_original
}

outp_default = {
    'drng': [0.25, 0.25, 2.5],
    'lcs': [3, scon.llcs],
    'trace': [0, 0, 0],
    'look': 4,
    'grex': False,
    'inform': outp_inform_default
}

outp_example = {
    'drng': [0.1, 0.05, 0.01],
    'lcs': [0, 10],
    'trace': [5, 2, 1],
    'look': 2,
    'grex': True,
    'inform': outp_inform_example
}

proj_elem_default = {
    'ranx': [0] * scon.nrnx,
    'maxrun': 0,
    'prim': 0,
    'new': 0,
    'ekip': 0,
    'leap': 0,
    'trmp': True,
    'raip': [0, 0, 0],
    'laip': 1,
    'refip': [0, 0, 0],
    'lrip': 1,
    'miller': True,
    'beam': [0, 0, 1.0],
    'tha': 0.0,
    'phi': 0.0,
    'dvrg': 0.0
}

proj_elem_example = {
    'ranx': list(range(scon.nrnx)),
    'maxrun': 100,
    'prim': 1,
    'new': 1,
    'ekip': 1000.0,
    'leap': 25,
    'trmp': False,
    'raip': [1.0, 2.0, 3.0],
    'laip': 2,
    'refip': [4.0, 5.0, 6.0],
    'lrip': 3,
    'miller': False,
    'beam': [1, 2, 3],
    'tha': 7,
    'phi': 30,
    'dvrg': 0.05
}

proj_default = []

proj_example = [proj_elem_example, proj_elem_default]

# root
root_default = {
    # comments
    'comment1': '',
    'comment2': '',
    # records
    'modl': modl_default,
    'xtal': xtal_default,
    'atom': atom_default,
    'surf': surf_default,
    'size': size_default,
    'outp': outp_default,
    'proj': proj_default,
    'vpar': vpar.param_default
}

root_example = {
    # comments
    'comment1': 'This is example ',
    'comment2': '  second line comment',
    # records
    'modl': modl_example,
    'xtal': xtal_example,
    'atom': atom_example,
    'surf': surf_example,
    'size': size_example,
    'outp': outp_example,
    'proj': proj_example,
    'vpar': vpar.param_example
}

default = root_default
example = root_example


def solve_version(d):
    """This is bottom of update chain, so return d as it is
    """
    return d
