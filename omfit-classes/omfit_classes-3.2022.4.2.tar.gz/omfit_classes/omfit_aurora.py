'''
Provides classes and utility functions for easily using Aurora within OMFIT.
Documentation: https://aurora-fusion.readthedocs.io/
'''

try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise


__all__ = ['OMFITaurora']


class OMFITaurora(SortedDict, OMFITobject):
    r"""
    OMFIT class used to interface with Aurora simulation files.

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, namelist=None, geqdsk=None, **kw):

        # AURORA is currently an OPTIONAL dependency, so import here
        from aurora.core import aurora_sim

        OMFITobject.__init__(self, filename, **kw)
        SortedDict.__init__(self)

        # user is initializing class
        if namelist is not None:
            self.dynaLoad = False
        else:
            self.dynaLoad = True

        self.aurora_sim = aurora_sim(namelist=namelist, geqdsk=geqdsk)

    @dynaLoad
    def __getitem__(self, key):
        return getattr(self.aurora_sim, key)

    @dynaLoad
    def __setitem__(self, key, value):
        return setattr(self.aurora_sim, key, value)

    @dynaLoad
    def __getattr__(self, attr):
        return getattr(self.aurora_sim, attr)

    def __setattr__(self, attr, value):
        if 'aurora_sim' in self.__dict__ and attr not in self.__dict__:
            if self.dynaLoad:
                self.load()
                self.dynaLoad = False
            setattr(self.aurora_sim, attr, value)
        else:
            self.__dict__[attr] = value

    @dynaLoad
    def keys(self):
        return self.aurora_sim.__dict__.keys()

    @dynaLoad
    def items(self):
        return self.aurora_sim.__dict__.items()

    @dynaLoad
    def load(self):
        print(f'Loading {self.filename}')
        return self.aurora_sim.load(self.filename)

    @dynaSave
    def save(self):
        print(f'Saving {self.filename}')
        return self.aurora_sim.save(self.filename)
