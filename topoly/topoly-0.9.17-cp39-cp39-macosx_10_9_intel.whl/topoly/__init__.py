#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
The main Topoly module collecting the functions designed for the users.

Pawel Dabrowski-Tumanski
p.dabrowski at cent.uw.edu.pl
04.09.2019

Wanda Niemyska, Bartosz Greń
w.niemyska, b.gren at cent.uw.edu.pl
14.03.2021

Documentation generated with Sphinx: www.sphinx-doc.org

Support in PyCharm:
https://www.jetbrains.com/help/pycharm/settings-tools-python-integrated-tools.html
- change default reStructuredText to Google

Docs will be published in: https://readthedocs.org/
"""

from .manipulation import *
from .invariants import *
from .topoly_knot import *
from .topoly_preprocess import *
from .codes import *
from .plotting import KnotMap, Reader
from .params import Translate, Closure, ReduceMethod, SurfacePlotFormat, TopolyException,\
                    PlotFormat, OutputFormat, PrecisionSurface, DensitySurface, Bridges,\
                    OutputType, Colors, test
from .polygongen import *
from .lasso import Lasso
from .convert import convert_xyz2vmd
from .knotcon import create, export


def alexander(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
              reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
              external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
              pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
              matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
              map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
              map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
              bridges=[], breaks=[], debug=False):
    """
    Calculates the Alexander polynomial of the given structure.

    Args:
        chain (str/list):
                The structure to calculate the polynomial
                for, given in abstract code, coordinates, or the path to
                the file containing the data.
        closure (str, optional):
                The method to close the chain. Viable options are the
                parameters of the Closure class (in topoly.params).
                Default: Closure.TWO_POINTS.
        tries (int, optional):
                The number of tries for stochastic closure methods.
                Default: 200.
        chain_boundary (list of [int, int], optional):
                The boundaries of the subchains to be checked. The
                subchains are specified as a list of subchain beginning
                and ending index. If empty, the whole chain is
                calculated. Default: None.
        reduce_method (str, optional):
                The method of chain reduction. Viable options are the
                parameters of the ReduceMethod class.
                Default: ReduceMethod.KMT.
        max_cross (int, optional):
                The maximal number of crossings after reduction to start
                the polynomial calculation. Default: 15.
        poly_reduce (bool, optional):
                If the polynomial should be presented in the reduced
                form. Default: False.
        translate (bool/str, optional):
                If translate the polynomial to the structure topology
                using the dictionary. Default: Translate.PIU -- translate
                if known topology, print polynomal value if unknown topology.
        external_dictionary (str, optional):
                The path to the file with the external dictionary of the
                polynomials. Default: ''.
        hide_trivial (bool, optional):
                If to suppress printing out the trivial results.
                Default: True.
        chiral (bool, optional):
                If the chirality should be taken into account.
                By default False.
        matrix_calc_cutoff (float, optional):
                Used with matrix_density parameter. The cutoff of the 
                non-trivial structure probability of specific subchain
                to check the topology of all neigbouring subchains.
                Default: 0.
        pdb_chain (string, optional):
                If inputting .pdb file, which chain should be used.
                If none, the first chain is taken into account.
                Default: None.
        pdb_model (string, optional):
                If inputting .pdb file, which model should be used.
                If none, the first model is taken into account.
                Default: None.
        pdb_bridges (string, optional):
                Useful only for topoly.yamada_ and topoly.aps_ and
                when inputting .pdb file.
                Determines which bridges should be used during topoly
                analysis:
                'ssbond' -- disulfide bonds,
                'ion'  -- ionic bridges,
                'covalent' -- other covalent (non-disulfide) bridges,
                'all' -- covalent (disulfide and non-disulfide) and 
                ionic bridges. Default: None.
        matrix (bool, optional):
                if to calculate the whole matrix i.e. the polynomial for
                each subchain. Default: False.
        matrix_density (int, optional):
                the inverse of resolution of matrix calculation. Higher
                number speeds up calculation, but may result in omitting
                some non-trivial subchains. Default: 1.
        matrix_filename (str, optional):
                The name of the file with the matrix results. If empty,
                the resulting matrix is returned to source. Default: ''.
        matrix_format (str, optional):
                The format of the matrix output. The viable formats are
                the parameters of the OutputFormat class.
                Default: OutputFormat.DICTIONARY.
        matrix_map (bool, optional):
                If to plot a figure of a matrix (knot fingerprint).
                Default: False.
        map_cutoff (float, optional):
                If knot probability is lover than map_cutoff, then
                is is not plotted. Default: 0.48.
        map_palette (dict, optional):
                Dictionary of knots (string keys) and their colors
                (string values) used in matrix plotting.
        map_arrows (bool, optional):
                Plot arrows directing knot core and knot tails.
                Default: True.
        map_filename (str, optional):
                The name of the matrix figure plot.
                Default: KnotFingerPrintMap.
        map_fileformat (str, optional):
                The format of the matrix figure plot. Viable formats are
                the parameters of the PlotFormat class.
                Default: PlotFormat.PNG.
        cuda (bool, optional):
                If to use the cuda-provided acceleration if possible.
                Default: True.
        run_parallel (bool, optional):
                If to use the Python-provided parallelization of
                calculation. Default: True.
        parallel_workers (int, optional):
                Number of parallel workers. If 0, all the available
                processors will be used. Default: 0.
        bridges (list, optional):
                The list of tuples denoting the bridging residues in
                the main chain. Default: [].
        breaks (list, optional):
                The list of breaks of the main chain. Default: [].
        debug (bool, optional):
                The debug mode. Default: False.

    Returns:
        If in closure parameter deterministic method is passed
        (Closure.CLOSED, Closure.MASS_CENTER, Closure.DIRECTION) then 
        topology type (string) is returned.
        If in closure parameter stochastic method is passed
        (Closure.ONE_POINT, Closure.TWO_POINTS, Closure.RAYS)
        then dictionary of topology types as keys and their 
        probabilities as key are returned.
        If matrix=True, then dictionary of subchain indices as keys and
        output adequate to closure as value is returned.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                AlexanderGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def jones(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
          reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
          external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
          pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
          matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
          map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
          map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
          bridges=[], breaks=[], debug=False):
    """
    Calculates the Jones polynomial of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                JonesGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def conway(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
           reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
           external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
           pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
           matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
           map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
           map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
           bridges=[], breaks=[], debug=False):
    """
    Calculates the Conway polynomial of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                ConwayGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def homfly(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
           reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
           external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
           pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
           matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
           map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
           map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
           bridges=[], breaks=[], debug=False):
    """
    Calculates the HOMFLY-PT polynomial of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                HomflyGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def yamada(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
           reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
           external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
           pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
           matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
           map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
           map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
           bridges=[], breaks=[], debug=False):
    """
    Calculates the Yamada polynomial of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                YamadaGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def kauffman_bracket(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
                reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
                external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
                pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1,
                matrix_filename='', matrix_format=OutputFormat.Dictionary, matrix_map=False,
                map_cutoff=0.48, map_palette=Colors.Knots, map_arrows=True,
                map_filename="KnotFingerprint", map_fileformat=PlotFormat.PNG, cuda=True,
                run_parallel=True, parallel_workers=None, bridges=[], breaks=[], debug=False):
    """
    Calculates the Kauffman bracket of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                KauffmanBracketGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def kauffman_polynomial(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
                reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
                external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
                pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1,
                matrix_filename='', matrix_format=OutputFormat.Dictionary, matrix_map=False,
                map_cutoff=0.48, map_palette=Colors.Knots, map_arrows=True,
                map_filename="KnotFingerprint", map_fileformat=PlotFormat.PNG, cuda=True,
                run_parallel=True, parallel_workers=None, bridges=[], breaks=[], debug=False):
    """
    Calculates the Kauffman two-variable polynomial of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                KauffmanPolynomialGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def blmho(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
          reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
          external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
          pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
          matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
          map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
          map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
          bridges=[], breaks=[], debug=False):
    """
    Calculates the BLM/Ho polynomial of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                BlmhoGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def aps(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
        reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
        external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
        pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
        matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
        map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
        map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
        bridges=[], breaks=[], debug=False):
    """
    Calculates the APS bracket of the given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        Return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                ApsGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def writhe(chain, closure=Closure.TWO_POINTS, tries=200, chain_boundary=None,
           reduce_method=ReduceMethod.KMT, max_cross=15, poly_reduce=True, translate=Translate.PIU,
           external_dictionary='', hide_trivial=True, chiral=False, matrix_calc_cutoff=0, pdb_chain=None,
           pdb_model=None, pdb_bridges=None, matrix=False, matrix_density=1, matrix_filename='',
           matrix_format=OutputFormat.Dictionary, matrix_map=False, map_cutoff=0.48,
           map_palette=Colors.Knots, map_arrows=True, map_filename="KnotFingerprint",
           map_fileformat=PlotFormat.PNG, cuda=True, run_parallel=True, parallel_workers=None,
           bridges=[], breaks=[], debug=False):
    """"
    Calculates writhe of a given structure.

    Parameters are the same as in topoly.alexander_.

    Returns:
        return behavior is analogical as in topoly.alexander_ return.
    """
    result = Invariant(chain, chain=pdb_chain, model=pdb_model, bridges=bridges, bridges_type=pdb_bridges,
                       breaks=breaks)
    return result.calculate(
                WritheGraph, closure=closure, tries=tries, boundaries=chain_boundary,
                reduce_method=reduce_method, max_cross=max_cross, poly_reduce=poly_reduce,
                translate=translate, external_dictionary=external_dictionary,
                hide_trivial=hide_trivial, chiral=chiral, level=matrix_calc_cutoff, matrix=matrix,
                density=matrix_density, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, matrix_cutoff=map_cutoff, palette=map_palette,
                arrows=map_arrows, plot_ofile=map_filename, plot_format=map_fileformat, cuda=cuda,
                run_parallel=run_parallel, parallel_workers=parallel_workers, debug=debug)


