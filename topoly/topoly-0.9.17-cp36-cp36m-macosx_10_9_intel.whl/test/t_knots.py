import itertools
import os
import sys
import traceback
from topoly import alexander, conway, jones, homfly, yamada, kauffman_bracket
from topoly import kauffman_polynomial, blmho, aps, gln, writhe
from topoly.params import Closure, ReduceMethod, PlotFormat, OutputFormat, TopolyException

corr = 'test_knots_correct.txt'
fail = 'test_knots_failed.txt'
line = '='*100

invariant_l     = [alexander, conway, jones, homfly, yamada, kauffman_bracket,
                   kauffman_polynomial, blmho, writhe]#, gln, aps]
input_data_l    = ['data/1j85.xyz', 'data/2efv.xyz', 'data/107l.xyz',
                   'data/1j85.pdb', 'data/2efv.pdb', 'data/107l.pdb',
                   'data/4wlr.pdb', 'data/3bjx.pdb', 'data/5zep.cif', 
                   'data/knot31.xyz','data/link31_0.xyz','data/unlink31_0.xyz']
closure_l       = [Closure.TWO_POINTS,  Closure.CLOSED, Closure.MASS_CENTER, 
                   Closure.ONE_POINT, Closure.RAYS, Closure.DIRECTION]
tries_l         = [1]
direction_l     = [0]
reduce_method_l = [ReduceMethod.KMT]#, ReduceMethod.REIDEMEISTER, ReduceMethod.EASY]
poly_reduce_l   = [True]#, False]
translate_l     = [False]#, True]
boundaries_l    = [[]]#,[6,10]]
hide_trivial_l  = [True]#, False]
max_cross_l     = [15]
matrix_l        = [False]#, True]
density_l       = [1]
level_l         = [0]
matrix_plot_l   = [False]#, True]
plot_ofile_l    = ["KnotFingerPrintMap"] # other?
plot_format_l   = [PlotFormat.PNG]#, PlotFormat.SVG]
output_file_l   = ['']#, 'test']
output_format_l = [OutputFormat.Dictionary]#, OutputFormat.KnotProt]

def test_knots():
    try:
        os.remove(corr)
        os.remove(fail)
    except: pass
    with open(corr, 'w') as f:
        with open(fail, 'w') as ff:
            for invariant, input_data, closure, tries, direction, reduce_method,\
                poly_reduce, translate, boundaries, hide_trivial, max_cross, matrix,\
                density, level, matrix_plot, plot_ofile, plot_format, output_file,\
                output_format \
                in itertools.product(invariant_l, input_data_l, closure_l, tries_l,\
                        direction_l, reduce_method_l, poly_reduce_l, translate_l,\
                        boundaries_l, hide_trivial_l, max_cross_l, matrix_l, density_l,\
                        level_l, matrix_plot_l, plot_ofile_l, plot_format_l, output_file_l,\
                        output_format_l):
                inv = str(invariant).split()[1].upper()
                to_write = str([
                        inv, input_data, closure, tries, direction, reduce_method,\
                        poly_reduce, translate, boundaries, hide_trivial, max_cross, matrix,\
                        density, level, matrix_plot, plot_ofile, plot_format, output_file,\
                        output_format])[1:-1]
                print(to_write, end='\r')
                try:
                    if inv == 'WRITHE': # bo writhe nie przyjmuje output_format
                        res = invariant(
                            input_data, closure=closure, tries=tries,\
                            direction=direction, reduce_method=reduce_method,\
                            poly_reduce=poly_reduce, translate=translate,\
                            boundaries=boundaries, hide_trivial=hide_trivial,\
                            max_cross=max_cross, matrix=matrix, density=density,\
                            level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,\
                            plot_format=plot_format, output_file=output_file)
                    else:
                        res = invariant(
                            input_data, closure=closure, tries=tries,\
                            direction=direction, reduce_method=reduce_method,\
                            poly_reduce=poly_reduce, translate=translate,\
                            boundaries=boundaries, hide_trivial=hide_trivial,\
                            max_cross=max_cross, matrix=matrix, density=density,\
                            level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,\
                            plot_format=plot_format, output_file=output_file,\
                            output_format=output_format)
                    f.write('{}\n{}\n\n'.format(to_write,res))
                except TopolyException:
                    f.write('{}\nTopolyException\n\n'.format(to_write))
                except Exception as err:
                    tb = traceback.format_exc()
                    ff.write('{}\n{}\n{}\n'.format(to_write,line,tb))

if __name__ == '__main__':
    test_knots()
