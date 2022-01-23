try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_ascii import OMFITascii

import numpy as np

__all__ = ['OMFITgnuplot']


class OMFITgnuplot(OMFITascii, SortedDict):
    r"""
    Class used to parse ascii gnuplot data files
    Gnuplot data indices are split by double empty lines
    Gnuplot data blocks are split by a single empty line

    :param filename: filename passed to OMFITobject class

    :param comment: character

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, comment='#', **kw):
        kw['comment'] = comment
        self.comment = comment
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read()
        lines = lines.split('\n')
        for k, line in enumerate(lines):
            if self.comment in line:
                lines[k] = line.split(self.comment)[0] + '\n'
        lines = '\n'.join(lines).strip('\n')
        INDEX = lines.split('\n\n\n')
        for kindex, index in enumerate(INDEX):
            BLOCK = index.split('\n\n')
            for kblock, block in enumerate(BLOCK):
                self[kindex, kblock] = np.atleast_2d(np.genfromtxt(StringIO(block)))

    def plot(self, ix=0, iy=1, **kw):
        r"""
        Plot individual data-sets

        :param ix: index of the data column to be used for the X axis

        :param iy: index of the data column to be used for the Y axis

        :param \**kw: parameters passed to the matplotlib plot function
        """
        for item in self:
            if self[item].shape[1] == 1:
                pyplot.plot(self[item][:, ix], **kw)
            elif self[item].shape[1] >= 2:
                pyplot.plot(self[item][:, ix], self[item][:, iy], **kw)


############################################
if __name__ == '__main__':
    test_classes_main_header()

    lines = '''
    1 2 3 4
    5 6 7 8
    %bla
    9 10 11 12
    13 14 15 16


    17 18 19 20 21
    22 23 24 25 26
    '''

    gplot = OMFITgnuplot('gnuplot.txt', fromString=lines, comment='%')
    print(gplot[(1, 0)])