def gln(chain1, chain2=None, chain1_boundary=(-1, -1), chain2_boundary=(-1, -1),
        avgGLN=False, avg_tries=200, maxGLN=False, max_density=-1, matrix=False,
        matrix_filename='', matrix_format=OutputFormat.Matrix, matrix_map=False,
        map_filename="GLN_map", map_fileformat=PlotFormat.PNG, pdb_chain1=None, pdb_model1=None,
        pdb_chain2=None, pdb_model2=None, bridges_chain1=[], bridges_chain2=[],
        breaks_chain1=[], breaks_chain2=[], precision_output=3, debug=False):
    """
    Calculates Gauss linking number between two chains.

    Args:
        chain1 (str/list):
                The structure containing two chains that may be linked
                -- or one chain and second one is given in another
                argument, chain2 -- given in coordinates, or the
                path to the file containing the data.
        chain2 (str/list, optional):
                The structure containing the second chain, given in
                coordinates, or the path to the file containing the
                data. If not given, both chains are expected to be
                present in the structure. Default: None
        chain1_boundary ([int, int], optional):
                The indices of chain1 within the structure. If [-1, -1]
                the whole structure is used as chain1.
                Default: [-1, -1]
        chain2_boundary ([int, int], optional):
                The indices delimiting chain2. If [-1, -1], the whole
                structure is treated as chain2. Note, that if the
                chain2 is not specified separately, boundaries must
                be given for both chains (as both of them are taken then
                from structure and they cannot overlap).
                Default: [-1, -1]
        avgGLN (bool, optional):
                Average GLN value after number of random closures of both 
                chains is calculated (and given in returned dictionary 
                with key 'avg'). Default: False
        avg_tries (int, optional):
                (If argument avgGLN is set to True)
                the number of closures performed in calculating 
                the average GLN value. Default: 200
        maxGLN (bool, optional):
                Maximal absolute GLN values between one chain and all
                fragments of second chain are calculated and given 
                in returned dictionary with keys 'subchain of chain 1'
                and 'subchain of chain 2'; possibly maximal GLN value
                between all fragments of two chains is calculated as well
                (argument max_density). Default: False
        max_density (int, optional):
                (If argument maxGLN is set to True) if max_density (d)=1,
                all pairs of fragments are analyzed; if d>1 then
                only fragments of length being a multiplication of d are
                analyzed. For longer chains d=1 is highly unrecommended
                due to high time and space complexity of computations
                (O(N^4/d^4)). If -1, local maximum is not calculated.
                Default: -1
        matrix (bool, optional):
                Whole GLN matrix between chain1 and all subchains of chain2
                is calculated and given in returned dictionary with key
                'matrix'; additionally one can choose format of output matrix
                (argument matrix_format), matrix can be written into 
                the file (argument matrix_filename) or plotted (arguments 
                map, map_fileformat and map_filename). 
                Default: False
        matrix_filename (str, optional):
                If not empty, it indicates the name of the file to save 
                the matrix calculation results. Default: ''
        matrix_format (str, optional):
                The format of the matrix output data. Viable formats 
                are the parameters of the OutputFormat class.
                Default: OutputFormat.Matrix
        matrix_map (bool, optional):
                If the plot of GLN matrix should be prepared. Default: False
        map_filename (str, optional):
                The name of the file containing the matrix plot. 
                Default: 'GLN_map'
        map_fileformat (str, optional):
                The format of the plot with the matrix of GLN. Viable
                formats are parameters of the PlotFormat class.
                Default: PlotFormat.DONTPLOT
        pdb_chain1 (str, optional):
                Name of chain one wants to choose from PDB file
                (important if "chain1" is a PDB file, where might be
                lots of different chains) to construct chain1. If None,
                first chain in PDB file is chosen. Default: None
        pdb_model1 (str, optional):
                Name of model one wants to choose from PDB file
                (important if "chain1" is a PDB file, where might be
                lots of different models) to construct chain1. If None,
                first model in PDB file is chosen. Default: None
        pdb_chain2 (str, optional):
                Name of chain one wants to choose from PDB file
                (important if "chain1"/"chain2" is a PDB file,
                where might be lots of different chains) to construct
                chain2. If None, first chain in PDB file is chosen.
                Default: None
        pdb_model2 (str, optional):
                Name of model one wants to choose from PDB file
                (important if "chain1"/"chain2" is a PDB file,
                where might be lots of different models) to construct
                chain2. If None, first model in PDB file is chosen.
                Default: None
        bridges_chain1 (list, optional):
                The list of tuples denoting the bridging residues in
                the chain1. Default: [].
        bridges_chain2 (list, optional):
                The list of tuples denoting the bridging residues in
                the chain2. Default: [].
        breaks_chain1 (list, optional):
                The list of breaks of the chain1. Default: [].
        breaks_chain2 (list, optional):
                The list of breaks of the chain2. Default: [].
        precision_output (int, optional):
                Precision of output, number of decimal places in
                returned values. Default: 3
        debug (bool, optional):
                The debug mode. Default: False

    Returns:
        The value of the Gaussian Linking Number calculated between two
        chains (which may be called loop and tail), specified either in
        separate files, or by the indices (tail_boundary). 
        If at least one of arguments avgGLN, maxGLN or matrix is set to
        True, then instead of just one number - the dictionary is returned
        (the key 'whole chains' keeps GLN between two whole chains, 
        other keys might keep information about the maximal absolute GLN
        between two chains, the average GLN value after number of random 
        closures of both chains, as well as whole matrix of GLN between 
        one chain (the loop) and each subchain of second chain (tail).
    """
    result = GlnGraph(chain1, chain=pdb_chain1, model=pdb_model1, bridges=bridges_chain1, breaks=breaks_chain1)
    return result.calculate(
                chain2=chain2, boundary=chain1_boundary, boundary2=chain2_boundary,
                avgGLN=avgGLN, avg_tries=avg_tries, maxGLN=maxGLN, max_density=max_density,
                matrix=matrix, output_file=matrix_filename, output_format=matrix_format,
                matrix_plot=matrix_map, plot_ofile=map_filename, matrix_plot_format=map_fileformat,
                chain2_id=pdb_chain2, model2=pdb_model2, precision=precision_output,
                bridges_chain2=bridges_chain2, breaks_chain2=breaks_chain2, debug=debug)


