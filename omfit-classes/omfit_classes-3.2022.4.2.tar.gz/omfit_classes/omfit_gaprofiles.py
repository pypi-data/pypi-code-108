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

__all__ = ['OMFITplasma_cer']

import numpy as np


class OMFITplasma_cer(OMFITascii, SortedDict):
    """
    Process a GAprofiles dplasma_cer_foramt.shot.time file
    """

    def __init__(self, filename, **kw):
        r"""
        :param filename: The path to the file

        :param \**kw: Passed to OMFITascii.__init__
        """
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        content = self.read().split('\n')
        if content[0] != '       rho     Ti (keV)  nc(e19 m**3)  Vpol (km/s)  Vtor (km/s) Er (kV/m)    Er_RBpol (krad/s)':
            raise ValueError('Unknown file format')
        cols = ' '.join(content[0].split()[1:])
        data = np.loadtxt(self.filename, skiprows=1)

        self['data'] = data
        self['rho'] = data[:, 0]
        for i, c in enumerate(cols.split(')')[:-1], 1):
            self[c + ')'] = data[:, i]
