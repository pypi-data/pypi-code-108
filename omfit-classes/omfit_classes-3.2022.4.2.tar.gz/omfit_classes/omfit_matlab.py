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

import numpy as np
from scipy.io import loadmat, savemat, matlab

__all__ = ['OMFITmatlab']


class OMFITmatlab(SortedDict, OMFITobject):
    r"""
    OMFIT class used to interface with MATLAB .mat files up to version 7.2

    This class makes use of the scipy.io.loadmat/savemat interface

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITobject.__init__(self, filename, **kw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute
        """
        if not (len(self.filename) and os.path.exists(self.filename) and os.stat(self.filename).st_size):
            return

        vars = loadmat(self.filename, appendmat=False, mat_dtype=False, squeeze_me=True, struct_as_record=False, chars_as_strings=True)

        def f_traverse(me, mat):
            if isinstance(mat, dict):
                keys = list(mat.keys())
            else:
                keys = mat._fieldnames
            for item in keys:
                if isinstance(mat, dict):
                    kid = mat[item]
                else:
                    kid = getattr(mat, item)
                if isinstance(kid, np.ndarray) and not len(kid.shape):
                    me[item] = kid.tolist()
                elif isinstance(kid, (dict, matlab.mio5_params.mat_struct)):
                    me[item] = {}
                    f_traverse(me[item], kid)
                else:
                    me[item] = kid

        self.clear()
        f_traverse(self, vars)

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        savemat(self.filename, self)