def getpoly(invariant, topolname, value=None):
    """
    Generates list of objects which have polynomial value corresponding
    to given invariant type and topolname. These objects can be
    multiplied (*) to find polynomial of joined structures and added (+)
    to find polynomial of unjoined union.

    Args:
        invariant (str):
                Name of invariant (or its abbreviation):
                'Alexander' ('a'), 'Conway' ('c'), 'Jones' ('j'),
                'HOMFLYPT' ('h'), 'Yamada' ('y'), 'BLMHo' ('b'),
                'Kauffman bracket' ('kb'), 'Kauffman polynomial' ('kp'),
        topolname (str):
                Topology name i.e. "3_1", "-5_1", "t3_1"
        value(str, optional):
                Polynomial of given topolname structure. If nothing is
                given searches for linkname value in polvalues.py.
                Default: None.

    Returns:
        List of Polynomial objects.
    """
    return create(invariant, topolname, value)


def exportpoly(polynomials, exportfile='new_polvalues.py'):
    """
    Sends list of Polynomial objects generated by getpoly to chosen
    exportfile, that can be used as an alternative dictionary.

    Args:
        polynomials (list of Poly objects):
                List of objects generated by getpoly.
        exportfile (str, optional):
                Name of file where polynomial records will be written.
                Default: 'new_polvalues.py'.

    """
    return export(polynomials, exportfile)


def make_surface(structure, loop_indices=None, precision=PrecisionSurface.HIGH,
            density=DensitySurface.MEDIUM, precision_output=3, pdb_chain=None, pdb_model=None,
            pdb_bridges=Bridges.SSBOND, bridges=[], breaks=[]):
    """
    Calculates minimal surface spanned on a given loop.

    Args:
        structure (str/list):
                The structure containing loop to calculate the surface
                spanned on, given in coordinates, or the path to the
                file containing the data.
        loop_indices (list, optional):
                The indices of loop within the structure. If they are
                not specified the whole structure is used as loop.
                Default: None.
        precision (int, optional):
                Precision of computations of minimal surface. Viable
                options are the parameters of the PrecisionSurface
                class. Default: PrecisionSurface.HIGH.
        density (int, optional):
                Density of the triangulation of minimal surface. Viable
                options are the parameters of the DensitySurface class.
                Default: DensitySurface.MEDIUM.
        precision_output (int, optional):
                Precision of output, number of decimal places in
                returned values. Default: 3
        pdb_chain (string, optional):
                If inputting .pdb file, which chain should be used.
                If none, the first chain is taken into account.
                Default: None.
        pdb_model (string, optional):
                If inputting .pdb file, which model should be used.
                If none, the first model is taken into account.
                Default: None.
        pdb_bridges (string, optional):
                Useful only for topoly.yamada_ and topoly.aps_ and
                when inputting .pdb file.
                Determines which bridges should be used during topoly
                analysis:
                'ssbond' -- disulfide bonds,
                'ion'  -- ionic bridges,
                'covalent' -- other covalent (non-disulfide) bridges,
                'all' -- covalent (disulfide and non-disulfide) and 
                ionic bridges. Default: 'ssbond'.
        bridges (list, optional):
                The list of tuples denoting the bridging residues in
                the main chain. Default: [].
        breaks (list, optional):
                The list of breaks of the main chain. Default: [].
    Returns:
        List of triangles that form minimal surface.
    """
    obj = Lasso(structure, loop_indices, chain=pdb_chain, model=pdb_model, bridges_type=pdb_bridges, bridges=bridges,
                breaks=breaks)
    return obj.make_surface(precision, density, precision_output)


