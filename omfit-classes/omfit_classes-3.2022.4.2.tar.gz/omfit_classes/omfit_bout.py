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

__all__ = ['boutdata', 'boututils', 'OMFITbout', 'OMFITboutinp']

from omfit_classes.omfit_data import OMFITncDataset, DataArray, Dataset
from omfit_classes.omfit_ini import OMFITini

if 'BOUT_TOP' in os.environ:
    _bout_pythonpath = os.path.abspath(os.environ['BOUT_TOP'] + os.sep + 'tools' + os.sep + 'pylib')
    if _bout_pythonpath not in [os.path.abspath(_path) for _path in sys.path]:
        sys.path.insert(1, _bout_pythonpath)
        print('* Path to BOUT python tools has been added: ' + _bout_pythonpath)
    else:
        print('* Path to BOUT python tools was found' + _bout_pythonpath)
    if 'PYTHONPATH' in os.environ and os.environ['PYTHONPATH']:
        if _bout_pythonpath not in os.environ['PYTHONPATH']:
            os.environ['PYTHONPATH'] = _bout_pythonpath + ':' + os.environ['PYTHONPATH']
    else:
        os.environ['PYTHONPATH'] = _bout_pythonpath

try:
    import netCDF4

    with quiet_environment():
        import boutdata
        import boututils
except Exception as _excp:
    boututils = boutdata = None
    warnings.warn('No `boutdata` and `boututils` support (BOUT_TOP environment variable): ' + repr(_excp))


class OMFITbout(OMFITncDataset):
    def __init__(self, filename, grid=None, tlim=None, **kw):
        if os.path.isdir(filename):
            filename = filename + os.sep + 'BOUT.dmp.0.nc'
        directory = os.path.split(filename)[0]

        # data already collected
        if not re.match(r'.*BOUT\.dmp\.[0-9]*\.nc', filename):
            OMFITncDataset.__init__(self, filename, **kw)

        # collect
        else:
            printi('Collecting BOUT++ quantities to a single file')

            tind = None
            if tlim is not None:
                t_array = boutdata.collect('t_array', path=directory, info=False)
                tind = [max([0, len(t_array) - tlim]), len(t_array)]

            OMFITncDataset.__init__(self, 'BOUT.dmp.nc')
            self.dynaLoad = False

            with netCDF4.Dataset(filename) as f:
                keys = list(f.variables.keys())
                for k, uvar in enumerate(keys):
                    var = str(uvar)
                    printi('[% 3d/% 3d] %s' % (k + 1, len(keys), var))
                    dims = list(f.variables[uvar].dimensions)
                    if len(dims) == 0:
                        continue
                    self[var] = DataArray(boutdata.collect(var, path=directory, info=False, tind=tind), dims=dims)

        # add grid information
        if grid is not None:
            self.add_grid(grid)

    def add_grid(self, grid):
        if grid is not None:
            self.update(grid)

    def pol_slice(self, var3d, n=1, zangle=0.0, info=True):
        """
        return 2D data from 3D array with x, y, z dimensions

        :param var3d: variable to process (string or 3D variable)

        :param n: toroidal mode number

        :param zangle: toroidal angle

        :param info: print info to screent

        :return: 2d data
        """
        n = int(n)
        zangle = float(zangle)

        if isinstance(var3d, str):
            var3d = self[var3d].values

        s = np.shape(var3d)
        if len(s) != 3:
            raise Exception('ERROR: pol_slice expects a 3D variable')

        nx, ny, nz = s

        dz = 2.0 * np.pi / float(n * (nz - 1))

        # Check the grid size is correct
        if self['nx'] != nx:
            raise Exception('ERROR: Grid X size is different to the variable')
        if self['ny'] != ny:
            raise Exception('ERROR: Grid Y size is different to the variable')

        # Get the toroidal shift
        if 'qinty' in self:
            zShift = self['qinty'].values
            if infp:
                print('Using qinty as toroidal shift angle')
        elif 'zShift' in self:
            zShift = self['zShift'].values
            if info:
                print('Using zShift as toroidal shift angle')
        else:
            raise Exception('ERROR: Neither qinty nor zShift found')

        var2d = np.zeros([nx, ny])

        ######################################
        # Perform 2D slice
        zind = (zangle - zShift) / dz
        z0f = np.floor(zind)
        z0 = z0f.astype(int)
        p = zind - z0f

        # Make z0 between 0 and (nz-2)
        z0 = ((z0 % (nz - 1)) + (nz - 1)) % (nz - 1)

        # Get z+ and z-
        zp = (z0 + 1) % (nz - 1)
        zm = (z0 - 1 + (nz - 1)) % (nz - 1)

        # There may be some more cunning way to do this indexing
        for x in np.arange(nx):
            for y in np.arange(ny):
                var2d[x, y] = (
                    0.5 * p[x, y] * (p[x, y] - 1.0) * var3d[x, y, zm[x, y]]
                    + (1.0 - p[x, y] * p[x, y]) * var3d[x, y, z0[x, y]]
                    + 0.5 * p[x, y] * (p[x, y] + 1.0) * var3d[x, y, zp[x, y]]
                )

        return var2d


class OMFITboutinp(OMFITini):
    """
    OMFIT class used to interface with BOUT++ configuration files (INP files).

    This class is based on the configobj class https://configobj.readthedocs.io/en/latest/index.html

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.list_values = False


############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp = OMFITboutinp(f'{OMFITsrc}/../samples/BOUT.inp')
    tmp.load()
