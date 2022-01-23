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


from omfit_classes.omfit_base import OMFITcollection
from omfit_classes.sortedDict import SortedDict

import numpy as np
import scipy
from scipy import io

__all__ = ['OMFITidlSav']


class OMFITidlSav(SortedDict, OMFITobject):
    r"""
    OMFIT class used to interface with IDL .sav files
    Note that these objects are "READ ONLY", meaning that the changes to the entries of this object will not be saved to a file.
    This class is based on a modified version of the idlsave class provided by https://github.com/astrofrog/idlsave
    The modified version (omfit/omfit_classes/idlsaveOM.py) returns python dictionaries instead of np.recarray objects

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        self.caseInsensitive = True
        OMFITobject.__init__(self, filename, **kw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """

        if not (len(self.filename) and os.path.exists(self.filename) and os.stat(self.filename).st_size):
            return

        orig_sav = scipy.io.readsav(self.filename, verbose=False)

        def get_iter(other_):
            if isinstance(other_, dict):
                keys = list(other_.keys())
            elif isinstance(other_, np.recarray):
                keys = other_.dtype.names
            elif isinstance(other_, list):
                keys = list(range(len(other_)))
            elif isinstance(other_, np.ndarray):
                keys = list(range(len(other_)))
            return keys

        def f_traverse(me, other_, keys):
            for key in keys:
                other = other_[key]
                if isinstance(other, (np.recarray, np.record)):
                    convert_to_dict = False
                    if other.dtype.names is not None:
                        for item in other.dtype.names:
                            if (isinstance(other[item], np.ndarray) and other[item].dtype == object) or isinstance(
                                other[item], np.recarray
                            ):
                                convert_to_dict = True
                                break
                    else:
                        me[key] = np.array(other)
                        continue
                    if convert_to_dict:
                        keys2 = get_iter(other)
                        if len(keys2) == 1:
                            me[key] = other[keys2[0]]
                            continue
                        else:
                            if other.shape[0] > 1:
                                printd(key, 'is going to be OMFITcollection because len(keys2)!=1 and other.shape[0]>1', topic='idlSav')
                                me[key] = OMFITcollection(sorted=True)
                                # me[key] = SortedDict(sorted=True)
                                for row in range(other.shape[0]):
                                    mydict = SortedDict(sorted=True)
                                    f_traverse(mydict, other[row], keys2)
                                    me[key][row] = mydict
                            else:
                                me[key] = SortedDict(sorted=True)
                                f_traverse(me[key], other[0], keys2)

                    else:
                        me[key] = other
                elif isinstance(other, np.ndarray) and other.dtype == object:
                    keys2 = get_iter(other)
                    if len(keys2) == 1:
                        me[key] = other[keys2[0]]
                    elif np.all([isinstance(b2s(other[x]), str) for x in keys2]):
                        me[key] = b2s(other)
                    else:
                        printd(key, 'is going to be OMFITcollection because len(keys2)!=1 and keys2 not str; keys2=', keys2, topic='idlSav')
                        me[key] = OMFITcollection(sorted=True)
                        # me[key] = SortedDict(sorted=True)
                        f_traverse(me[key], other, keys2)
                elif isinstance(other, np.ndarray) and len(other.shape) == 1 and other.shape[0] == 1:
                    me[key] = other[0]
                elif isinstance(other, bytes):
                    me[key] = other.decode('utf-8')
                else:
                    me[key] = other

        f_traverse(self, orig_sav, get_iter(orig_sav))