def lasso_type(structure, loop_indices=None, smooth=0, precision=PrecisionSurface.HIGH,
               density=DensitySurface.MEDIUM, min_dist=(10, 3, 3),
               pic_files=SurfacePlotFormat.DONTPLOT, output_prefix='',
               more_info=False, pdb_chain=None, pdb_model=None,
               pdb_bridges=Bridges.SSBOND, bridges=[], breaks=[]):
    """
    Calculates minimal surfaces spanned on given loops and checks if
    remaining parts of chains cross surfaces and how many times.
    Returns corresponding topoly types of lassos (type for each loop).

    Args:
        structure: (str/list):
                The structure containing the loop which may be pierced
                by the tail, given in coordinates, or the path to the
                file containing the data.
        loop_indices (list, optional):
                the indices of all loops within the structure (list of
                pairs). If they are not specified, SS-bonds defining
                loops are automatically found in input data (if the
                file is in PDB or CIF format). Default: None
        smooth (int, optional):
                Number of smoothing iterations. Higher number
                -- structure will be more smooth. Default: 0.
        precision (int, optional):
                Precision of computations of minimal surface. Viable
                options are the parameters of the PrecisionSurface
                class. Default: PrecisionSurface.HIGH.
        density (int, optional):
                Density of the triangulation of minimal surface. Viable
                options are the parameters of the DensitySurface class.
                Default: DensitySurface.MEDIUM
        min_dist ([int, int, int], optional):
                Minimal distance (number of atoms/amino acids etc.)
                between, respectively, next two crossings, crossing and
                bridge defining loop and crossing and end of tail -- to
                think about these crossings as deep enough ones and do
                NOT reduce them. Default: [10,3,3]
        pic_files (int/list of ints, optional):
                Output file format for generated pictures with
                surface and crossings. Possible formats: 
                * VMD -- SurfacePlotFormat.VMD or 1,
                * JSmol -- SurfacePlotFormat.JSMOL or 2,
                * Mathematica -- SurfacePlotFormat.MATHEMATICA or 4.
                Input as one of these or any combination of these as
                a list. Default: SurfacePlotFormat.DONTPLOT
        output_prefix (str, optional):
                Prefix of desired output file. Default: No prefix.
        more_info (bool, optional):
                If True, more info is returned. Look down below in 
                "return". Default: False
        pdb_chain (string, optional):
                If inputting .pdb file, which chain should be used.
                If none, the first chain is taken into account.
                Default: None.
        pdb_model (string, optional):
                If inputting .pdb file, which model should be used.
                If none, the first model is taken into account.
                Default: None.
        pdb_bridges (string, optional):
                Useful only for topoly.yamada_ and topoly.aps_ and
                when inputing .pdb file.
                Determines which bridges should be used during topoly
                analysis:
                'ssbond' -- disulfide bonds,
                'ion'  -- ionic bridges,
                'covalent' -- other covalent (non-disulfide) bridges,
                'all' -- covalent (disulfide and non-disulfide) and 
                ionic bridges. Default: 'ssbond'.
        bridges (list, optional):
                The list of tuples denoting the bridging residues in
                the main chain. Default: [].
        breaks (list, optional):
                The list of breaks of the main chain. Default: [].

    Returns:
        Dictionary with loops indices as keys and string report with 
        lasso type as values. If more_info=True more info is produced: 
        IDs of atoms that cross the surface ("crossingsN/C"); IDs of 
        atoms that cross  he surface before the procedure of crossing
        reduction ("beforeN/C"); radius of gyration ("Rg"); number of 
        iterations of structure smoothing procedure ("smoothing_iterations").

    """
    obj = Lasso(structure, loop_indices, chain=pdb_chain, model=pdb_model, bridges_type=pdb_bridges, bridges=bridges,
                breaks=breaks)
    return obj.lasso_type(
                smooth, precision, density, min_dist, pic_files, output_prefix, int(more_info))


def find_loops(structure, output_type=OutputType.PDcode, pdb_chain=None, pdb_model=None, breaks=[],
               bridges=[], pdb_bridges=Bridges.SSBOND, arc_bridges=1,
               output='list', file_prefix='loop', folder_prefix=''):
    """
    Finds all loops in a given structure and return as one of many
    possible formats.

    Args:
        structure (str/list):
                The structure to find the links in, given in abstract
                code, coordinates, or the path to the file containing
                the data.
        output_type (str/list, optional):
                The output format of the loops. The viable formats are
                parameters of the OutputType class.
                Default: OutputType.PDcode.
        pdb_chain (str, optional):
                The chain identifier in the PDB file.
                If none, the first chain is taken into account.
                Default: None.
        pdb_model (int, optional):
                The model identifier in the PDB file.
                If none, the first model is taken into account.
                Default: None.
        breaks (list, optional): 
                The list of breaks of the main chain. Default: []
        bridges (list, optional):  Default: [].
                The list of tuples denoting the bridging residues in 
                the main chain. Default: [].
        pdb_bridges (string, optional):
                Useful only for topoly.yamada_ and topoly.aps_ and
                when inputting .pdb file.
                Determines which bridges should be used during topoly
                analysis:
                'ssbond' -- disulfide bonds,
                'ion'  -- ionic bridges,
                'covalent' -- other covalent (non-disulfide) bridges,
                'all' -- covalent (disulfide and non-disulfide) and 
                ionic bridges. Default: 'ssbond'.
        arc_bridges (int, optional): 
                Number of bridges which can be included in a given loop. 
                For 0 no restriction is made. Default: 1.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
                Default: 'list'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "loop".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.

    Returns:
        List/generator/files with the loops found represented in 
        a chosen format.
    """
    g = Graph(structure, chain=pdb_chain, model=pdb_model, bridges=bridges, breaks=breaks, bridges_type=pdb_bridges)
    if output == 'generator':
        return g.find_loops(output_type=output_type, arc_bridges=arc_bridges)
    elif output == 'list':
        return list(g.find_loops(output_type=output_type, arc_bridges=arc_bridges))
    elif output == 'file':
        k = 0
        for loop in g.find_loops(output_type=output_type, arc_bridges=arc_bridges):
            if not folder_prefix:
                folder_prefix = os.getcwd()
            try:
                os.mkdir(folder_prefix)
            except:
                pass
            fname = folder_prefix + '/' + file_prefix + '_' + str(k)
            with open(fname, 'w') as myfile:
                myfile.write(str(loop))
            k += 1
        return
    else:
        raise TopolyException("Unknown output method. Possible options are 'list' (default), 'generator' or 'file'.")


def find_links(structure, output_type=OutputType.PDcode, pdb_chain=None, pdb_model=None, breaks=[],
               bridges=[], pdb_bridges=Bridges.SSBOND, arc_bridges=1, components=2,
               output='list', file_prefix='link', folder_prefix=''):
    """
    Finds all links in a given structure and return as one of many
    possible formats.

    Args:
        structure (str/list):
                The structure to find the links in, given in abstract
                code, coordinates, or the path to the file containing
                the data.
        output_type (str/list, optional):
                The output format of the loops. The viable formats are
                parameters of the OutputType class.
                Default: OutputType.PDcode.
        pdb_chain (str, optional):
                The chain identifier in the PDB file.
                If none, the first chain is taken into account.
                Default: None.
        pdb_model (int, optional):
                the model identifier in the PDB file.
                If none, the first model is taken into account.
                Default: None.
        breaks (list, optional): 
                The list of breaks of the main chain. Default: [].
        bridges (list, optional): 
                The list of tuples denoting the bridging residues in 
                the main chain. Default: [].
        pdb_bridges (string, optional):
                Useful only for topoly.yamada_ and topoly.aps_ and
                when inputting .pdb file.
                Determines which bridges should be used during topoly
                analysis:
                'ssbond' -- disulfide bonds,
                'ion'  -- ionic bridges,
                'covalent' -- other covalent (non-disulfide) bridges,
                'all' -- covalent (disulfide and non-disulfide) and 
                ionic bridges. Default: 'ssbond'.
        arc_bridges (int, optional): 
                Number of bridges which can be included in each 
                component. For 0 no restriction is made. Default: 1.
        components (int, optional): 
                Number of components in the link. Default: 2.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
                Default: 'list'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "link".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.

    Returns:
        List/generator/files with the links found represented in 
        a chosen format.
    """
    g = Graph(structure, chain=pdb_chain, model=pdb_model, bridges=bridges, breaks=breaks, bridges_type=pdb_bridges)
    if output == 'generator':
        return g.find_links(output_type=output_type, arc_bridges=arc_bridges, components=components)
    elif output == 'list':
        return list(g.find_links(output_type=output_type, arc_bridges=arc_bridges, components=components))
    elif output == 'file':
        k = 0
        for link in g.find_links(output_type=output_type, arc_bridges=arc_bridges, components=components):
            if not folder_prefix:
                folder_prefix = os.getcwd()
            try:
                os.mkdir(folder_prefix)
            except:
                pass
            fname = folder_prefix + '/' + file_prefix + '_' + str(k)
            with open(fname, 'w') as myfile:
                myfile.write(str(link))
            k += 1
        return
    else:
        raise TopolyException("Unknown output method. Possible options are 'list' (default), 'generator' or 'file'.")


