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
from omfit_classes import zdata
import numpy as np

__all__ = ['OMFITfastran']


class OMFITfastran(SortedDict, OMFITascii):
    """FASTRAN data files"""

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self, sorted=True)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        self.clear()
        tmp = zdata.read_formatted(self.filename)
        self.update(tmp)
        for k in self:
            if len(self[k]) == 1:
                self[k] = self[k][0]
            else:
                self[k] = np.array(self[k])

    @dynaSave
    def save(self):
        tmp = {}
        tmp.update(self)
        for k in self:
            self[k] = np.atleast_1d(self[k]).tolist()
        zdata.from_dict(self, self.filename)
