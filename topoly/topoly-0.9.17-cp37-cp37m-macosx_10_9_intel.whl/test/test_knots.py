""" Testing various aspects of polynomials function.

Test by Bartosz Gren
Version from 17.02.2020
"""

import itertools
import os
import sys
import traceback
from topoly import alexander, conway, jones, homfly, yamada, kauffman_bracket
from topoly import kauffman_polynomial, blmho, aps, gln, writhe
from topoly.params import Closure, ReduceMethod, PlotFormat, Translate
import pytest

corr = 'test_knots_correct.txt'
fail = 'test_knots_failed.txt'
line = '='*100

invariant_l          = [alexander, conway, jones, homfly, yamada, kauffman_bracket,
                        kauffman_polynomial, blmho, aps, gln, writhe]
chain_l              = ['data/1j85.xyz', 'data/2efv.xyz', 'data/4wlr.xyz',
                       'data/3bjx.xyz', 'data/5zep.xyz', 'data/107l.xyz', 
                       'data/knot31.xyz','data/link31_0.xyz','data/unlink31_0.xyz']
closure_l            = [Closure.TWO_POINTS,  Closure.CLOSED, Closure.MASS_CENTER, 
                        Closure.ONE_POINT, Closure.RAYS, Closure.DIRECTION]
tries_l              = [1]
reduce_method_l      = [ReduceMethod.KMT, ReduceMethod.REIDEMEISTER, ReduceMethod.EASY]
poly_reduce_l        = [True, False]
translate_l          = [Translate.NO, Translate.YES]
beg_l                = [-1]
end_l                = [-1]
max_cross_l          = [4]
matrix_calc_cutoff_l = [0]
matrix_l             = [False, True]
matrix_density_l     = [1]
matrix_map_l         = [False, True]
map_filename_l       = ["KnotFingerPrintMap"] # other?
map_fileformat_l     = [PlotFormat.PNG, PlotFormat.SVG]


@pytest.mark.skip
def test_knots():
    try:
        os.remove(corr)
        os.remove(fail)
    except: pass
    with open(corr, 'w') as f:
        with open(fail, 'w') as ff:
            for invariant, chain, closure, tries, reduce_method,\
                poly_reduce, translate, beg, end, max_cross, matrix_calc_cutoff,\
                matrix, matrix_density, matrix_map, map_filename, map_fileformat\
                in itertools.product(invariant_l, chain_l, closure_l, tries_l,\
                      reduce_method_l, poly_reduce_l, translate_l, beg_l, end_l,\
                      max_cross_l, matrix_calc_cutoff_l, matrix_l, matrix_density_l,\
                      matrix_map_l, map_filename_l, map_fileformat_l):
                inv = str(invariant).split()[1].upper()
                to_write = str([inv, chain, closure, tries, reduce_method,\
                                poly_reduce, translate, beg, end, max_cross,\
                                matrix_calc_cutoff, matrix, matrix_density,\
                                matrix_map, map_filename, map_fileformat])[1:-1]
                print(to_write, end='\r')
                try:
                    res = invariant(chain, closure=closure, tries=tries, reduce_method=reduce_method,\
                            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,\
                            max_cross=max_cross, matrix_calc_cutoff=matrix_calc_cutoff,\
                            matrix=matrix, matrix_density=matrix_density, matrix_map=matrix_map,
                            map_filename=map_filename, map_fileformat=map_fileformat)
                    f.write('{}\n{}\n\n'.format(to_write,res))
                except Exception as err:
                    tb = traceback.format_exc()
                    ff.write('{}\n{}\n{}\n'.format(to_write,line,tb))

if __name__ == '__main__':
    test_knots()