def find_thetas(structure, output_type=OutputType.PDcode, pdb_chain=None, pdb_model=None, breaks=[],
               bridges=[], pdb_bridges=Bridges.SSBOND, arc_bridges=1,
               output='list', file_prefix='theta', folder_prefix=''):
    """
    Finds all theta-curves in a given structure and return as one of
    many possible formats.

    Args:
        structure (str/list):
                The structure to find the theta-curves in, given in
                abstract code, coordinates, or the path to the file
                containing the data.
        output_type (str/list, optional):
                The output format of the loops. The viable formats are
                parameters of the OutputType class.
                Default: OutputType.PDcode.
        pdb_chain (str, optional):
                The chain identifier in the PDB file.
                If none, the first chain is taken into account.
                Default: None.
        pdb_model (int, optional):
                The model identifier in the PDB file.
                If none, the first model is taken into account.
                Default: None.
        breaks (list, optional): 
                The list of breaks of the main chain. Default: [].
        bridges (list, optional): 
                The list of tuples denoting the bridging residues in the 
                main chain. Default: [].
        pdb_bridges (string, optional):
                Useful only for topoly.yamada_ and topoly.aps_ and
                when inputting .pdb file.
                Determines which bridges should be used during topoly
                analysis:
                'ssbond' -- disulfide bonds,
                'ion'  -- ionic bridges,
                'covalent' -- other covalent (non-disulfide) bridges,
                'all' -- covalent (disulfide and non-disulfide) and 
                ionic bridges. Default: 'ssbond'.
        arc_bridges (int, optional): 
                Number of bridges which can be included in each arc. For 
                0 no restriction is made. Default: 1.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
                Default: 'list'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "theta".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.

    Returns:
        List/generator/files with the theta-curves found represented in 
        a chosen format.
    """
    g = Graph(structure, chain=pdb_chain, model=pdb_model, bridges=bridges, breaks=breaks, bridges_type=pdb_bridges)
    if output == 'generator':
        return g.find_thetas(output_type=output_type, arc_bridges=arc_bridges)
    elif output == 'list':
        return list(g.find_thetas(output_type=output_type, arc_bridges=arc_bridges))
    elif output == 'file':
        k = 0
        for theta in g.find_thetas(output_type=output_type, arc_bridges=arc_bridges):
            if not folder_prefix:
                folder_prefix = os.getcwd()
            try:
                os.mkdir(folder_prefix)
            except:
                pass
            fname = folder_prefix + '/' + file_prefix + '_' + str(k)
            with open(fname, 'w') as myfile:
                myfile.write(str(theta))
            k += 1
        return
    else:
        raise TopolyException("Unknown output method. Possible options are 'list' (default), 'generator' or 'file'.")


def find_handcuffs(structure, output_type=OutputType.PDcode, pdb_chain=None, pdb_model=None, breaks=[],
               bridges=[], pdb_bridges=Bridges.SSBOND, arc_bridges=1,
               output='list', file_prefix='handcuff', folder_prefix=''):
    """
    Finds all handcuff graphs in a given structure and return as one of
    many possible formats.

    Args:
        structure (str/list):
                The structure to find the handcuff graphs in, given in
                abstract code, coordinates, or the path to the file
                containing the data.
        output_type (str/list, optional):
                The output format of the loops. The viable formats are
                parameters of the OutputType class.
                Default: OutputType.PDcode.
        pdb_chain (str, optional):
                The chain identifier in the PDB file.
                If none, the first chain is taken into account.
                Default: None.
        pdb_model (int, optional):
                The model identifier in the PDB file.
                If none, the first model is taken into account.
                Default: None.
        breaks (list, optional): 
                The list of breaks of the main chain. Default: [].
        bridges (list, optional): 
                The list of tuples denoting the bridging residues in the 
                main chain. Default: [].
        pdb_bridges (string, optional):
                Useful only for topoly.yamada_ and topoly.aps_ and
                when inputting .pdb file.
                Determines which bridges should be used during topoly
                analysis:
                'ssbond' -- disulfide bonds,
                'ion'  -- ionic bridges,
                'covalent' -- other covalent (non-disulfide) bridges,
                'all' -- covalent (disulfide and non-disulfide) and 
                ionic bridges. Default: 'ssbond'.
        arc_bridges (int, optional): 
                Number of bridges which can be included in each arc. For 
                0 no restriction is made. Default: 1.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
                Default: 'list'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "handcuff".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.

    Returns:
        List/generator/files with the handcuff graphs found represented 
        in a chosen format.
    """
    g = Graph(structure, chain=pdb_chain, model=pdb_model, bridges=bridges, breaks=breaks, bridges_type=pdb_bridges)
    if output == 'generator':
        return g.find_handcuffs(output_type=output_type, arc_bridges=arc_bridges)
    elif output == 'list':
        return list(g.find_handcuffs(output_type=output_type, arc_bridges=arc_bridges))
    elif output == 'file':
        k = 0
        for handcuff in g.find_handcuffs(output_type=output_type, arc_bridges=arc_bridges):
            if not folder_prefix:
                folder_prefix = os.getcwd()
            try:
                os.mkdir(folder_prefix)
            except:
                pass
            fname = folder_prefix + '/' + file_prefix + '_' + str(k)
            with open(fname, 'w') as myfile:
                myfile.write(str(handcuff))
            k += 1
        return
    else:
        raise TopolyException("Unknown output method. Possible options are 'list' (default), 'generator' or 'file'.")


