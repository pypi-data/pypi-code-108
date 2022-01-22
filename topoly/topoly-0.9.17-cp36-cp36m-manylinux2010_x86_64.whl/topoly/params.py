# -*- coding: utf-8 -*-
import sys
""" 
Topoly Parameters
This module contains common parameters for various functions used in Topoly
"""
class Translate:
    """
    Variant of polynomial invariant value translation to topology type.
    """
    NO = False
    """ Without translation."""
    YES = True
    """ Translate if known structure. Print "Unknown" in other cases."""
    BOTH = 'both'
    """ Print both -- translation and polynomial value."""
    PIU = 'piu'
    """ Translate if nown structure. Print polynomial value if other cases.
    (PIU -- Polvalue If Unknown)."""

class Closure:
    """
    Type of closure for invariant calculating functions.
    """
    CLOSED = 0
    """ (Deterministic) direct segment between two endpoints. """
    MASS_CENTER = 1
    """ (Deterministic) segments added to two endpoints in the direction
    "going out of center of mass", and then connected by an arc on the 
    big sphere."""
    TWO_POINTS = 2
    """ (Random) each endpoint connected with different random point on
    the big sphere, and those added points connected by an arc on the
    big sphere."""
    ONE_POINT = 3
    """ (Random) both endpoints connected with the same random point on
    the big sphere."""
    RAYS = 4
    """ (Random) parallel segments added to two endpoints, and then 
    connected by an arc on the big sphere; direction of added segments
    is random."""
    DIRECTION = 5
    """ (Deterministic) the same as RAYS but the direction can be given."""

class ReduceMethod:
    """
    Reduction method for invariant calculating functions.
    """
    KMT = 1
    """ KMT algorithm [ Koniaris K, Muthukumar M (1991) 
    Self-entanglement in ring polymers, J. Chem. Phys. 95, 2873–2881 ]. 
    This algorithm analyzes all triangles in a chain made by three 
    consecutive amino acids, and removes the middle amino acid in case 
    a given triangle is not intersected by any other segment of the 
    chain. In effect, after a number of iterations, the initial chain 
    is replaced by (much) shorter chain of the same topological type."""
    REIDEMEISTER = 2
    """ Simplification of chain (and number of crossings) by a sequence
    of Reidemeister moves."""
    EASY = 3
    """ The deterministic version of Reidemeister simplification, using
    only the 1st and 2nd move."""


class SurfacePlotFormat:
    """
    The output formats for minimal surface plotting.
    """
    DONTPLOT = 0 
    """Without plotting."""
    VMD = 1
    """Plot files to visualisation in VMD."""
    JSMOL = 2
    """Plot files to visualisation in JSMOL."""
    MATHEMATICA = 4
    """Plot files to visualisation in Mathematica."""

class TopolyException(Exception):
    pass

class PlotFormat:
    """
    The output format for images.
    """
    PNG = 'png'
    """.png file -- lossless compression, raster."""
    SVG = 'svg' 
    """.svg -- lossless, vector."""
    PDF = 'pdf'
    """.pdf -- portable document format."""

class OutputFormat:
    """
    The output formats for matrices.
    """
    KnotProt = 'knotprot'
    """ The matrix in the format used in KnotProt."""
    Dictionary = 'dict'
    """ The dictionary-like output."""
    Matrix = 'matrix'
    """ The matrix-like (list of lists) output"""
    Ccode = 'Ccode'
    """ The output suitable for passing to C-coded parts of the package."""

class PrecisionSurface:
    """
    Precision of computations of minimal surface spanned on the loop 
    (high precision => time consuming computations).
    """
    HIGH = 0
    """ High precision level. Default. """
    MEDIUM = 1
    """ Medium precision level, may be used when analyzing large 
    structures, trajectories or other big sets of data."""
    LOW = 2
    """ Lowest precision level, may be used when analyzing large 
    structures, trajectories or other big sets of data."""

class DensitySurface:
    """
    Density of the triangulation of minimal surface spanned on the loop 
    (high density => time consuming computations).
    Default value: MEDIUM.
    """
    HIGH = 2
    """ The highest density. """
    MEDIUM = 1
    """ Medium precision level. Default."""
    LOW = 0
    """ Lowest precision level, may be used when analyzing large 
    structures, trajectories or other big sets of data."""

class Bridges:
    """
    The bridges types to be parsed from PDB file.
    """
    SSBOND = 'ssbond'
    """ Disulfide bonds. """
    ION = 'ion'
    """ Ionic bridges. """
    COVALENT = 'covalent'
    """ Other covalent (non-disulfide) bridges. """
    ALL = 'all'
    """ Covalent (disulfide and non-disulfide) and ionic bridges. """

class OutputType:
    """
    The possible output types for find_loops, find_thetas, etc.
    """
    PDcode = 'pdcode'
    """ PDcode format """
    EMcode = 'emcode'
    """ EMcode format """
    XYZ = 'xyz'
    """ .xyz file format (only coordinates) """
    NXYZ = 'nxyz'
    """ .xyz file format (indexes and coordinates) """
    PDB = 'pdb'
    """ PDB file format """
    Mathematica = 'math'
    """ Mathematica list format """
    MMCIF = 'mmcif'
    """ mmcif structure format """
    PSF = 'psf'
    """ psf topology file format """
    IDENT = 'ident'
    """ indices of first and last atom of each arc of the structure """
    ATOMS = 'atoms'
    """  """
    
class Colors:
    """
    Colors for drawing figures.
    """
    Knots = {'name': 'knot', '5_1': 'Reds', '6_1': 'Blues',
             '3_1': 'Greens', '5_2': 'Purples', '4_1': 'Oranges', '8_20|3_1#3_1': 'Reds'}
    """ Default knot fields colors in knot map """
    GLN = {'name': 'GLN', '': 'seismic'}
    """ Default colormap for GLN maps """
    Structure = {'name': 'structure', 'all': 'hsv'}
    """ Default colormap for structure plotting using plot_graph """
    Writhe = {'name': 'writhe', 'all': 'Spectral'}
    # def colorFromGLN(gln):
    #     if (gln < -1):
    #         return (int(255 * 1 / (gln * gln)), 0, 0)
    #     elif (gln <= 0):
    #         return (255, int(255 * (1 + gln)), int(255 * (1 + gln)))
    #     elif (gln <= 1):
    #         return (int(255 * (1 - gln)), int(255 * (1 - gln)), 255)
    #     else:
    #         return (0, 0, int(255 * 1 / (gln * gln)))

def test(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            print('  Error occurred:', sys.exc_info()[0], sys.exc_info()[1])
            return None
    return wrapper
