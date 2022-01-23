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

from omfit_classes.omfit_error import OMFITobjectError

__all__ = ['OMFITpdb']

try:
    import pact.pdb as pdb
except Exception as _excp:
    pdb_error = repr(_excp)

    class OMFITpdb(OMFITobjectError):
        def __init__(self, filename, **kw):
            super().__init__(filename, 'OMFITpdb', error=pdb_error, **kw)


else:

    class OMFITpdb(SortedDict, OMFITobject):
        r"""
        OMFIT class used to interface with PACT pdb files: https://wci.llnl.gov/codes/pact/

        :param filename: filename passed to OMFITobject class

        :param \**kw: keyword dictionary passed to OMFITobject class
        """

        def __init__(self, filename, **kw):
            OMFITobject.__init__(self, filename, **kw)
            SortedDict.__init__(self, sorted=True)
            self.dynaLoad = True

        @dynaLoad
        def load(self):
            with pdb.open(self.filename, 'r') as f:
                for var in f.ls():
                    tmp = f.read(var)
                    sub = self
                    if '@' in var:
                        sub = self.setdefault(var.split('@')[1], SortedDict())
                        var = var.split('@')[0]
                    if isinstance(tmp, (list, tuple)):
                        if isinstance(tmp[0], str):
                            sub[var] = ''.join(tmp).decode('ascii', errors='ignore')
                        else:
                            sub[var] = np.array(tmp)
                            if sub[var].size == 1:
                                sub[var] = sub[var][0]
                            elif len(sub[var].shape) > 1:
                                sub[var] = np.reshape(sub[var][:], sub[var].shape[::-1])
                    else:
                        sub[var] = tmp
                    if isinstance(sub[var], int64):
                        sub[var] = int(sub[var])

        @dynaSave
        def save(self):
            with pdb.open(self.filename, 'w') as f:
                for sub in self:
                    for var in self[sub]:
                        tmp = self[sub][var]
                        if isinstance(tmp, str):
                            tmp = str(tmp)
                        elif isinstance(tmp, np.ndarray):
                            if len(tmp.shape) > 1:
                                tmp = np.reshape(tmp[:], tmp.shape[::-1])
                            tmp = tmp.tolist()
                        try:
                            f.write(var + '@' + sub, tmp)
                        except Exception as _excp:
                            printe('Could not write PDB variable ' + var + '@' + sub)
                            raise