def generate_walk(length, no_of_structures, bond_length=1, print_with_index=True, output='file',
                file_prefix='walk', folder_prefix='', file_fmt=(3, 5)):
    """
    Generates polygonal lasso structure with vertices of equal lengths
    and saves in .xyz file. Each structures is saved in distinct file
    named <file_prefix>_<num>.xyz in folder l<looplength>_t<taillength>.

    Args:
        length (int):
                Number of sides of polygonal random walk.
        no_of_structures (int):
                Quantity of created walks.
        bond_length (int, optional):
                Length of each side of created walks. Default: 1.
        print_with_index (bool, optional):
                If True, then output has also node index. Default: True.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "walk".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.
        file_fmt ([int,int], optional):
                Only if output=='file'. Numbers on file and folder
                format <num>, <length> are padded with maximally these
                numbers of zeros respectively.

    Returns:
        If output='file' -- information with folder name.
        If output='list' -- list of structures, each structure is coordinate list of lists.
        If output='generator' -- generator yielding structure which is coordinate list of lists.
    """
    if output == 'file':
        P = Polygon_walk(length, no_of_structures, bond_length, print_with_index, file_prefix,
                         folder_prefix, file_fmt)
        return P.export_polyg_xyz()
    elif output == 'list':
        P = Polygon_walk(length, no_of_structures, bond_length, print_with_index, file_prefix,
                         folder_prefix, file_fmt)
        return P.export_polyg_list()
    elif output == 'generator':
        return generate_polygon('walk', n=no_of_structures, walk_length=length, no_of_structures=1,
                                bond_length=bond_length, print_with_index=print_with_index,
                                file_prefix=file_prefix, folder_prefix=folder_prefix,
                                file_fmt=file_fmt)
    else:
        raise NameError('Parameter \'output\' accepts only \'file\', \'list\' and \'generator\''
                          'arguments')


def generate_loop(length, no_of_structures, bond_length=1, print_with_index=True, output='file',
                file_prefix='loop', folder_prefix='', file_fmt=(3, 5)):
    """
    Generates polygonal loop structure with vertices of equal lengths
    and saves in .xyz file. Each structures is saved in distinct file
    named <file_prefix>_<num>.xyz in folder w<length>.

    Args:
        length (int):
                Number of sides of polygonal loops.
        no_of_structures (int):
                Quantity of created loops.
        bond_length (int, optional):
                Length of each side of created loops. Default: 1.
        print_with_index (bool, optional):
                If True, then created .xyz has nxyz format instead of
                xyz, where n is index number. Default: True.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "loop".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.
        file_fmt ([int,int], optional):
                Only if output=='file'. Numbers on file and folder
                format <num>, <looplength> are padded with maximally
                these numbers of zeros respectively.

    Returns:
        If output='file' -- information with folder name.
        If output='list' -- list of structures, each structure is coordinate list of lists.
        If output='generator' -- generator yielding structure which is coordinate list of lists.
    """
    if output == 'file':
        P = Polygon_loop(length, no_of_structures, bond_length, print_with_index, file_prefix,
                         folder_prefix, file_fmt)
        return P.export_polyg_xyz()
    elif output == 'list':
        P = Polygon_loop(length, no_of_structures, bond_length, print_with_index, file_prefix,
                         folder_prefix, file_fmt)
        return P.export_polyg_list()
    elif output == 'generator':
        return generate_polygon('loop', n=no_of_structures, loop_length=length, no_of_structures=1,
                                bond_length=bond_length, print_with_index=print_with_index,
                                file_prefix=file_prefix, folder_prefix=folder_prefix,
                                file_fmt=file_fmt)
    else:
        raise NameError('Parameter \'output\' accepts only \'file\', \'list\' and \'generator\''
                           'arguments')


def generate_lasso(looplength, taillength, no_of_structures, bond_length=1, output='file',
                print_with_index=True, file_prefix='lasso', folder_prefix='', file_fmt=(3, 3, 5)):
    """
    Generates polygonal lasso structure with vertices of equal lengths
    and saves in .xyz file. Each structures is saved in distinct file
    named <file_prefix>_<num>.xyz in folder l<looplength>_t<taillength>.

    Args:
        looplength (int):
                Number of sides of polygonal loop.
        taillength (int):
                Number of sides of polygonal tail.
        no_of_structures (int):
                Quantity of created loops.
        bond_length (int, optional):
                Length of each side of created lassos. Default: 1.
        print_with_index (bool, optional):
                If True, then created .xyz has nxyz format instead of
                xyz, where n is index number. Default: True.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "lasso".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.
        file_fmt ([int,int,int], optional):
                Only if output=='file'. Numbers on file and folder
                format <num>, <looplength>, <taillength> are padded with
                maximally these numbers of zeros respectively.

    Returns:
        If output='file' -- information with folder name.
        If output='list' -- list of structures, each structure is coordinate list of lists.
        If output='generator' -- generator yielding structure which is coordinate list of lists.
    """
    if output == 'file':
        P = Polygon_lasso(looplength, taillength, no_of_structures, bond_length, print_with_index,
                          file_prefix, folder_prefix, file_fmt)
        return P.export_polyg_xyz()
    elif output == 'list':
        P = Polygon_lasso(looplength, taillength, no_of_structures, bond_length, print_with_index,
                          file_prefix, folder_prefix, file_fmt)
        return P.export_polyg_list()
    elif output == 'generator':
        return generate_polygon('lasso', n=no_of_structures, loop_length=looplength,
                                tail_length=taillength, no_of_structures=1, bond_length=bond_length,
                                print_with_index=print_with_index, file_prefix=file_prefix,
                                folder_prefix=folder_prefix, file_fmt=file_fmt)
    else:
        raise NameError('Parameter \'output\' accepts only \'file\', \'list\' and \'generator\''
                           'arguments')


def generate_handcuff(looplengths, linkerlength, no_of_structures, bond_length=1, output='file',
                print_with_index=True, file_prefix='hdcf', folder_prefix='', file_fmt=(3, 3, 3, 5)):
    """
    Generates polygonal lasso structure with vertices of equal lengths
    and saves in .xyz file. Each structures is saved in distinct file
    named <file_prefix>_<num>.xyz in folder
    l<looplength1>_<looplength2>_t<linkerlength>.

    Args:
        looplengths ([int,int]):
                Number of sides of polygonal loops.
        linkerlength (int):
                Number of sides of polygonal linker.
        no_of_structures (int):
                Quantity of created loops.
        bond_length (int, optional):
                Length of each side of created lassos. Default: 1.
        print_with_index (bool, optional):
                If True, then created .xyz has nxyz format instead of
                xyz, where n is index number. Default: True.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "hdcf".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.
        file_fmt ([int,int,int,int], optional):
                Only if output=='file'. Numbers on file and folder
                format <num>, <looplength1>, <looplength2>,
                <linkerlength> are padded with maximally these numbers
                of zeros respectively.

    Returns:
        If output='file' -- information with folder name.
        If output='list' -- list of structures, each structure is coordinate list of lists.
        If output='generator' -- generator yielding structure which is coordinate list of lists.
    """
    if output == 'file':
        P = Polygon_handcuff(looplengths, linkerlength, no_of_structures, bond_length,
                             print_with_index, file_prefix, folder_prefix, file_fmt)
        return P.export_polyg_xyz()
    elif output == 'list':
        P = Polygon_handcuff(looplengths, linkerlength, no_of_structures, bond_length,
                             print_with_index, file_prefix, folder_prefix, file_fmt)
        return P.export_polyg_list()
    elif output == 'generator':
        return generate_polygon('handcuff', n=no_of_structures, loop_lengths=looplengths,
                                linker_length=linkerlength, no_of_structures=1,
                                bond_length=bond_length, print_with_index=print_with_index,
                                file_prefix=file_prefix, folder_prefix=folder_prefix,
                                file_fmt=file_fmt)
    else:
        raise NameError('Parameter \'output\' accepts only \'file\', \'list\' and \'generator\''
                           'arguments')


