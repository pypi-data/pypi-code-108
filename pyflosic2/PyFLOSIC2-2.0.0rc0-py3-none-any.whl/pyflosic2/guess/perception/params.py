import numpy 
from pyflosic2.atoms.atoms import symbol2number

""" These functions are used from different routines. 
    The module name is not optimal and may renamed, i.e,
       common
       moved to utils
"""

# Max coordination 
# ----------------
# Correspond/ respect UFF MMTypes
missing = 1
max_coordination = numpy.array([
    0, # X
    1,
    4,
    1,
    4,
    4,
    4,
    3, #4,
    2,
    1,
    4,
    1,
    4,
    4,
    4,
    4,
    4,
    1,
    4,
    1,
    6,
    4,
    6,
    4,
    6,
    6,
    6,
    6,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    1,
    4,
    1,
    6,
    4,
    4,
    4,
    6,
    6,
    6,
    6,
    4,
    2,
    4,
    4,
    4,
    4,  # used the same value as for Sn
    4,
    1,
    4,
    1,
    6,
    4,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,# https://www.webelements.com/tungsten/atom_sizes.html
    3,# https://www.webelements.com/platinum/atom_sizes.html
    2,# https://www.webelements.com/gold/atom_sizes.html
    1 # https://www.webelements.com/mercury/atom_sizes.html
    ])

def get_max_valence(symbol,co):
    """
        Get maximal valence (ve)
        ------------------------
        Is defined/limited by the available UFF MMTypes.

        Adjustments:
            - N, O fixes lone electrons/ pairs
              but breaks sp
    """
    if symbol == 'H':
        if co == 2:
            ve = 2
        else:
            ve = 1
    if symbol == 'C':
        ve = 4
    if symbol == 'N':
        # KT: adjusted for NH3
        ve = 5 # orig: 4 KT: 5
    if symbol == 'O':
        # SS: added this for Conformer3D_CID_7861
        #     O_3 double bound - sp2 ?
        #ve = 3
        #if co == 2:
        #    ve = 3
        #### KT: adjusted for COH2
        #else:
        #    ve = 6 # orig: 3
        ve = 6
    if symbol == 'Si':
        ve = 4
    if symbol == 'P':
        if co > 3:
            ve = 4
        else:
            ve = 5
    if symbol == 'S':
        if co == 2:
            ve = 4
        else:
            ve = 6
    return ve


# atomic penalty score (aps) 
# --------------------------
# atom_symbol : ftype : va : value 
# 
# Reference:
# - [1] Automatic Molecular Structure Perception for the Universal Force Field
#       Table. 1

nodef = numpy.nan
aps_bo = {'C' : {
                 'default' : {1: 128,
                              2:  64,
                              3:  32,
                              4 :  0,
                              5 : nodef,
                              6 : nodef},
                 'COO'     : {1 : nodef,
                              2 : nodef,
                              3 : 64,
                              4 : 0,
                              5 : nodef,
                              6 : nodef}
                 },
         'Si' : {
                'default' : {1: 8,
                             2: 4,
                             3: 2,
                             4: 0,
                             5: nodef,
                             6: nodef}
                },
         'N' : {
                1         : {1: 64,
                             2:  2,
                             3:  0,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  4,
                             3:  0,
                             4 : 2,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  0,
                             4 : 1,
                             5 : nodef,
                             6 : nodef},
                4         : {1:  nodef,
                             2:  nodef,
                             3:  nodef,
                             4 : 0,
                             5 : nodef,
                             6 : nodef},
                'NOO'     : {1:  nodef,
                             2:  nodef,
                             3:  64,
                             4 : 0,
                             5 : nodef,
                             6 : nodef},
               },
         'O' : {
                1         : {1:  2,
                             2:  0,
                             3:  16,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  0,
                             3:  16,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  0,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef}},
         'P' : {
                1         : {1: 64,
                             2:  2,
                             3:  0,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  4,
                             3:  0,
                             4 : 2,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  0,
                             4 : 1,
                             5 : 2,
                             6 : nodef},
                4         : {1:  nodef,
                             2:  nodef,
                             3:  nodef,
                             4 : 1,
                             5 : 0,
                             6 : nodef}},
         'S' : {
                1         : {1:  2,
                             2:  0,
                             3:  64,
                             4 : nodef,
                             5 : nodef,
                             6 : nodef},
                2         : {1:  nodef,
                             2:  0,
                             3:  32,
                             4 : 1,
                             5 : nodef,
                             6 : nodef},
                3         : {1:  nodef,
                             2:  nodef,
                             3:  1,
                             4 : 0,
                             5 : 2,
                             6 : 2},
                4         : {1:  nodef,
                             2:  nodef,
                             3:  nodef,
                             4 : 4,
                             5 : 2,
                             6 : 0}}
         }

def eval_bond_order(atoms,nn,bo,verbose=3):
    """
        Evalutate bond order
        --------------------
        Calculate total penalty score (tps).
        The optimum is tps = 0.0.

    """
    co = numpy.zeros(len(atoms))
    va = numpy.zeros(len(atoms))
    va_max = numpy.zeros(len(atoms))
    nn_opt = numpy.zeros(len(atoms))
    ftype = numpy.zeros(len(atoms),dtype=object)
    tps = numpy.zeros(len(atoms))
    for i in range(len(atoms)):
        co[i] = len(nn[i].nonzero()[0])
        va[i] = bo[i, :].sum()
        va_max[i] = max_coordination[symbol2number[atoms[i].symbol]]
        nn_atoms = nn[i].nonzero()[0].tolist()
        sym_i = atoms[i].symbol
        symbols_j = atoms[nn_atoms].symbols
        values, counts = numpy.unique(symbols_j,return_counts=True)
        if sym_i == 'C':
            for s,c in zip(values,counts):
                # len(symbols_j) to not eval CO2 molecule
                if len(symbols_j) > 2 and s == 'O' and c == 2:
                    typ = 'COO'
                else:
                    typ = 'default'
        if sym_i == 'N':
            for s,c in zip(values,counts):
                # len(symbols_j) to not eval NO2 molecule
                if len(symbols_j) > 2 and s == 'O' and c == 2:
                    typ = 'NOO'
                else:
                    typ = co[i]

        if sym_i in ['C','N','Si']:
            ftype[i] = typ
            try:
                aps = aps_bo[sym_i][typ][va[i]]
            except:
                aps = nodef
            tps[i] = aps
    if verbose > 3:
        print(f'total pentalty score (tps) : {tps.sum()}')
    return tps.sum()