def generate_link(looplengths, loop_dist, no_of_structures, bond_length=1, output='file',
                print_with_index=True, file_prefix='link', folder_prefix='', file_fmt=(3, 3, 3, 5)):
    """
    Generates polygonal lasso structure with vertices of equal lengths
    and saves in .xyz file. Each structures is saved in distinct file
    named <file_prefix>_<num>.xyz in folder
    l<looplength1>_<looplength2>_d<loop_dist>.

    Args:
        looplengths ([int,int]):
                Number of sides of polygonal loops.
        loop_dist (float):
                Distance between geometrical centers of loops measured
                in multiples of bond_length.
        no_of_structures (int):
                Quantity of created loops.
        bond_length (int, optional):
                Length of each side of created lassos. Default: 1.
        print_with_index (bool, optional):
                If True, then created .xyz has nxyz format instead of
                xyz, where n is index number. Default: True.
        output (str, optional):
                Format of output data 'file', 'list' or 'generator'.
        print_with_index (bool, optional):
                If True, then created .xyz has nxyz format instead of
                xyz, where n is index number. Default: True.
        file_prefix (str, optional):
                Only if output=='file'. Prefix of each created file.
                Default: "link".
        folder_prefix (str, optional):
                Only if output=='file'. Prefix of created file folder.
                Default: no prefix.
        file_fmt ([int,int,int,int], optional):
                Only if output=='file'. Numbers on file and folder
                format <num>, <looplength1>, <looplength2>, <loop_dist>
                are padded with maximally these numbers of zeros
                respectively.

    Returns:
        If output='file' -- information with folder name.
        If output='list' -- list of structures, each structure is coordinate list of lists.
        If output='generator' -- generator yielding structure which is coordinate list of lists.
    """
    if output == 'file':
        P = Polygon_link(looplengths, loop_dist, no_of_structures, bond_length, print_with_index,
                         file_prefix, folder_prefix, file_fmt)
        return P.export_polyg_xyz()
    elif output == 'list':
        P = Polygon_link(looplengths, loop_dist, no_of_structures, bond_length, print_with_index,
                         file_prefix, folder_prefix, file_fmt)
        return P.export_polyg_list()
    elif output == 'generator':
        return generate_polygon('link', n=no_of_structures, loop_lengths=looplengths,
                                loop_dist=loop_dist, no_of_structures=1,
                                bond_length=bond_length, print_with_index=print_with_index,
                                file_prefix=file_prefix, folder_prefix=folder_prefix,
                                file_fmt=file_fmt)
    else:
        raise NameError('Parameter \'output\' accepts only \'file\', \'list\' and \'generator\''
                           'arguments')


def plot_matrix(matrix, map_filename="KnotFingerPrintMap", map_fileformat=PlotFormat.PNG,
                map_cutoff=0.48, map_palette=Colors.Knots, map_arrows=True, debug=False):
    """
    Plotting the figure for a given fingerprint matrix.

    Args:
        matrix (str):
                The matrix with information about the topology of each
                subchain of the structure. Can be given either in
                dictionary, or KnotProt format. The matrix can be given
                directly, or as a path to the file.
        map_filename (str, optional):
                The name of the output file with the matrix figure.
                Default: KnotFingerPrintMap.
        map_fileformat (str, optional):
                The format of the output matrix figure. Viable options
                are the parameters of the PlotFormat class.
                Default: PlotFormat.PNG.
        map_cutoff (float, optional):
                The cutoff of the non-trivial structure probability. All
                structures with probability below the cutoff will be
                regarded as trivial, and therefore not marked in the
                figure. Default: 0.48.
        map_palette (str, optional):
                The palette of colors for matrix plot. Viable options
                are parameters of the Palette class.
                Default: Palette.KNOT.
        map_arrows (bool, optional):
                If the arrows are to be plotted. Default: True
        debug (bool, optional):
                The debug mode.

    Returns:
        Communicate about the figure creation.
    """
    return manipulation.plot_matrix(
                matrix, plot_ofile=map_filename, plot_format=map_fileformat, palette=map_palette,
                arrows=map_arrows, cutoff=map_cutoff, debug=debug)


def find_spots(matrix, gap_size=0, spot_size=20, map_cutoff=0.48):
    """
    Finds centers of fields in the matrix.

    Args:
        matrix (str/dict):
                The matrix fingerprint of the structure.
        gap_size (int, optional):
                The size of the trivial fragment allowed between two
                parts to classify them as single spot. If 0, only the
                connected fragments are considered as spots. Default: 0.
        spot_size (int, optional):
                The minimal size of the spot. Fragments with less
                non-trivial repentants will be suppressed. Default: 20.
        map_cutoff (float, optional):
                The cutoff of the non-trivial structure probability. All
                structures with probability below the cutoff will be
                regarded as trivial, and therefore not marked in the
                figure. Default: 0.48.
    Returns:
        The list of the centers of the spots.
    """
    return find_spots_centers(matrix, gap_size=gap_size, spot_size=spot_size, cutoff=map_cutoff)


def translate_matrix(matrix, output_format=OutputFormat.Dictionary, knot='', beg=0, end=0):
    """
    Translates between various formats of the matrix
    (KnotProt-like <-> dictionary <-> list of lists).

    Args:
        matrix (str/dict):
                The matrix fingerprint of the structure, or the path to
                the file with the matrix.
        output_format(string, optional):
                The format of the output matrix. The viable options are
                the paramters of the OutputFormat class.
                Default: OutputFormat.Dictionary
        knot(string, optional):
                The knot name in case the input is matrix (list of lists).
                Default: ''.
        beg(int, optional):
                The first index of the chain, needed if the input is
                matrix (list of lists). Default: 0
        end(int, optional):
                The last index of the chain, needed if the input is
                matrix (list of lists) or KnotProt string output.
                Default: 0

    Returns:
        The matrix in desired format (string, dictionary or list of lists).

    """
    if type(matrix) is str and os.path.isfile(matrix):
        with open(matrix, 'r') as myfile:
            data = myfile.read()
    else:
        data = matrix
    if output_format == OutputFormat.Dictionary:
        return data2dictionary(data, knot=knot, beg=beg)
    elif output_format == OutputFormat.KnotProt:
        return data2knotprot(data, beg=beg, end=end, knot=knot)
    elif output_format == OutputFormat.Matrix:
        return data2matrix(data)
    else:
        raise TopolyException("Unknown output format.")


def translate_matrix_polynomial(matrix, polynomial_name='Alexander', chiral=False, external_dictionary=''):
    """
  Translates a matrix file from polynomial parameters to obtain identified knots based on the dictionary
  for a given polynomial type

  Args:
      matrix (str/dict):
              The matrix fingerprint of the structure, or the path to
              the file with the matrix.
      polynomial_name(string, optional):
              The name of the polynomial that was used to calculate the matrix
              Possible values are:
              'Alexander', 'Conway', 'Jones', 'HOMFLY', 'Yamada','APS',
              'Kauffman bracket', 'Kauffman polynomial', 'BLM/Ho'
              Default: 'Alexander'
      chiral(bool, optional):
              Take into account chirality or not
              Default: False.
      external_dictionary(dict, optional):
              Use also another dictionary for the identification of knots

  Returns:
      The matrix with translated knots
  """
    if polynomial_name not in polvalues.keys():
        raise TopolyException('Unknown polynomial_name specified')
    return find_matching_structure(matrix, polynomial_name, chiral=chiral, external_dictionary=external_dictionary)


def xyz2vmd(xyz_file):
    """
    Converts .xyz file into .pdb file and creates .psf topoly file with
    same name. Then you can open your structure in vmd typing
    "vmd file.pdb -psf file.psf".

    .xyz file format: 4 columns (id, x, y, z), atoms in neighboring rows
    are treated as bonded, lines with single letter (e.g. X) separate
    different arcs.

    Args:
        xyz_file (str):
                Name of xyz file.
    Returns:
        None
    """
    return convert_xyz2vmd(xyz_file)


def plot_graph(structure, palette=Colors.Structure):
    """
    Plotting the 3D rotable presentation of the structure with each arc
    colored differently.

    Args:
        structure (str/list):
                The structure or the path to the file containing the
                data to plot.
        palette (str, optional):
                The palette of colors for matrix plot. Viable options
                are parameters of the Palette class.
                Default: Palette.RAINBOW.

    Returns:
        Communicate about the figure creation.
    """
    g = Graph(structure)
    g.plot(palette)
    return


def translate_code(structure, output_type=OutputType.PDcode):
    """
    Translates between the representations of structure. In particular,
    can print the abstract codes of a structure specified by coordinates,
    or translate between the abstract codes.

    Args:
        structure (str/list):
                The structure to print the data.
        output_type (str, optional):
                The output format. The viable formats are
                parameters of the OutputType class.
                Default: OutputType.PDcode.

    Returns:
        The structure in a given format.
    """
    g = Graph(structure)
    return g.print_data(output_type=output_type)


def find_matching(data, invariant, chiral=False, external_dictionary=''):
    """
    Finds the matching structure for a given polynomial. Searches either
    the built-in, or user-defined dictionary.

    Args:
        data (string/dictionary):
                The polynomial given either in string of coefficients
                (e.g. '1 -1 1'),
                the dictionary of polynomials with their probabilities
                (e.g. {'1 -1 1': 0.8, '1 -3 1': 0.2},
                or dictionary of probabilities for each subchain (e.g.
                {(0, 100): {'1 -1 1': 0.8, '1 -3 1': 0.2},
                (50, 100): {'1 -1 1': 0.3, '1': 0.7}}).
        invariant (string):
                The name of the invariant, e.g. 'Alexander', of 'Jones'.
        chiral (bool, optional):
                If the chirality should be taken into account.
                By default False.
        external_dictionary (string, optional):
                The absolute path to the user-defined dictionary of
                polynomials. The dictionary must be compliant with the
                template which can be obtained on the Topoly website
                (https://topoly.cent.uw.edu.pl).

    Returns:
        Either the string with matching structure name (e.g. '3_1'), or
        the dictionary with the structure name and respective
        probability (e.g. {'3_1': 0.8, '4_1': 0.2}), or the dictionary
        with data for each subchain, e.g.
        {(0, 100): {'3_1': 0.8, '4_1': 0.2},
        (50, 100): {'3_1': 0.3, '0_1': 0.7}}.
    """
    return find_matching_structure(
                data, invariant, chiral=chiral, external_dictionary=external_dictionary)


def import_structure(structure_name):
    """
    Finds a PDcode of the structure required.

    Args:
        structure_name (str):
                The name of the structure to create.

    Returns:
        The graph of the corresponding structure defined by the PDcode.
    """
    code = ''
    structure_name = structure_name.strip()
    if structure_name in PD.keys():
        code = PD[structure_name]
    else:
        for key in PD.keys():
            if re.sub('\.[1-9]*', '', re.sub('[-+*]', '', key)) == structure_name:
                code = PD[key]
                break
    if not code:
        raise TopolyException('The structure ' + str(structure_name) + ' is not available in the local library.')
    return code


def reduce_structure(structure, steps=1000, reduce_method=ReduceMethod.KMT,
                output_type=OutputType.XYZ, debug=False, closed=True):
    """
    Reducing the structure to a form with less crossing in a planar
    projection.

    Args:
        structure (str/list):
                The structure to calculate the polynomial for, given in
                abstract code, coordinates, or the path to the file
                containing the data.
        steps (int, optional):
                Number of reduction steps. Default: 1000.
        reduce_method (str, optional):
                The method used to reduce the structure. Viable methods
                are the parameters of the ReduceMethod class.
                Default: ReduceMethod.KMT.
        output_type (str, optional):
                The format of the reduced chain. The abstract codes are
                possible only for closed structure.
                Default: OutputType.XYZ.
        debug (bool, optional):
                The debug mode. Default: False.

    Returns:
        The abstract code or the coordinates of the reduced structure.
    """
    g = Graph(structure)
    #JESTEM WAZNE - CHCE ZAKOMENTOWAC KOLEJNE DWA WIERSZE
    #if not g.closed:
    #    raise TopolyException("The curve is not closed. Use topoly.close_curve first.")
    abstract_reduction = [ReduceMethod.EASY, ReduceMethod.REIDEMEISTER]
    abstract_output = [OutputType.EMcode, OutputType.PDcode]
    if reduce_method in abstract_reduction and output_type not in abstract_output:
        raise TopolyException("With chosen reduction method only the abstract codes are possible")
    g.reduce(method=reduce_method, steps=steps, debug=debug, closed=closed)
    return g.print_data(output_type=output_type)


def close_curve(structure, closure=Closure.TWO_POINTS, output_type=OutputType.XYZ, debug=False):
    """
    Closing the structure (connecting loose ends) with a chosen method.

    Args:
        structure (str/list):
                The structure to calculate the polynomial for, given in
                abstract code, coordinates, or the path to the file
                containing the data.
        closure (str, optional):
                The method used to close the structure. Viable methods
                are the parameters of the Closure class.
                Default: Closure.TWO_POINTS.
        output_type (str, optional):
                The format of the closed chain.
                Default: OutputType.XYZ.
        debug (bool, optional):
                The debug mode. Default: False.

    Returns:
        The abstract code or the coordinates of the closed structure.
    """
    g = Graph(structure)
    g.close(method=closure, debug=debug)
    return g.print_data(output_type=output_type)
