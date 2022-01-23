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

from omfit_classes.exceptions_omfit import doNotReportException as DoNotReportException

from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_nc import OMFITnc
from omfit_classes.omfit_namelist import OMFITnamelist

from omfit_classes import fluxSurface
from omfit_classes.fluxSurface import fluxSurfaces, fluxSurfaceTraces, boundaryShape, BoundaryShape, fluxGeo, rz_miller, miller_derived
from omfit_classes import namelist
from omfit_classes.omfit_mds import OMFITmdsValue
from omfit_classes.omfit_error import OMFITerror

from omfit_classes import utils_fusion
from omfit_classes.utils_fusion import is_device
from omfit_classes.utils_math import contourPaths, closestIndex, RectBivariateSplineNaN, interp1e, interp1dPeriodic, fourier_boundary

from omas import ODS, omas_environment, cocos_transform, define_cocos
import scipy
from scipy import interpolate, integrate
from matplotlib import pyplot
import numpy as np
import itertools
import fortranformat

__all__ = [
    'read_basic_eq_from_mds',
    'from_mds_plus',
    'OMFIT_pcs_shape',
    'read_basic_eq_from_toksearch',
    'x_point_search',
    'x_point_quick_search',
    'gEQDSK_COCOS_identify',
]
for k in ['', 'a', 'g', 'k', 'm', 's']:
    __all__.append('OMFIT%seqdsk' % k)
__all__.extend(fluxSurface.__all__)


############################
# auto CLASS OMFITeqdsk    #
############################
def OMFITeqdsk(filename, EFITtype=None, **kw):
    r"""
    Automatically determine the type of an EFIT file and parse it with the appropriate class.
    It is faster to just directly use the appropriate class. Using the right class also avoids problems because some
    files technically can be parsed with more than one class (no exceptions thrown), giving junk results.

    :param filename: string
        Name of the file on disk, including path

    :param EFITtype: string
        Letter giving the type of EFIT file, like 'g'. Should be in 'gamks'.
        If None, then the first letter in the filename is used to determine the file type
        If this is also not helping, then a brute-force load is attempted

    :param strict: bool
        Filename (not including path) must include the letter giving the file type.
        Prevents errors like using sEQDSK to parse g133221.01000, which might otherwise be possible.

    :param \**kw: Other keywords to pass to the class that is chosen.

    :return: OMFIT*eqdsk instance
    """
    if EFITtype is None:
        EFITtype = os.path.split(filename)[1][0].lower()

    if EFITtype in ['g', 'e']:
        return OMFITgeqdsk(filename, **kw)
    elif EFITtype == 'a':
        return OMFITaeqdsk(filename, **kw)
    elif EFITtype in ['k', 'r', 'x']:
        return OMFITkeqdsk(filename, **kw)
    elif EFITtype == 'm':
        return OMFITmeqdsk(filename, **kw)
    elif EFITtype == 's':
        return OMFITseqdsk(filename, **kw)
    else:
        eqdsk_classes = SortedDict([['g', OMFITgeqdsk], ['a', OMFITaeqdsk], ['m', OMFITmeqdsk], ['k', OMFITkeqdsk], ['s', OMFITseqdsk]])
        loaded = False
        exceptions = []
        for EFITtype in eqdsk_classes:
            try:
                tmp = eqdsk_classes[EFITtype](filename, **kw)
                tmp.load()
            except Exception as _excp:
                exceptions += ['\n\nNot {}EQDSK:\n{}'.format(EFITtype, repr(_excp))]
            else:
                loaded = True
                tmp.close()
                break
        if not loaded:
            raise TypeError(''.join(exceptions))
        printe(
            '''You have just loaded a `%s` file: %s
The OMFITeqdsk wrapper is slower than just using the OMFIT%seqdsk
For better performance, please adjust your code. OMFITeqdsk will be deprecated.'''
            % (EFITtype, os.path.split(filename)[1], EFITtype)
        )
        return tmp


class XPointSearchFail(ValueError, DoNotReportException):
    """x_point_search failed"""


def x_point_quick_search(rgrid, zgrid, psigrid, psi_boundary=None, psi_boundary_weight=1.0, zsign=0):
    """
    Make a quick and dirty estimate for x-point position to guide higher quality estimation

    The goal is to identify the primary x-point to within a grid cell or so

    :param rgrid: 1d float array
        R coordinates of the grid

    :param zgrid: 1d float array
        Z coordinates of the grid

    :param psigrid: 2d float array
        psi values corresponding to rgrid and zgrid

    :param psi_boundary: float [optional]
        psi value on the boundary; helps distinguish the primary x-point from other field nulls
        If this is not provided, you may get the wrong x-point.

    :param psi_boundary_weight: float
        Sets the relative weight of matching psi_boundary compared to minimizing B_pol.
        1 gives ~equal weight after normalizing Delta psi by grid spacing and r (to make it comparable to B_pol in
        the first place)
        10 gives higher weight to psi_boundary, which might be nice if you keep locking onto the secondary x-point.
        Actually, it seems like the outcome isn't very sensitive to this weight. psi_boundary is an adequate tie
        breaker between two B_pol nulls with weights as low as 1e-3 for some cases, and it's not strong enough to move
        the quick estiamte to a different grid cell on a 65x65 with weights as high as 1e2. Even then, the result is
        still close enough to the True X-point that the higher quality algorithm can find the same answer. So, just
        leave this at 1.

    :param zsign: int
        If you know the X-point you want is on the top or the bottom, you can pass in 1 or -1 to exclude
        the wrong half of the grid.

    :return: two element float array
        Low quality estimate for the X-point R,Z coordinates with units matching rgrid
    """
    rr, zz = np.meshgrid(rgrid, zgrid)
    [dpsidz, dpsidr] = np.gradient(psigrid, zgrid[1] - zgrid[0], rgrid[1] - rgrid[0])
    br = dpsidz / rr
    bz = -dpsidr / rr
    bpol2 = br ** 2 + bz ** 2
    if psi_boundary is None:
        dpsi2 = psigrid * 0
    else:
        dpsi2 = (psigrid - psi_boundary) ** 2
    gridspace2 = (zgrid[1] - zgrid[0]) * (rgrid[1] - rgrid[0])  # For normalizing dpsi2 so it can be compared to bpol2
    dpsi2norm = abs(dpsi2 / gridspace2 / rr ** 2)
    deviation = bpol2 + psi_boundary_weight * dpsi2norm
    if zsign == 1:
        deviation[zz <= 0] = np.nanmax(deviation) * 10
    elif zsign == -1:
        deviation[zz >= 0] = np.nanmax(deviation) * 10
    idx = np.nanargmin(deviation)
    rx = rr.flatten()[idx]
    zx = zz.flatten()[idx]
    return np.array([rx, zx])


def x_point_search(rgrid, zgrid, psigrid, r_center=None, z_center=None, dr=None, dz=None, zoom=5, hardfail=False, **kw):
    """
    Improve accuracy of X-point coordinates by upsampling a region of the fluxmap around the initial estimate

    Needs some sort of initial estimate to define a search region

    :param rgrid: 1d float array
        R coordinates of the grid
    :param zgrid: 1d float array
        Z coordinates of the grid
    :param psigrid: 2d float array
        psi values corresponding to rgrid and zgrid
    :param r_center: float
        Center of search region in r; units should match rgrid. Defaults to result of x_point_quick_search()
    :param z_center: float
        Center of the search region in z.
    :param dr: float
        Half width of the search region in r. Defaults to about 5 grid cells.
    :param dz:
        Half width of the search region in z. Defaults to about 5 grid cells.
    :param zoom: int
        Scaling factor for upsample
    :param hardfail: bool
        Raise an exception on failure
    :param kw: additional keywords passed to x_point_quick_search r_center and z_center are not given.
    :return: two element float array
        Higher quality estimate for the X-point R,Z coordinates with units matching rgrid
    """
    printd(
        f'Inputs to x_point_search: rgrid[0] = {rgrid[0]}, rgrid[-1] = {rgrid[-1]}, len(rgrid) = {len(rgrid)}, '
        f'zgrid[0] = {zgrid[0]}, zgrid[-1] = {zgrid[-1]}, len(zgrid) = {len(zgrid)}, '
        f'shape(psigrid) = {np.shape(psigrid)}, '
        f'r_center = {r_center}, z_center = {z_center}, dr = {dr}, dz = {dz}, zoom = {zoom}',
        topic='x_point_search',
    )
    # Get the basics
    psigrid = psigrid
    dr = dr or (rgrid[1] - rgrid[0]) * 5
    dz = dz or (zgrid[1] - zgrid[0]) * 5
    # Guess center of search region, if not provided
    if (r_center is None) or (z_center is None):
        r_center, z_center = x_point_quick_search(rgrid, zgrid, psigrid, **kw)
    # Select the region
    selr = (rgrid >= (r_center - dr)) & (rgrid <= (r_center + dr))
    selz = (zgrid >= (z_center - dz)) & (zgrid <= (z_center + dz))
    if sum(selr) == 0 or sum(selz) == 0:
        if hardfail:
            raise XPointSearchFail(
                f'There were no grid points within the search region: '
                f'{r_center - dr} <= R <= {r_center + dr}, {z_center - dz} <= Z <= {z_center + dz}'
            )
        else:
            return np.array([np.NaN, np.NaN])
    # Zoom in on the region of interest
    r = scipy.ndimage.zoom(rgrid[selr], zoom)
    z = scipy.ndimage.zoom(zgrid[selz], zoom)
    psi = scipy.ndimage.zoom(psigrid[selz, :][:, selr], zoom)
    printd(
        f'x_point_search status update: sum(selr) = {sum(selr)}, sum(selz) = {sum(selz)}, '
        f'len(r) = {len(r)}, len(z) = {len(z)}, shape(psi) = {np.shape(psi)}',
        topic='x_point_search',
    )
    # Find Br and Bz in the region
    rr, zz = np.meshgrid(r, z)
    [dpsidz, dpsidr] = np.gradient(psi, z[1] - z[0], r[1] - r[0])
    br = dpsidz / rr
    bz = -dpsidr / rr
    # Find the curve where Br = 0
    segments = contourPaths(r, z, br, [0], remove_boundary_points=True)[0]
    if len(segments):
        dist2 = [np.min((seg.vertices[:, 0] - r_center) ** 2 + (seg.vertices[:, 1] - z_center) ** 2) for seg in segments]
        verts = segments[np.argmin(dist2)].vertices
        # Interpolate along the path to find Bz = 0
        bzpathi = interpolate.interp2d(r, z, bz)
        bzpath = [bzpathi(verts[i, 0], verts[i, 1])[0] for i in range(len(verts[:, 0]))]
        rx = float(interpolate.interp1d(bzpath, verts[:, 0], bounds_error=False, fill_value=np.NaN)(0))
        zx = float(interpolate.interp1d(bzpath, verts[:, 1], bounds_error=False, fill_value=np.NaN)(0))
    else:
        rx = zx = np.NaN

    return np.array([rx, zx])


############################
# G-FILE CLASS OMFITgeqdsk #
############################
class OMFITgeqdsk(SortedDict, OMFITascii):
    r"""
    class used to interface G files generated by EFIT

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """
    transform_signals = {
        'SIMAG': 'PSI',
        'SIBRY': 'PSI',
        'BCENTR': 'BT',
        'CURRENT': 'IP',
        'FPOL': 'BT',
        'FFPRIM': 'dPSI',
        'PPRIME': 'dPSI',
        'PSIRZ': 'PSI',
        'QPSI': 'Q',
    }

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self, caseInsensitive=True)
        self._cocos = 1
        self._AuxNamelistString = None
        self.dynaLoad = True

    def __getattr__(self, attr):
        try:
            return SortedDict.__getattr__(self, attr)
        except Exception:
            raise AttributeError('bad attribute `%s`' % attr)

    def surface_integral(self, *args, **kw):
        """
        Cross section integral of a quantity

        :param what: quantity to be integrated specified as array at flux surface

        :return: array of the integration from core to edge
        """
        return self['fluxSurfaces'].surface_integral(*args, **kw)

    def volume_integral(self, *args, **kw):
        """
        Volume integral of a quantity

        :param what: quantity to be integrated specified as array at flux surface

        :return: array of the integration from core to edge
        """
        return self['fluxSurfaces'].volume_integral(*args, **kw)

    def surfAvg(self, Q, interp='linear'):
        """
        Flux surface averaging of a quantity at each flux surface

        :param Q: 2D quantity to do the flux surface averaging (either 2D array or string from 'AuxQuantities', e.g. RHORZ)

        :param interp: interpolation method ['linear','quadratic','cubic']

        :return: array of the quantity fluxs surface averaged for each flux surface

        >> OMFIT['test']=OMFITgeqdsk(OMFITsrc+"/../samples/g133221.01000")
        >> jpar=OMFIT['test'].surfAvg('Jpar')
        >> pyplot.plot(OMFIT['test']['rhovn'],jpar)
        """
        Z = self['AuxQuantities']['Z']
        R = self['AuxQuantities']['R']
        if isinstance(Q, str):
            Q = self['AuxQuantities'][Q]
        if callable(Q):
            avg_function = Q
        else:

            def avg_function(r, z):
                return RectBivariateSplineNaN(Z, R, Q, kx=interp, ky=interp).ev(z, r)

        if interp == 'linear':
            interp = 1
        elif interp == 'quadratic':
            interp = 2
        elif interp == 'cubic':
            interp = 3

        return self['fluxSurfaces'].surfAvg(avg_function)

    @property
    @dynaLoad
    def cocos(self):
        """
        Return COCOS of current gEQDSK as represented in memory
        """
        if self._cocos is None:
            return self.native_cocos()
        return self._cocos

    @cocos.setter
    def cocos(self, value):
        raise OMFITexception("gEQDSK COCOS should not be defined via .cocos property: use .cocosify() method")

    @dynaLoad
    def load(self, raw=False, add_aux=True):
        """
        Method used to read g-files
        :param raw: bool
            load gEQDSK exactly as it's on file, regardless of COCOS
        :param add_aux: bool
            Add AuxQuantities and fluxSurfaces when using `raw` mode. When not raw, these will be loaded regardless.
        """

        if self.filename is None or not os.stat(self.filename).st_size:
            return

        # todo should be rewritten using FortranRecordReader
        # based on w3.pppl.gov/ntcc/TORAY/G_EQDSK.pdf
        def splitter(inv, step=16):
            value = []
            for k in range(len(inv) // step):
                value.append(inv[step * k : step * (k + 1)])
            return value

        def merge(inv):
            if not len(inv):
                return ''
            if len(inv[0]) > 80:
                # SOLPS gEQDSK files add spaces between numbers
                # and positive numbers are preceeded by a +
                return (''.join(inv)).replace(' ', '')
            else:
                return ''.join(inv)

        self.clear()

        # clean lines from the carriage returns
        with open(self.filename, 'r') as f:
            EQDSK = f.read().splitlines()

        # first line is description and sizes
        self['CASE'] = np.array(splitter(EQDSK[0][0:48], 8))
        try:
            tmp = list([_f for _f in EQDSK[0][48:].split(' ') if _f])
            [IDUM, self['NW'], self['NH']] = list(map(int, tmp[:3]))
        except ValueError:  # Can happen if no space between numbers, such as 10231023
            IDUM = int(EQDSK[0][48:52])
            self['NW'] = int(EQDSK[0][52:56])
            self['NH'] = int(EQDSK[0][56:60])
            tmp = []
            printd('IDUM, NW, NH', IDUM, self['NW'], self['NH'], topic='OMFITgeqdsk.load')
        if len(tmp) > 3:
            self['EXTRA_HEADER'] = EQDSK[0][49 + len(re.findall('%d +%d +%d ' % (IDUM, self['NW'], self['NH']), EQDSK[0][49:])[0]) + 2 :]
        offset = 1

        # now, the next 20 numbers (5 per row)

        # fmt: off
        [self['RDIM'], self['ZDIM'], self['RCENTR'], self['RLEFT'], self['ZMID'],
         self['RMAXIS'], self['ZMAXIS'], self['SIMAG'], self['SIBRY'], self['BCENTR'],
         self['CURRENT'], self['SIMAG'], XDUM, self['RMAXIS'], XDUM,
         self['ZMAXIS'], XDUM, self['SIBRY'], XDUM, XDUM] = list(map(eval, splitter(merge(EQDSK[offset:offset + 4]))))
        # fmt: on
        offset = offset + 4

        # now I have to read NW elements
        nlNW = int(np.ceil(self['NW'] / 5.0))
        self['FPOL'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
        offset = offset + nlNW
        self['PRES'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
        offset = offset + nlNW
        self['FFPRIM'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
        offset = offset + nlNW
        self['PPRIME'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
        offset = offset + nlNW
        try:
            # official gEQDSK file format saves PSIRZ as a single flat array of size rowsXcols
            nlNWNH = int(np.ceil(self['NW'] * self['NH'] / 5.0))
            self['PSIRZ'] = np.reshape(
                np.fromiter(splitter(merge(EQDSK[offset : offset + nlNWNH])), dtype=np.float64)[: self['NH'] * self['NW']],
                (self['NH'], self['NW']),
            )
            offset = offset + nlNWNH
        except ValueError:
            # sometimes gEQDSK files save row by row of the PSIRZ grid (eg. FIESTA code)
            nlNWNH = self['NH'] * nlNW
            self['PSIRZ'] = np.reshape(
                np.fromiter(splitter(merge(EQDSK[offset : offset + nlNWNH])), dtype=np.float64)[: self['NH'] * self['NW']],
                (self['NH'], self['NW']),
            )
            offset = offset + nlNWNH
        self['QPSI'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
        offset = offset + nlNW

        # now vacuum vessel and limiters
        self['NBBBS'], self['LIMITR'] = list(map(int, [_f for _f in EQDSK[offset : offset + 1][0].split(' ') if _f][:2]))
        offset = offset + 1

        nlNBBBS = int(np.ceil(self['NBBBS'] * 2 / 5.0))
        self['RBBBS'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNBBBS]))))[0::2])[: self['NBBBS']]
        self['ZBBBS'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNBBBS]))))[1::2])[: self['NBBBS']]
        offset = offset + max(nlNBBBS, 1)

        try:
            # this try/except is to handle some gEQDSK files written by older versions of ONETWO
            nlLIMITR = int(np.ceil(self['LIMITR'] * 2 / 5.0))
            self['RLIM'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlLIMITR]))))[0::2])[: self['LIMITR']]
            self['ZLIM'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlLIMITR]))))[1::2])[: self['LIMITR']]
            offset = offset + nlLIMITR
        except ValueError:
            # if it fails make the limiter as a rectangle around the plasma boundary that does not exceed the computational domain
            self['LIMITR'] = 5
            dd = self['RDIM'] / 10.0
            R = np.linspace(0, self['RDIM'], 2) + self['RLEFT']
            Z = np.linspace(0, self['ZDIM'], 2) - self['ZDIM'] / 2.0 + self['ZMID']
            self['RLIM'] = np.array(
                [
                    max([R[0], np.min(self['RBBBS']) - dd]),
                    min([R[1], np.max(self['RBBBS']) + dd]),
                    min([R[1], np.max(self['RBBBS']) + dd]),
                    max([R[0], np.min(self['RBBBS']) - dd]),
                    max([R[0], np.min(self['RBBBS']) - dd]),
                ]
            )
            self['ZLIM'] = np.array(
                [
                    max([Z[0], np.min(self['ZBBBS']) - dd]),
                    max([Z[0], np.min(self['ZBBBS']) - dd]),
                    min([Z[1], np.max(self['ZBBBS']) + dd]),
                    min([Z[1], np.max(self['ZBBBS']) + dd]),
                    max([Z[0], np.min(self['ZBBBS']) - dd]),
                ]
            )

        try:
            [self['KVTOR'], self['RVTOR'], self['NMASS']] = list(map(float, [_f for _f in EQDSK[offset : offset + 1][0].split(' ') if _f]))
            offset = offset + 1

            if self['KVTOR'] > 0:
                self['PRESSW'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
                offset = offset + nlNW
                self['PWPRIM'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
                offset = offset + nlNW

            if self['NMASS'] > 0:
                self['DMION'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
                offset = offset + nlNW

            self['RHOVN'] = np.array(list(map(float, splitter(merge(EQDSK[offset : offset + nlNW])))))
            offset = offset + nlNW
        except Exception:
            pass

        # add RHOVN if missing
        if 'RHOVN' not in self or not len(self['RHOVN']) or not np.sum(self['RHOVN']):
            self.add_rhovn()

        # fix some gEQDSK files that do not fill PRES info (eg. EAST)
        if not np.sum(self['PRES']):
            pres = integrate.cumtrapz(self['PPRIME'], np.linspace(self['SIMAG'], self['SIBRY'], len(self['PPRIME'])), initial=0)
            self['PRES'] = pres - pres[-1]

        # parse auxiliary namelist
        self.addAuxNamelist()

        if raw and add_aux:
            # add AuxQuantities and fluxSurfaces
            self.addAuxQuantities()
            self.addFluxSurfaces(**self.OMFITproperties)
        elif not raw:
            # Convert tree representation to COCOS 1
            self._cocos = self.native_cocos()
            self.cocosify(1, calcAuxQuantities=True, calcFluxSurfaces=True)

    @dynaSave
    def save(self, raw=False):
        """
        Method used to write g-files

        :param raw: save gEQDSK exactly as it's in the the tree, regardless of COCOS
        """

        # Change gEQDSK to its native COCOS before saving
        if not raw:
            original = self.cocos
            native = self.native_cocos()
            self.cocosify(native, calcAuxQuantities=False, calcFluxSurfaces=False)
        try:
            XDUM = 0.0
            IDUM = 0
            f2000 = fortranformat.FortranRecordWriter('6a8,3i4')
            f2020 = fortranformat.FortranRecordWriter('5e16.9')
            f2020NaN = fortranformat.FortranRecordWriter('5a16')
            f2022 = fortranformat.FortranRecordWriter('2i5')
            f2024 = fortranformat.FortranRecordWriter('i5,e16.9,i5')
            tmps = f2000.write(
                [
                    self['CASE'][0],
                    self['CASE'][1],
                    self['CASE'][2],
                    self['CASE'][3],
                    self['CASE'][4],
                    self['CASE'][5],
                    IDUM,
                    self['NW'],
                    self['NH'],
                ]
            )
            if 'EXTRA_HEADER' in self:
                tmps += ' ' + self['EXTRA_HEADER']
            tmps += '\n'
            tmps += f2020.write([self['RDIM'], self['ZDIM'], self['RCENTR'], self['RLEFT'], self['ZMID']]) + '\n'
            tmps += f2020.write([self['RMAXIS'], self['ZMAXIS'], self['SIMAG'], self['SIBRY'], self['BCENTR']]) + '\n'
            tmps += f2020.write([self['CURRENT'], self['SIMAG'], XDUM, self['RMAXIS'], XDUM]) + '\n'
            tmps += f2020.write([self['ZMAXIS'], XDUM, self['SIBRY'], XDUM, XDUM]) + '\n'
            tmps += f2020.write(self['FPOL']) + '\n'
            tmps += f2020.write(self['PRES']) + '\n'
            tmps += f2020.write(self['FFPRIM']) + '\n'
            tmps += f2020.write(self['PPRIME']) + '\n'
            psirz = list(['%16.9e' % x for x in self['PSIRZ'].flatten()])
            for p in range(4, int(self['NW'] * self['NH']) - 1, 5):
                psirz[p] = psirz[p] + '\n'
            tmps += ''.join(psirz) + '\n'
            tmps += f2020.write(self['QPSI']) + '\n'
            tmps += f2022.write([self['NBBBS'], self['LIMITR']]) + '\n'
            tmps += f2020.write(list((np.transpose([self['RBBBS'], self['ZBBBS']])).flatten())) + '\n'
            tmps += f2020.write(list((np.transpose([self['RLIM'], self['ZLIM']])).flatten())) + '\n'
            if 'KVTOR' in self and 'RVTOR' in self and 'NMASS' in self:
                tmps += f2024.write([self['KVTOR'], self['RVTOR'], self['NMASS']]) + '\n'
                if self['KVTOR'] > 0 and 'PRESSW' in self and 'PWPRIM' in self:
                    tmps += f2020.write(self['PRESSW']) + '\n'
                    tmps += f2020.write(self['PWPRIM']) + '\n'
                if self['NMASS'] > 0 and 'DMION' in self:
                    try:
                        tmps += f2020.write(self['DMION']) + '\n'
                    except Exception:
                        tmps += f2020NaN.write(map(str, self['DMION'])) + '\n'
                if 'RHOVN' in self:
                    tmps += f2020.write(self['RHOVN']) + '\n'
            tmps += '    0\n'

            # write file
            with open(self.filename, 'w') as f:
                f.write(tmps)
                if 'AuxNamelist' in self and self['AuxNamelist'].dynaLoad:
                    if self._AuxNamelistString is not None:
                        f.write(self._AuxNamelistString)
                    else:
                        self['AuxNamelist'].save(f)
        finally:
            if not raw:
                # Return gEQDSK to the original COCOS
                self.cocosify(original, calcAuxQuantities=False, calcFluxSurfaces=False)

    def cocosify(self, cocosnum, calcAuxQuantities, calcFluxSurfaces, inplace=True):
        """
        Method used to convert gEQDSK quantities to desired COCOS

        :param cocosnum: desired COCOS number (1-8, 11-18)

        :param calcAuxQuantities: add AuxQuantities based on new cocosnum

        :param calcFluxSurfaces: add fluxSurfaces based on new cocosnum

        :param inplace:  change values in True: current gEQDSK, False: new gEQDSK

        :return: gEQDSK with proper cocos
        """

        if inplace:
            gEQDSK = self
        else:
            gEQDSK = copy.deepcopy(self)

        if self.cocos != cocosnum:

            # how different gEQDSK quantities should transform
            transform = cocos_transform(self.cocos, cocosnum)

            # transform the gEQDSK quantities appropriately
            for key in self:
                if key in list(self.transform_signals.keys()):
                    gEQDSK[key] = transform[self.transform_signals[key]] * self[key]

        # set the COCOS attribute of the gEQDSK
        gEQDSK._cocos = cocosnum

        # recalculate AuxQuantities and fluxSurfaces if necessary
        if calcAuxQuantities:
            gEQDSK.addAuxQuantities()
        if calcFluxSurfaces:
            gEQDSK.addFluxSurfaces(**self.OMFITproperties)

        return gEQDSK

    def native_cocos(self):
        """
        Returns the native COCOS that an unmodified gEQDSK would obey, defined by sign(Bt) and sign(Ip)
        In order for psi to increase from axis to edge and for q to be positive:
        All use sigma_RpZ=+1 (phi is counterclockwise) and exp_Bp=0 (psi is flux/2.*pi)
        We want
        sign(psi_edge-psi_axis) = sign(Ip)*sigma_Bp > 0  (psi always increases in gEQDSK)
        sign(q) = sign(Ip)*sign(Bt)*sigma_rhotp > 0      (q always positive in gEQDSK)
        ::
            ============================================
            Bt    Ip    sigma_Bp    sigma_rhotp    COCOS
            ============================================
            +1    +1       +1           +1           1
            +1    -1       -1           -1           3
            -1    +1       +1           -1           5
            -1    -1       -1           +1           7
        """
        try:
            return gEQDSK_COCOS_identify(self['BCENTR'], self['CURRENT'])
        except Exception as _excp:
            printe("Assuming COCOS=1: " + repr(_excp))
            return 1

    def flip_Bt_Ip(self):
        """
        Flip direction of the magnetic field and current without changing COCOS
        """
        cocosnum = self.cocos
        # artificially flip phi to the opposite direction
        if np.mod(cocosnum, 2) == 0:
            self._cocos -= 1
        elif np.mod(cocosnum, 2) == 1:
            self._cocos += 1
        # change back to original COCOS, flipping phi & all relevant quantities
        self.cocosify(cocosnum, calcAuxQuantities=True, calcFluxSurfaces=True)

    def flip_ip(self):
        """
        Flip sign of IP and related quantities without changing COCOS
        """
        for key in self:
            if self.transform_signals.get(key, None) in ['PSI', 'IP', 'dPSI', 'Q']:
                self[key] = -self[key]
        self.addAuxQuantities()
        self.addFluxSurfaces(**self.OMFITproperties)

    def flip_bt(self):
        """
        Flip sign of BT and related quantities without changing COCOS
        """
        for key in self:
            if self.transform_signals.get(key, None) in ['BT', 'Q']:
                self[key] = -self[key]
        self.addAuxQuantities()
        self.addFluxSurfaces(**self.OMFITproperties)

    def combineGEQDSK(self, other, alpha):
        """
        Method used to linearly combine current equilibrium (eq1) with other g-file
        All quantities are linearly combined, except 'RBBBS','ZBBBS','NBBBS','LIMITR','RLIM','ZLIM','NW','NH'
        OMFIT['eq3']=OMFIT['eq1'].combineGEQDSK(OMFIT['eq2'],alpha)
        means:
        eq3=alpha*eq1+(1-alpha)*eq2

        :param other: g-file for eq2

        :param alpha: linear combination parameter

        :return: g-file for eq3
        """
        out = copy.deepcopy(self)

        # gEQDSKs need to be in the same COCOS to combine
        if self.cocos != other.cocos:
            # change other to self's COCOS, but don't modify other
            eq2 = other.cocosify(self.cocos, calcAuxQuantities=True, calcFluxSurfaces=True, inplace=False)
        else:
            eq2 = other

        keys_self = set(self.keys())
        keys_other = set(self.keys())
        keys_ignore = set(['RBBBS', 'ZBBBS', 'NBBBS', 'LIMITR', 'RLIM', 'ZLIM', 'NW', 'NH'])
        keys = keys_self.intersection(keys_other).difference(keys_ignore)
        for key in keys:
            if is_numlike(self[key]) and is_numlike(eq2[key]):
                out[key] = alpha * self[key] + (1.0 - alpha) * eq2[key]

        # combine the separatrix
        t_self = np.arctan2(self['ZBBBS'] - self['ZMAXIS'], self['RBBBS'] - self['RMAXIS'])
        t_other = np.arctan2(
            eq2['ZBBBS'] - self['ZMAXIS'], eq2['RBBBS'] - self['RMAXIS']
        )  # must be defined with respect to the same center
        for key in ['RBBBS', 'ZBBBS']:
            out[key] = alpha * self[key] + interp1dPeriodic(t_other, eq2[key])(t_self) * (1 - alpha)

        out.addAuxQuantities()
        out.addFluxSurfaces()

        return out

    def addAuxNamelist(self):
        """
        Adds ['AuxNamelist'] to the current object

        :return: Namelist object containing auxiliary quantities
        """
        if self.filename is None or not os.stat(self.filename).st_size:
            self['AuxNamelist'] = namelist.NamelistFile(input_string='')
            return self['AuxNamelist']
        self['AuxNamelist'] = namelist.NamelistFile(self.filename, nospaceIsComment=True, retain_comments=False, skip_to_symbol='&')
        self._AuxNamelistString = None
        tmp = self.read()
        self._AuxNamelistString = tmp[tmp.find('&') :]
        return self['AuxNamelist']

    def delAuxNamelist(self):
        """
        Removes ['AuxNamelist'] from the current object
        """
        self._AuxNamelistString = None
        self.safe_del('AuxNamelist')
        return

    def addAuxQuantities(self):
        """
        Adds ['AuxQuantities'] to the current object

        :return: SortedDict object containing auxiliary quantities
        """

        self['AuxQuantities'] = self._auxQuantities()

        return self['AuxQuantities']

    def fourier(self, surface=1.0, nf=128, symmetric=True, resolution=2, **kw):
        r"""
        Reconstructs Fourier decomposition of the boundary for fixed boundary codes to use

        :param surface: Use this normalised flux surface for the boundary (if <0 then original gEQDSK BBBS boundary is used), else the flux surfaces are from FluxSurfaces.

        :param nf: number of Fourier modes

        :param symmetric: return symmetric boundary

        :param resolution: FluxSurfaces resolution factor

        :param \**kw: additional keyword arguments are passed to FluxSurfaces.findSurfaces
        """

        if surface < 0:
            rb = self['RBBBS']
            zb = self['ZBBBS']
        else:
            flx = copy.deepcopy(self['fluxSurfaces'])
            kw.setdefault('map', None)
            flx.changeResolution(resolution)
            flx.findSurfaces(np.linspace(surface - 0.01, surface, 3), **kw)
            rb = flx['flux'][1]['R']
            zb = flx['flux'][1]['Z']
        bndfour = fourier_boundary(nf, rb, zb, symmetric=symmetric)
        fm = np.zeros(nf)
        if symmetric:
            fm = bndfour.realfour
        else:
            fm[0::2] = bndfour.realfour
            fm[1::2] = bndfour.imagfour
        amin = bndfour.amin
        r0 = bndfour.r0
        return (bndfour, fm, amin, r0)

    def _auxQuantities(self):
        """
        Calculate auxiliary quantities based on the g-file equilibria
        These AuxQuantities obey the COCOS of self.cocos so some sign differences from the gEQDSK file itself

        :return: SortedDict object containing some auxiliary quantities
        """

        aux = SortedDict()
        iterpolationType = 'linear'  # note that interpolation should not be oscillatory -> use linear or pchip

        aux['R'] = np.linspace(0, self['RDIM'], self['NW']) + self['RLEFT']
        aux['Z'] = np.linspace(0, self['ZDIM'], self['NH']) - self['ZDIM'] / 2.0 + self['ZMID']

        if self['CURRENT'] != 0.0:

            # poloidal flux and normalized poloidal flux
            aux['PSI'] = np.linspace(self['SIMAG'], self['SIBRY'], len(self['PRES']))
            aux['PSI_NORM'] = np.linspace(0.0, 1.0, len(self['PRES']))

            aux['PSIRZ'] = self['PSIRZ']
            if self['SIBRY'] != self['SIMAG']:
                aux['PSIRZ_NORM'] = abs((self['PSIRZ'] - self['SIMAG']) / (self['SIBRY'] - self['SIMAG']))
            else:
                aux['PSIRZ_NORM'] = abs(self['PSIRZ'] - self['SIMAG'])
            # rho poloidal
            aux['RHOp'] = np.sqrt(aux['PSI_NORM'])
            aux['RHOpRZ'] = np.sqrt(aux['PSIRZ_NORM'])

            # extend functions in PSI to be clamped at edge value when outside of PSI range (i.e. outside of LCFS)
            dp = aux['PSI'][1] - aux['PSI'][0]
            ext_psi_mesh = np.hstack((aux['PSI'][0] - dp * 1e6, aux['PSI'], aux['PSI'][-1] + dp * 1e6))

            def ext_arr(inv):
                return np.hstack((inv[0], inv, inv[-1]))

            # map functions in PSI to RZ coordinate
            for name in ['FPOL', 'PRES', 'QPSI', 'FFPRIM', 'PPRIME', 'PRESSW', 'PWPRIM']:
                if name in self:
                    aux[name + 'RZ'] = interpolate.interp1d(ext_psi_mesh, ext_arr(self[name]), kind=iterpolationType, bounds_error=False)(
                        aux['PSIRZ']
                    )

            # Correct Pressure by rotation term (eq 26 & 30 of Lao et al., FST 48.2 (2005): 968-977.
            aux['PRES0RZ'] = copy.deepcopy(aux['PRESRZ'])
            if 'PRESSW' in self:
                aux['PRES0RZ'] = copy.deepcopy(aux['PRESRZ'])
                aux['PPRIME0RZ'] = PP0 = copy.deepcopy(aux['PPRIMERZ'])
                R = aux['R'][None, :]
                R0 = self['RCENTR']
                Pw = aux['PRESSWRZ']
                P0 = aux['PRES0RZ']
                aux['PRESRZ'] = P = P0 * np.exp(Pw / P0 * (R - R0) / R0)
                PPw = aux['PWPRIMRZ']
                aux['PPRIMERZ'] = PP0 * P / P0 * (1.0 - Pw / P0 * (R ** 2 - R0 ** 2) / R0 ** 2)
                aux['PPRIMERZ'] += PPw * P / P0 * (R ** 2 - R0 ** 2) / R0 ** 2

        else:
            # vacuum gEQDSK
            aux['PSIRZ'] = self['PSIRZ']

        # from the definition of flux
        COCOS = define_cocos(self.cocos)
        if (aux['Z'][1] != aux['Z'][0]) and (aux['R'][1] != aux['R'][0]):
            [dPSIdZ, dPSIdR] = np.gradient(aux['PSIRZ'], aux['Z'][1] - aux['Z'][0], aux['R'][1] - aux['R'][0])
        else:
            [dPSIdZ, dPSIdR] = np.gradient(aux['PSIRZ'])
        [R, Z] = np.meshgrid(aux['R'], aux['Z'])
        aux['Br'] = (dPSIdZ / R) * COCOS['sigma_RpZ'] * COCOS['sigma_Bp'] / (2.0 * np.pi) ** COCOS['exp_Bp']
        aux['Bz'] = (-dPSIdR / R) * COCOS['sigma_RpZ'] * COCOS['sigma_Bp'] / (2.0 * np.pi) ** COCOS['exp_Bp']
        if self['CURRENT'] != 0.0:
            signTheta = COCOS['sigma_RpZ'] * COCOS['sigma_rhotp']  # + CW, - CCW
            signBp = signTheta * np.sign((Z - self['ZMAXIS']) * aux['Br'] - (R - self['RMAXIS']) * aux['Bz'])  # sign(theta)*sign(r x B)
            aux['Bp'] = signBp * np.sqrt(aux['Br'] ** 2 + aux['Bz'] ** 2)
            # once I have the poloidal flux as a function of RZ I can calculate the toroidal field (showing DIA/PARAmagnetism)
            aux['Bt'] = aux['FPOLRZ'] / R
        else:
            aux['Bt'] = self['BCENTR'] * self['RCENTR'] / R

        # now the current densities as curl B = mu0 J in cylindrical coords
        if (aux['Z'][2] != aux['Z'][1]) and (aux['R'][2] != aux['R'][1]):
            [dBrdZ, dBrdR] = np.gradient(aux['Br'], aux['Z'][2] - aux['Z'][1], aux['R'][2] - aux['R'][1])
            [dBzdZ, dBzdR] = np.gradient(aux['Bz'], aux['Z'][2] - aux['Z'][1], aux['R'][2] - aux['R'][1])
            [dBtdZ, dBtdR] = np.gradient(aux['Bt'], aux['Z'][2] - aux['Z'][1], aux['R'][2] - aux['R'][1])
            [dRBtdZ, dRBtdR] = np.gradient(R * aux['Bt'], aux['Z'][2] - aux['Z'][1], aux['R'][2] - aux['R'][1])
        else:
            [dBrdZ, dBrdR] = np.gradient(aux['Br'])
            [dBzdZ, dBzdR] = np.gradient(aux['Bz'])
            [dBtdZ, dBtdR] = np.gradient(aux['Bt'])
            [dRBtdZ, dRBtdR] = np.gradient(R * aux['Bt'])

        aux['Jr'] = COCOS['sigma_RpZ'] * (-dBtdZ) / (4 * np.pi * 1e-7)
        aux['Jz'] = COCOS['sigma_RpZ'] * (dRBtdR / R) / (4 * np.pi * 1e-7)
        aux['Jt'] = COCOS['sigma_RpZ'] * (dBrdZ - dBzdR) / (4 * np.pi * 1e-7)
        if self['CURRENT'] != 0.0:
            signJp = signTheta * np.sign((Z - self['ZMAXIS']) * aux['Jr'] - (R - self['RMAXIS']) * aux['Jz'])  # sign(theta)*sign(r x J)
            aux['Jp'] = signJp * np.sqrt(aux['Jr'] ** 2 + aux['Jz'] ** 2)
            aux['Jt_fb'] = (
                -COCOS['sigma_Bp'] * ((2.0 * np.pi) ** COCOS['exp_Bp']) * (aux['PPRIMERZ'] * R + aux['FFPRIMRZ'] / R / (4 * np.pi * 1e-7))
            )

            aux['Jpar'] = (aux['Jr'] * aux['Br'] + aux['Jz'] * aux['Bz'] + aux['Jt'] * aux['Bt']) / np.sqrt(
                aux['Br'] ** 2 + aux['Bz'] ** 2 + aux['Bt'] ** 2
            )

            # The toroidal flux PHI can be found by recognizing that the safety factor is the ratio of the differential toroidal and poloidal fluxes
            aux['PHI'] = (
                COCOS['sigma_Bp']
                * COCOS['sigma_rhotp']
                * integrate.cumtrapz(self['QPSI'], aux['PSI'], initial=0)
                * (2.0 * np.pi) ** (1.0 - COCOS['exp_Bp'])
            )
            if aux['PHI'][-1] != 0 and np.isfinite(aux['PHI'][-1]):
                aux['PHI_NORM'] = aux['PHI'] / aux['PHI'][-1]
            else:
                aux['PHI_NORM'] = aux['PHI'] * np.NaN
                printw('Warning: unable to properly normalize PHI')
            if abs(np.diff(aux['PSI'])).min() > 0:
                aux['PHIRZ'] = interpolate.interp1d(
                    aux['PSI'], aux['PHI'], kind=iterpolationType, bounds_error=False, fill_value='extrapolate'
                )(aux['PSIRZ'])
            else:
                aux['PHIRZ'] = aux['PSIRZ'] * np.NaN
            if self['BCENTR'] != 0:
                aux['RHOm'] = float(np.sqrt(abs(aux['PHI'][-1] / np.pi / self['BCENTR'])))
            else:
                aux['RHOm'] = np.NaN
            aux['RHO'] = np.sqrt(aux['PHI_NORM'])
            with np.errstate(invalid='ignore'):
                aux['RHORZ'] = np.nan_to_num(np.sqrt(aux['PHIRZ'] / aux['PHI'][-1]))

        aux['Rx1'], aux['Zx1'] = x_point_search(aux['R'], aux['Z'], self['PSIRZ'], psi_boundary=self['SIBRY'])
        aux['Rx2'], aux['Zx2'] = x_point_search(aux['R'], aux['Z'], self['PSIRZ'], zsign=-np.sign(aux['Zx1']))

        return aux

    def addFluxSurfaces(self, **kw):
        r"""
        Adds ['fluxSurface'] to the current object

        :param \**kw: keyword dictionary passed to fluxSurfaces class

        :return: fluxSurfaces object based on the current gEQDSK file
        """
        if self['CURRENT'] == 0.0:
            printw('Skipped tracing of fluxSurfaces for vacuum equilibrium')
            return

        options = {}
        options.update(kw)
        options['quiet'] = kw.pop('quiet', self['NW'] <= 129)
        options['levels'] = kw.pop('levels', True)
        options['resolution'] = kw.pop('resolution', 0)
        options['calculateAvgGeo'] = kw.pop('calculateAvgGeo', True)

        # N.B., the middle option accounts for the new version of CHEASE
        #       where self['CASE'][1] = 'OM CHEAS'
        if (
            self['CASE'] is not None
            and self['CASE'][0] is not None
            and self['CASE'][1] is not None
            and ('CHEASE' in self['CASE'][0] or 'CHEAS' in self['CASE'][1] or 'TRXPL' in self['CASE'][0])
        ):
            options['forceFindSeparatrix'] = kw.pop('forceFindSeparatrix', False)
        else:
            options['forceFindSeparatrix'] = kw.pop('forceFindSeparatrix', True)

        try:
            self['fluxSurfaces'] = fluxSurfaces(gEQDSK=self, **options)
        except Exception as _excp:
            warnings.warn('Error tracing flux surfaces: ' + repr(_excp))
            self['fluxSurfaces'] = OMFITerror('Error tracing flux surfaces: ' + repr(_excp))

        return self['fluxSurfaces']

    def calc_masks(self):
        """
        Calculate grid masks for limiters, vessel, core and edge plasma

        :return: SortedDict object with 2D maps of masks
        """
        import matplotlib

        if 'AuxQuantities' not in self:
            aux = self._auxQuantities()
        else:
            aux = self['AuxQuantities']
        [R, Z] = np.meshgrid(aux['R'], aux['Z'])
        masks = SortedDict()
        # masking
        limiter_path = matplotlib.path.Path(np.transpose(np.array([self['RLIM'], self['ZLIM']])))
        masks['limiter_mask'] = 1 - np.reshape(
            np.array(list(map(limiter_path.contains_point, list(map(tuple, np.transpose(np.array([R.flatten(), Z.flatten()]))))))),
            (self['NW'], self['NH']),
        )
        masks['vessel_mask'] = 1 - masks['limiter_mask']
        plasma_path = matplotlib.path.Path(np.transpose(np.array([self['RBBBS'], self['ZBBBS']])))
        masks['core_plasma_mask'] = np.reshape(
            np.array(list(map(plasma_path.contains_point, list(map(tuple, np.transpose(np.array([R.flatten(), Z.flatten()]))))))),
            (self['NW'], self['NH']),
        )
        masks['edge_plasma_mask'] = (1 - masks['limiter_mask']) - masks['core_plasma_mask']
        for vname in [_f for _f in [re.findall(r'.*masks', value) for value in list(aux.keys())] if _f]:
            aux[vname[0]] = np.array(aux[vname[0]], float)
            aux[vname[0]][aux[vname[0]] == 0] = np.nan
        return masks

    def plot(
        self,
        usePsi=False,
        only1D=False,
        only2D=False,
        top2D=False,
        q_contour_n=0,
        label_contours=False,
        levels=None,
        mask_vessel=True,
        show_limiter=True,
        xlabel_in_legend=False,
        **kw,
    ):
        r"""
        Function used to plot g-files. This plot shows flux surfaces in the vessel, pressure, q profiles, P' and FF'

        :param usePsi: In the plots, use psi instead of rho, or both

        :param only1D: only make plofile plots

        :param only2D: only make flux surface plot

        :param top2D: Plot top-view 2D cross section

        :param q_contour_n: If above 0, plot q contours in 2D plot corresponding to rational surfaces of the given n

        :param label_contours: Adds labels to 2D contours

        :param levels: list of sorted numeric values to pass to 2D plot as contour levels

        :param mask_vessel: mask contours with vessel

        :param show_limiter: Plot the limiter outline in (R,Z) 2D plots

        :param xlabel_in_legend: Show x coordinate in legend instead of under axes (usefull for overplots with psi and rho)

        :param label: plot item label to apply lines in 1D plots (only the q plot has legend called by the geqdsk class
            itself) and to the boundary contour in the 2D plot (this plot doesn't call legend by itself)

        :param ax: Axes instance to plot in when using only2D

        :param \**kw: Standard plot keywords (e.g. color, linewidth) will be passed to Axes.plot() calls.
        """
        import matplotlib

        # backward compatibility: remove deprecated kw (not used anywhere in repo)
        garbage = kw.pop('contour_smooth', None)

        if sum(self['RHOVN']) == 0.0:
            usePsi = True

        def plot2D(what, ax, levels=levels, Z_in=None, **kw):
            if levels is None:
                if what in ['PHIRZ_NORM', 'RHOpRZ', 'RHORZ', 'PSIRZ_NORM']:
                    levels = np.r_[0.1:10:0.1]
                    label_levels = levels[:9]
                elif what in ['QPSIRZ']:
                    q1 = self['QPSI'][-2]  # go one in because edge can be jagged in contour and go outside seperatrix
                    q0 = self['QPSI'][0]
                    qsign = np.sign(q0)  # q profile can be negative depending on helicity
                    levels = np.arange(np.ceil(qsign * q0), np.floor(qsign * q1), 1.0 / int(q_contour_n))[:: int(qsign)] * qsign
                    label_levels = levels
                else:
                    levels = np.linspace(np.nanmin(self['AuxQuantities'][what]), np.nanmax(self['AuxQuantities'][what]), 20)
                    label_levels = levels
            else:
                label_levels = levels

            label = kw.pop('label', None)  # Take this out so the legend doesn't get spammed by repeated labels

            # use this to set up the plot key word args, get the next line color, and move the color cycler along
            (l,) = ax.plot(self['AuxQuantities']['R'], self['AuxQuantities']['R'] * np.nan, **kw)
            # contours
            cs = ax.contour(
                self['AuxQuantities']['R'],
                self['AuxQuantities']['Z'],
                self['AuxQuantities'][what],
                levels,
                colors=[l.get_color()] * len(levels),
                linewidths=l.get_linewidth(),
                alpha=l.get_alpha(),
                linestyles=l.get_linestyle(),
            )

            # optional labeling of contours
            if label_contours:
                label_step = max(len(label_levels) // 4, 1)
                ax.clabel(cs, label_levels[::label_step], inline=True, fontsize=8, fmt='%1.1f')

            # optional masking of contours outside of limiter surface
            if len(self['RLIM']) > 2 and mask_vessel and not np.any(np.isnan(self['RLIM'])) and not np.any(np.isnan(self['ZLIM'])):
                path = matplotlib.path.Path(np.transpose(np.array([self['RLIM'], self['ZLIM']])))
                patch = matplotlib.patches.PathPatch(path, facecolor='none')
                ax.add_patch(patch)
                for col in cs.collections:
                    col.set_clip_path(patch)

            # get the color
            kw1 = copy.copy(kw)
            kw1['linewidth'] = kw['linewidth'] + 1
            kw1.setdefault('color', ax.lines[-1].get_color())

            # boundary
            ax.plot(self['RBBBS'], self['ZBBBS'], label=label, **kw1)

            # magnetic axis
            ax.plot(self['RMAXIS'], self['ZMAXIS'], '+', **kw1)

            # limiter
            if len(self['RLIM']) > 2:
                if show_limiter:
                    ax.plot(self['RLIM'], self['ZLIM'], 'k', linewidth=2)

                try:
                    ax.axis([np.nanmin(self['RLIM']), np.nanmax(self['RLIM']), np.nanmin(self['ZLIM']), np.nanmax(self['ZLIM'])])
                except ValueError:
                    pass

            # aspect_ratio
            ax.set_aspect('equal')

        def plot2DTop(what, ax, levels=levels, Z_in=None, **kw):
            # If z_in is specified then plot a vertical slice else plot the outer and innermost R value of each flux surface
            if levels is None:
                if what in ['PHIRZ_NORM', 'RHOpRZ', 'RHORZ', 'PSIRZ_NORM']:
                    levels = np.r_[0.1:10:0.1]
                elif what in ['PHIRZ', 'PSIRZ']:
                    levels = np.linspace(np.nanmin(self['AuxQuantities'][what]), np.nanmax(self['AuxQuantities'][what]), 20)
                else:
                    raise ValueError(what + " is not supported for top view plot.")

            # use this to set up the plot key word args, get the next line color, and move the color cycler along
            (l,) = ax.plot(self['AuxQuantities']['R'], self['AuxQuantities']['R'] * np.nan, **kw)
            if Z_in is None:
                # Plots the outer and inner most points of a flux surface in topview
                what_sort = np.argsort(self['AuxQuantities'][what.replace("RZ", "")])
                psi_map = interpolate.interp1d(
                    self['AuxQuantities'][what.replace("RZ", "")][what_sort], self['AuxQuantities']['PSI'][what_sort]
                )
                psi_levels = []
                for level in levels:
                    if (level > np.min(self['AuxQuantities'][what.replace("RZ", "")])) and level < np.max(
                        self['AuxQuantities'][what.replace("RZ", "")]
                    ):
                        psi_levels.append(psi_map(level))
                psi_levels = np.asarray(psi_levels)
                psi_surf = np.zeros(len(self['fluxSurfaces']["flux"]) + 1)
                R_in = np.zeros(len(self['fluxSurfaces']["flux"]) + 1)
                R_out = np.zeros(len(self['fluxSurfaces']["flux"]) + 1)
                psi_surf[0] = self["SIMAG"]
                R_in[0] = self["RMAXIS"]
                R_out[0] = R_in[0]
                for iflux in range(len(self['fluxSurfaces']["flux"])):
                    psi_surf[iflux + 1] = self['fluxSurfaces']["flux"][iflux]["psi"]
                    R_in[iflux + 1] = np.max(self['fluxSurfaces']["flux"][iflux]["R"])
                    R_out[iflux + 1] = np.min(self['fluxSurfaces']["flux"][iflux]["R"])
                # In case of decreasing flux
                psi_sort = np.argsort(psi_surf)
                R_in_spl = interpolate.InterpolatedUnivariateSpline(psi_surf[psi_sort], R_in[psi_sort])
                R_out_spl = interpolate.InterpolatedUnivariateSpline(psi_surf[psi_sort], R_out[psi_sort])
                R_cont = R_in_spl(psi_levels)
                R_cont = np.sort(np.concatenate([R_cont, R_out_spl(psi_levels)]))
                # Boundary optional masking of contours outside of limiter surface and plotting boundary
                R_max = np.max(R_cont)
                R_min = np.min(R_cont)
                if len(self['RLIM']) > 2 and not np.any(np.isnan(self['RLIM'])):
                    R_vessel_in = np.min(self['RLIM'])
                    R_vessel_out = np.max(self['RLIM'])
                    if mask_vessel:
                        R_max = R_vessel_out
                        R_min = R_vessel_in
                    ax.add_patch(matplotlib.patches.Circle([0.0, 0.0], R_vessel_in, edgecolor='k', facecolor='none', linestyle="-"))
                    ax.add_patch(matplotlib.patches.Circle([0.0, 0.0], R_vessel_out, edgecolor='k', facecolor='none', linestyle="-"))
                for R in R_cont:
                    if R >= R_min and R <= R_max:
                        ax.add_patch(
                            matplotlib.patches.Circle(
                                [0.0, 0.0],
                                R,
                                edgecolor=l.get_color(),
                                linewidth=l.get_linewidth(),
                                linestyle=l.get_linestyle(),
                                facecolor='none',
                            )
                        )
                ax.add_patch(matplotlib.patches.Circle([0.0, 0.0], self["RMAXIS"], edgecolor='b', facecolor='none', linestyle="-"))
                if self["SIBRY"] < np.max(psi_surf):
                    R_sep_in = R_in_spl(self["SIBRY"])
                    R_sep_out = R_out_spl(self["SIBRY"])
                    ax.add_patch(matplotlib.patches.Circle([0.0, 0.0], R_sep_in, edgecolor='b', facecolor='none', linestyle="-"))
                    ax.add_patch(matplotlib.patches.Circle([0.0, 0.0], R_sep_out, edgecolor='b', facecolor='none', linestyle="-"))
            else:
                # Plots the R and z values of the wall and the choosen magnetic coordiante for a specific z level
                what_spl = interpolate.RectBivariateSpline(
                    self['AuxQuantities']['R'], self['AuxQuantities']['Z'], self['AuxQuantities'][what].T
                )
                R_cut = np.linspace(np.min(self['AuxQuantities']['R']), np.max(self['AuxQuantities']['R']), self["NW"])
                Z_cut = np.zeros(self["NW"])
                Z_cut[:] = Z_in
                what_cut = what_spl(R_cut, Z_cut, grid=False)
                R_max = -np.inf
                for level in levels:
                    root_spl = interpolate.InterpolatedUnivariateSpline(R_cut, what_cut - level)
                    roots = root_spl.roots()
                    if len(roots) == 2:
                        if np.max(roots) > R_max:
                            R_max = np.max(roots)
                        if level == 1.0:
                            ax.add_patch(
                                matplotlib.patches.Circle([0.0, 0.0], np.min(roots), edgecolor='b', facecolor='none', linestyle="-")
                            )
                            ax.add_patch(
                                matplotlib.patches.Circle([0.0, 0.0], np.max(roots), edgecolor='b', facecolor='none', linestyle="-")
                            )
                        else:
                            ax.add_patch(
                                matplotlib.patches.Circle(
                                    [0.0, 0.0],
                                    np.min(roots),
                                    edgecolor=l.get_color(),
                                    linewidth=l.get_linewidth(),
                                    linestyle=l.get_linestyle(),
                                    facecolor='none',
                                )
                            )
                            ax.add_patch(
                                matplotlib.patches.Circle(
                                    [0.0, 0.0],
                                    np.max(roots),
                                    edgecolor=l.get_color(),
                                    linewidth=l.get_linewidth(),
                                    linestyle=l.get_linestyle(),
                                    facecolor='none',
                                )
                            )
                s_wall = np.linspace(0, 1, len(self["RLIM"]))
                wall_R_spl = interpolate.InterpolatedUnivariateSpline(s_wall, self["RLIM"])
                wall_Z_root_spl = interpolate.InterpolatedUnivariateSpline(s_wall, self["ZLIM"] - Z_in)
                wall_roots = wall_Z_root_spl.roots()
                if len(wall_roots) < 2:
                    printw("WARNING in OMFITgeqdsk.plot2DTop: Did not find intersection with wall!")
                else:
                    if np.max(wall_R_spl(wall_roots)) > R_max:
                        R_max = np.max(wall_R_spl(wall_roots))
                    ax.add_patch(
                        matplotlib.patches.Circle(
                            [0.0, 0.0], np.min(wall_R_spl(wall_roots)), edgecolor='k', facecolor='none', linestyle="-"
                        )
                    )
                    ax.add_patch(
                        matplotlib.patches.Circle(
                            [0.0, 0.0], np.max(wall_R_spl(wall_roots)), edgecolor='k', facecolor='none', linestyle="-"
                        )
                    )
            ax.set_aspect('equal')
            ax.set_xlim(-R_max, R_max)
            ax.set_ylim(-R_max, R_max)

        kw.setdefault('linewidth', 1)

        if not only2D:
            fig = pyplot.gcf()
            kw.pop('ax', None)  # This option can't be used in this context, so remove it to avoid trouble.
            pyplot.subplots_adjust(wspace=0.23)

            if usePsi:
                xName = '$\\psi$'
                x = np.linspace(0, 1, len(self['PRES']))
            else:
                xName = '$\\rho$'
                if 'RHOVN' in self and np.sum(self['RHOVN']):
                    x = self['RHOVN']
                else:
                    x = self['AuxQuantities']['RHO']

            if 'label' not in kw:
                kw['label'] = (' '.join([a.strip() for a in self['CASE'][3:]])).strip()
                if not len(kw['label']):
                    kw['label'] = (' '.join([a.strip() for a in self['CASE']])).strip()
                    if not len(kw['label']):
                        kw['label'] = os.path.split(self.filename)[1]
            if xlabel_in_legend:
                kw['label'] += ' vs ' + xName

            ax = fig.add_subplot(232)
            ax.plot(x, self['PRES'], **kw)
            kw.setdefault('color', ax.lines[-1].get_color())
            ax.set_title(r'$\,$ Pressure')
            ax.ticklabel_format(style='sci', scilimits=(-1, 2), axis='y')
            pyplot.setp(ax.get_xticklabels(), visible=False)
            ax = fig.add_subplot(233, sharex=ax)
            ax.plot(x, self['QPSI'], **kw)
            ax.set_title('$q$ Safety Factor')
            ax.ticklabel_format(style='sci', scilimits=(-1, 2), axis='y')

            try:
                ax.legend(labelspacing=0.2, loc=0).draggable(state=True)
            except Exception:
                pass
            pyplot.setp(ax.get_xticklabels(), visible=False)

            ax = fig.add_subplot(235, sharex=ax)
            ax.plot(x, self['PPRIME'], **kw)
            ax.set_title(r"$P\,^\prime$ Source")
            ax.ticklabel_format(style='sci', scilimits=(-1, 2), axis='y')
            ax.set_xlabel((not xlabel_in_legend) * xName)

            ax = fig.add_subplot(236, sharex=ax)
            ax.plot(x, self['FFPRIM'], **kw)
            ax.set_title(r"$FF\,^\prime$ Source")
            ax.ticklabel_format(style='sci', scilimits=(-1, 2), axis='y')
            ax.set_xlabel((not xlabel_in_legend) * xName)

            ax = fig.add_subplot(131, aspect='equal')
            ax.set_frame_on(False)
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

        else:
            if 'ax' not in kw:
                ax = pyplot.gca()
            else:
                ax = kw.pop('ax')

        if not only1D:
            if top2D:
                plot2DTop('RHOpRZ', ax, **kw)
            elif q_contour_n > 0:
                plot2D('QPSIRZ', ax, **kw)
            elif usePsi:
                plot2D('PSIRZ_NORM', ax, **kw)
            else:
                plot2D('RHORZ', ax, **kw)

    def get2D(self, Q, r, z, interp='linear'):
        """
        Function to retrieve 2D quantity at coordinates

        :param Q: Quantity to be retrieved (either 2D array or string from 'AuxQuantities', e.g. RHORZ)

        :param r: r coordinate for retrieval

        :param z: z coordinate for retrieval

        :param interp: interpolation method ['linear','quadratic','cubic']

        >> OMFIT['test']=OMFITgeqdsk(OMFITsrc+"/../samples/g133221.01000")
        >> r=np.linspace(min(OMFIT['test']['RBBBS']),max(OMFIT['test']['RBBBS']),100)
        >> z=r*0
        >> tmp=OMFIT['test'].get2D('Br',r,z)
        >> pyplot.plot(r,tmp)
        """

        Z = self['AuxQuantities']['Z']
        R = self['AuxQuantities']['R']
        if isinstance(Q, str):
            Q = self['AuxQuantities'][Q]
        if interp == 'linear':
            interp = 1
        elif interp == 'quadratic':
            interp = 2
        elif interp == 'cubic':
            interp = 3
        return np.reshape(RectBivariateSplineNaN(Z, R, Q, kx=interp, ky=interp).ev(z.flatten(), r.flatten()), r.size)

    def map2D(self, x, y, X, interp='linear', maskName='core_plasma_mask', outsideOfMask=np.nan):
        """
        Function to map 1D quantity to 2D grid

        :param x: abscissa of 1D quantity

        :param y: 1D quantity

        :param X: 2D distribution of 1D quantity abscissa

        :param interp: interpolation method ['linear','cubic']

        :param maskName: one among `limiter_mask`, `vessel_mask`, `core_plasma_mask`, `edge_plasma_mask` or None

        :param outsideOfMask: value to use outside of the mask

        """

        dp = x[1] - x[0]
        Y = interp1e(x, y, kind=interp)(X)

        if maskName is not None:
            mask = self.calc_masks()[maskName]
            Y *= mask
            Y[np.where(mask <= 0)] = outsideOfMask
        return Y

    def calc_pprime_ffprim(self, press=None, pprime=None, Jt=None, Jt_over_R=None, fpol=None):
        """
        This method returns the P' and FF' given P or P' and J or J/R based on the current equilibrium fluxsurfaces geometry

        :param press: pressure

        :param pprime: pressure*pressure'

        :param Jt: toroidal current

        :param Jt_over_R: flux surface averaged toroidal current density over major radius

        :param fpol: F

        :return: P', FF'
        """
        COCOS = define_cocos(self.cocos)
        if press is not None:
            pprime = deriv(np.linspace(self['SIMAG'], self['SIBRY'], len(press)), press)
        if fpol is not None:
            ffprim = deriv(np.linspace(self['SIMAG'], self['SIBRY'], len(press)), fpol) * fpol
        if Jt is not None:
            ffprim = Jt * COCOS['sigma_Bp'] / (2.0 * np.pi) ** COCOS['exp_Bp'] + pprime * self['fluxSurfaces']['avg']['R']
            ffprim *= -4 * np.pi * 1e-7 / (self['fluxSurfaces']['avg']['1/R'])
        elif Jt_over_R is not None:
            ffprim = Jt_over_R * COCOS['sigma_Bp'] / (2.0 * np.pi) ** COCOS['exp_Bp'] + pprime
            ffprim *= -4 * np.pi * 1e-7 / self['fluxSurfaces']['avg']['1/R**2']
        return pprime, ffprim

    def calc_Ip(self, Jt_over_R=None):
        """
        This method returns the toroidal current within the flux surfaces based on the current equilibrium fluxsurfaces geometry

        :param Jt_over_R: flux surface averaged toroidal current density over major radius

        :return: Ip
        """
        if Jt_over_R is None:
            Jt_over_R = self['fluxSurfaces']['avg']['Jt/R']
        return integrate.cumtrapz(self['fluxSurfaces']['avg']['vp'] * Jt_over_R, self['fluxSurfaces']['geo']['psi'], initial=0) / (
            2.0 * np.pi
        )

    def add_rhovn(self):
        """
        Calculate RHOVN from PSI and `q` profile
        """
        # add RHOVN if QPSI is non-zero (ie. vacuum gEQDSK)
        if np.sum(np.abs(self['QPSI'])):
            phi = integrate.cumtrapz(self['QPSI'], np.linspace(self['SIMAG'], self['SIBRY'], len(self['QPSI'])), initial=0)
            self['RHOVN'] = np.sqrt(np.abs(2 * np.pi * phi / (np.pi * self['BCENTR'])))
            if np.nanmax(self['RHOVN']) > 0:
                self['RHOVN'] = self['RHOVN'] / np.nanmax(self['RHOVN'])
        else:
            # if no QPSI information, then set RHOVN to zeros
            self['RHOVN'] = self['QPSI'] * 0.0

    def case_info(self):
        """
        Interprets the CASE field of the GEQDSK and converts it into a dictionary

        :return: dict
        Contains as many values as can be determined. Fills in None when the correct value cannot be determined.
            device
            shot
            time (within shot)
            date (of code execution)
            efitid (aka snap file or tree name)
            code_version
        """
        device = None
        shot = None
        time = None
        date = None
        efitid = None
        code_version = None

        # Make a list of substrings that should be contained by each field of CASE for each form.
        # Form 1: CASE is a 6 element list containing code_version, month/day, /year, #shot, time, efitid
        caseform_contains = {1: ['', '/', '/', '#', 'ms', '']}
        caseform = None
        possible_forms = []

        # Go through each known form and test whether it could apply
        for caseform_, contains in caseform_contains.items():
            if (len(self['CASE']) == len(contains)) and all(c in self['CASE'][i] for i, c in enumerate(contains)):
                possible_forms += [caseform_]
        if len(possible_forms) == 1:
            caseform = possible_forms[0]
        else:
            printe('More than one form of CASE could be valid.')

        # Assign info based on which form CASE takes.
        if caseform == 1:
            device = None
            shot = int(self['CASE'][3].split('#')[1].strip())
            time = float(self['CASE'][4].split('ms')[0].strip())
            year = int(self['CASE'][2].split('/')[1].strip())
            month, day = self['CASE'][1].split('/')
            date = datetime.datetime(year=year, month=int(month), day=int(day))
            efitid = self['CASE'][5].strip()
            code_version = self['CASE'][0].strip()

        return dict(device=device, shot=shot, time=time, date=date, efitid=efitid, code_version=code_version)

    @dynaLoad
    def to_omas(self, ods=None, time_index=0, allow_derived_data=True):
        """
        translate gEQDSK class to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :param allow_derived_data: bool
            Allow data to be drawn from fluxSurfaces, AuxQuantities, etc. May trigger dynamic loading.

        :return: ODS
        """
        if ods is None:
            ods = ODS()

        if self.cocos is None:
            cocosio = self.native_cocos()  # assume native gEQDSK COCOS
        else:
            cocosio = self.cocos

        # delete time_slice before writing, since these quantities all need to be consistent
        if 'equilibrium.time_slice.%d' % time_index in ods:
            del ods['equilibrium.time_slice.%d' % time_index]

        # write derived quantities from fluxSurfaces
        flx = self['fluxSurfaces']
        ods = flx.to_omas(ods, time_index=time_index)

        # align psi grid
        psi = np.linspace(self['SIMAG'], self['SIBRY'], len(self['PRES']))
        if f'equilibrium.time_slice.{time_index}.profiles_1d.psi' in ods:
            with omas_environment(ods, cocosio=cocosio):
                m0 = psi[0]
                M0 = psi[-1]
                m1 = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.psi'][0]
                M1 = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.psi'][-1]
                psi = (psi - m0) / (M0 - m0) * (M1 - m1) + m1
        coordsio = {f'equilibrium.time_slice.{time_index}.profiles_1d.psi': psi}

        # add gEQDSK quantities
        with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):

            try:
                ods['dataset_description.data_entry.pulse'] = int(
                    re.sub('[a-zA-Z]([0-9]+).([0-9]+).*', r'\1', os.path.split(self.filename)[1])
                )
            except Exception:
                ods['dataset_description.data_entry.pulse'] = 0

            try:
                separator = ''
                ods['equilibrium.ids_properties.comment'] = self['CASE'][0]
            except Exception:
                ods['equilibrium.ids_properties.comment'] = 'omasEQ'

            try:
                ods[f'equilibrium.time_slice.{time_index}.time'] = (
                    float(re.sub('[a-zA-Z]([0-9]+).([0-9]+).*', r'\2', os.path.split(self.filename)[1])) / 1000.0
                )
            except Exception:
                ods[f'equilibrium.time_slice.{time_index}.time'] = 0.0

            # *********************
            # ESSENTIAL
            # *********************
            if 'RHOVN' in self:  # EAST gEQDSKs from MDSplus do not always have RHOVN defined
                rhovn = self['RHOVN']
            else:

                printd('RHOVN is missing from top level geqdsk, so falling back to RHO from AuxQuantities', topic='OMFITgeqdsk')
                rhovn = self['AuxQuantities']['RHO']

            # ============0D
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.magnetic_axis.r'] = self['RMAXIS']
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.magnetic_axis.z'] = self['ZMAXIS']
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.psi_axis'] = self['SIMAG']
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.psi_boundary'] = self['SIBRY']
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.ip'] = self['CURRENT']

            # ============0D time dependent vacuum_toroidal_field
            ods['equilibrium.vacuum_toroidal_field.r0'] = self['RCENTR']
            ods.set_time_array('equilibrium.vacuum_toroidal_field.b0', time_index, self['BCENTR'])

            # ============1D
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.f'] = self['FPOL']
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.pressure'] = self['PRES']
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.f_df_dpsi'] = self['FFPRIM']
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.dpressure_dpsi'] = self['PPRIME']
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.q'] = self['QPSI']
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.rho_tor_norm'] = rhovn

            # ============2D
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.grid_type.index'] = 1
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.grid.dim1'] = np.linspace(0, self['RDIM'], self['NW']) + self['RLEFT']
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.grid.dim2'] = (
                np.linspace(0, self['ZDIM'], self['NH']) - self['ZDIM'] / 2.0 + self['ZMID']
            )
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.psi'] = self['PSIRZ'].T

            # *********************
            # DERIVED
            # *********************

            # ============0D
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.magnetic_axis.b_field_tor'] = (
                self['BCENTR'] * self['RCENTR'] / self['RMAXIS']
            )
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.q_axis'] = self['QPSI'][0]
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.q_95'] = interpolate.interp1d(rhovn, self['QPSI'])(0.95)
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.q_min.value'] = self['QPSI'][np.argmin(abs(self['QPSI']))]
            ods[f'equilibrium.time_slice.{time_index}.global_quantities.q_min.rho_tor_norm'] = rhovn[np.argmin(abs(self['QPSI']))]

            # ============1D
            Psi1D = np.linspace(self['SIMAG'], self['SIBRY'], len(self['FPOL']))
            # ods[f'equilibrium.time_slice.{time_index}.profiles_1d.psi'] = Psi1D #no need bacause of coordsio
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.phi'] = self['AuxQuantities']['PHI']
            ods[f'equilibrium.time_slice.{time_index}.profiles_1d.rho_tor'] = rhovn * self['AuxQuantities']['RHOm']

            # ============2D
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.b_field_r'] = self['AuxQuantities']['Br'].T
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.b_field_tor'] = self['AuxQuantities']['Bt'].T
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.b_field_z'] = self['AuxQuantities']['Bz'].T
            ods[f'equilibrium.time_slice.{time_index}.profiles_2d.0.phi'] = (interp1e(Psi1D, self['AuxQuantities']['PHI'])(self['PSIRZ'])).T

        # These quantities don't require COCOS or coordinate transformation
        ods[f'equilibrium.time_slice.{time_index}.boundary.outline.r'] = self['RBBBS']
        ods[f'equilibrium.time_slice.{time_index}.boundary.outline.z'] = self['ZBBBS']
        if allow_derived_data and 'Rx1' in self['AuxQuantities'] and 'Zx1' in self['AuxQuantities']:
            ods[f'equilibrium.time_slice.{time_index}.boundary.x_point.0.r'] = self['AuxQuantities']['Rx1']
            ods[f'equilibrium.time_slice.{time_index}.boundary.x_point.0.z'] = self['AuxQuantities']['Zx1']
        if allow_derived_data and 'Rx2' in self['AuxQuantities'] and 'Zx2' in self['AuxQuantities']:
            ods[f'equilibrium.time_slice.{time_index}.boundary.x_point.1.r'] = self['AuxQuantities']['Rx2']
            ods[f'equilibrium.time_slice.{time_index}.boundary.x_point.1.z'] = self['AuxQuantities']['Zx2']

        # Set the time array
        ods.set_time_array('equilibrium.time', time_index, ods[f'equilibrium.time_slice.{time_index}.time'])

        # ============WALL
        ods['wall.description_2d.0.limiter.type.name'] = 'first_wall'
        ods['wall.description_2d.0.limiter.type.index'] = 0
        ods['wall.description_2d.0.limiter.type.description'] = 'first wall'
        ods['wall.description_2d.0.limiter.unit.0.outline.r'] = self['RLIM']
        ods['wall.description_2d.0.limiter.unit.0.outline.z'] = self['ZLIM']

        # Set the time array (yes... also for the wall)
        ods.set_time_array('wall.time', time_index, ods[f'equilibrium.time_slice.{time_index}.time'])

        return ods

    def from_omas(self, ods, time_index=0, profiles_2d_index=0, time=None):
        """
        translate OMAS data structure to gEQDSK

        :param time_index: time index to extract data from

        :param profiles_2d_index: index of profiles_2d to extract data from

        :param time: time in seconds where to extract the data (if set it superseeds time_index)

        :return: self
        """

        cocosio = 1  # from OMAS always makes a gEQDSK in COCOS 1
        COCOS = define_cocos(cocosio)

        # handle shot and time
        try:
            shot = int(ods['dataset_description.data_entry.pulse'])
        except Exception:
            try:
                tmp = re.match('g([0-9]+).([0-9]+)', os.path.basename(self.filename))
                shot = int(tmp.groups()[0])
            except Exception:
                shot = 0
        if time is not None:
            time_index = np.argmin(np.abs(ods['equilibrium.time'] - time))
        time = int(np.round(ods['equilibrium.time'][time_index] * 1000))

        # setup coordinates
        with omas_environment(ods, cocosio=cocosio):
            psi = np.linspace(
                ods[f'equilibrium.time_slice.{time_index}.profiles_1d.psi'][0],
                ods[f'equilibrium.time_slice.{time_index}.profiles_1d.psi'][-1],
                ods[f'equilibrium.time_slice.{time_index}.profiles_2d.{profiles_2d_index}.grid.dim1'].size,
            )
            coordsio = {f'equilibrium.time_slice.{time_index}.profiles_1d.psi': psi}

        # assign data in gEQDSK class
        with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
            R = ods[f'equilibrium.time_slice.{time_index}.profiles_2d.{profiles_2d_index}.grid.dim1']
            Z = ods[f'equilibrium.time_slice.{time_index}.profiles_2d.{profiles_2d_index}.grid.dim2']

            # ============0D
            today = datetime.datetime.now().strftime('   %d/%m_/%Y   ').split('_')
            self['CASE'] = [ods.get('equilibrium.ids_properties.comment', '  EFITD ')] + today + [' #%6d' % shot, '  %dms' % time, '  omas']

            self['NW'] = ods[f'equilibrium.time_slice.{time_index}.profiles_2d.{profiles_2d_index}.grid.dim1'].size
            self['NH'] = ods[f'equilibrium.time_slice.{time_index}.profiles_2d.{profiles_2d_index}.grid.dim2'].size
            self['RDIM'] = max(R) - min(R)
            self['ZDIM'] = max(Z) - min(Z)
            self['RLEFT'] = min(R)
            self['ZMID'] = (max(Z) + min(Z)) / 2.0
            self['RMAXIS'] = ods[f'equilibrium.time_slice.{time_index}.global_quantities.magnetic_axis.r']
            self['ZMAXIS'] = ods[f'equilibrium.time_slice.{time_index}.global_quantities.magnetic_axis.z']

            if 'equilibrium.vacuum_toroidal_field.b0' in ods:
                self['RCENTR'] = ods['equilibrium.vacuum_toroidal_field.r0']
                self['BCENTR'] = ods['equilibrium.vacuum_toroidal_field.b0'][time_index]
            else:
                self['RCENTR'] = (max(R) + min(R)) / 2.0
                Baxis = ods[f'equilibrium.time_slice.{time_index}.global_quantities.magnetic_axis.b_field_tor']
                self['BCENTR'] = Baxis * self['RMAXIS'] / self['RCENTR']

            self['CURRENT'] = ods[f'equilibrium.time_slice.{time_index}.global_quantities.ip']
            self['SIMAG'] = ods[f'equilibrium.time_slice.{time_index}.global_quantities.psi_axis']
            self['SIBRY'] = ods[f'equilibrium.time_slice.{time_index}.global_quantities.psi_boundary']
            self['KVTOR'] = 0.0
            self['RVTOR'] = self['RCENTR']
            self['NMASS'] = 0.0

            # ============1D
            self['FPOL'] = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.f']
            self['PRES'] = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.pressure']
            self['FFPRIM'] = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.f_df_dpsi']
            self['PPRIME'] = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.dpressure_dpsi']
            self['QPSI'] = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.q']

            if 'profiles_1d.rho_tor_norm' in ods['equilibrium.time_slice'][time_index]:
                self['RHOVN'] = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.rho_tor_norm']
            elif 'profiles_1d.rho_tor' in ods['equilibrium.time_slice'][time_index]:
                rho = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.rho_tor']
                self['RHOVN'] = rho / np.max(rho)
            else:
                if 'profiles_1d.phi' in ods['equilibrium.time_slice'][time_index]:
                    phi = ods[f'equilibrium.time_slice.{time_index}.profiles_1d.phi']
                elif 'profiles_1d.q' in ods['equilibrium.time_slice'][time_index]:
                    phi = integrate.cumtrapz(
                        ods[f'equilibrium.time_slice.{time_index}.profiles_1d.q'],
                        ods[f'equilibrium.time_slice.{time_index}.profiles_1d.psi'],
                        initial=0,
                    )
                    phi *= COCOS['sigma_Bp'] * COCOS['sigma_rhotp'] * (2.0 * np.pi) ** (1.0 - COCOS['exp_Bp'])
                self['RHOVN'] = np.sqrt(phi / phi[-1])

            # ============2D
            self['PSIRZ'] = ods[f'equilibrium.time_slice.{time_index}.profiles_2d'][profiles_2d_index]['psi'].T

        # These quantities don't require COCOS or coordinate transformation
        self['RBBBS'] = ods[f'equilibrium.time_slice.{time_index}.boundary.outline.r']
        self['ZBBBS'] = ods[f'equilibrium.time_slice.{time_index}.boundary.outline.z']
        self['NBBBS'] = len(self['RBBBS'])

        # ============WALL
        self['RLIM'] = ods['wall.description_2d.0.limiter.unit.0.outline.r']
        self['ZLIM'] = ods['wall.description_2d.0.limiter.unit.0.outline.z']
        self['LIMITR'] = len(self['RLIM'])

        self.addAuxNamelist()
        # cocosify to have AuxQuantities and fluxSurfaces creater properly
        self._cocos = cocosio
        self.cocosify(cocosio, calcAuxQuantities=True, calcFluxSurfaces=True)

        # automatically set gEQDSK filename if self.filename was None
        if self.filename is None:
            self.filename = OMFITobject('g%06d.%05d' % (shot, time)).filename
            self.dynaLoad = False

        return self

    def resample(self, nw_new):
        """
        Change gEQDSK resolution
        NOTE: This method operates in place

        :param nw_new: new grid resolution

        :return: self
        """
        old1d = np.linspace(0, 1, len(self['PRES']))
        old2dw = np.linspace(0, 1, self['NW'])
        old2dh = np.linspace(0, 1, self['NH'])
        new = np.linspace(0, 1, nw_new)

        for item in list(self.keys()):
            if item == 'PSIRZ':
                self[item] = RectBivariateSplineNaN(old2dh, old2dw, self['PSIRZ'])(new, new)
            elif isinstance(self[item], np.ndarray) and self[item].size == len(old1d):
                self[item] = interpolate.interp1d(old1d, self[item], kind=3)(new)
        self['NW'] = nw_new
        self['NH'] = nw_new
        if 'AuxQuantities' in self:
            self.addAuxQuantities()
        if 'fluxSurfaces' in self:
            self.addFluxSurfaces(**self.OMFITproperties)

        return self

    def downsample_limiter(self, max_lim=None, in_place=True):
        """
        Downsample the limiter

        :param max_lim: If max_lim is specified and the number of limiter points
            - before downsampling is smaller than max_lim, then no downsampling is performed
            after downsampling is larger than max_lim, then an error is raised

        :param in_place: modify this object in place or not

        :return: downsampled rlim and zlim arrays
        """
        from omfit_classes.utils_math import simplify_polygon

        if 'LIMITR' not in self:
            raise KeyError('LIMITR: Limiter does not exist for this geqdsk')
        rlim, zlim = self['RLIM'], self['ZLIM']
        if max_lim and self['LIMITR'] <= max_lim:
            printd('Not downsampling number of limiter points', topic='omfit_geqdsk')
            return rlim, zlim
        printd('Downsampling number of limiter points', topic='omfit_geqdsk')
        printd('- Started with %d' % self['LIMITR'], topic='omfit_geqdsk')
        tolerance = simplify_polygon(rlim, zlim, tolerance=None)
        max_tolerance = np.sqrt((np.max(rlim) - np.min(rlim)) ** 2 + (np.max(zlim) - np.min(zlim)) ** 2)
        nlim = len(rlim)
        it = 0
        while nlim > 3:
            it += 1
            if it > 1000:
                raise RuntimeError('Too many interations downsampling limiter')
            rlim, zlim = simplify_polygon(self['RLIM'], self['ZLIM'], tolerance=tolerance)
            if max_lim is None:
                tolerance = simplify_polygon(rlim, zlim, tolerance=None)
            else:
                tolerance = tolerance * 2.0
            if max_lim is None and len(rlim) >= nlim:
                break
            elif max_lim is not None and len(rlim) <= max_lim:
                break
            elif tolerance >= max_tolerance:
                break
            nlim = len(rlim)
        nlim = len(rlim)
        if max_lim and nlim > max_lim:
            raise RuntimeError('After downsampling limiter has too many points: %d' % self['LIMITR'])
        if in_place:
            self['RLIM'] = rlim
            self['ZLIM'] = zlim
            self['LIMITR'] = nlim
            printd('- Ended with %d' % nlim, topic='omfit_geqdsk')
        return rlim, zlim

    def downsample_boundary(self, max_bnd=None, in_place=True):
        """
        Downsample the boundary

        :param max_bnd: If max_bnd is specified and the number of boundary points
            - before downsampling is smaller than max_bnd, then no downsampling is performed
            - after downsampling is larger than max_bnd, then an error is raised

        :param in_place: modify this object in place or not

        :return: downsampled rbnd and zbnd arrays
        """
        from omfit_classes.utils_math import simplify_polygon

        rbnd, zbnd = self['RBBBS'], self['ZBBBS']
        if max_bnd and self['NBBBS'] <= max_bnd:
            printd('Not downsampling number of boundary points', topic='omfit_geqdsk')
            return rbnd, zbnd
        printd('Downsampling number of boundary points', topic='omfit_geqdsk')
        printd('- Started with %d' % self['NBBBS'], topic='omfit_geqdsk')
        tolerance = simplify_polygon(rbnd, zbnd, tolerance=None)
        max_tolerance = np.sqrt((np.max(rbnd) - np.min(rbnd)) ** 2 + (np.max(zbnd) - np.min(zbnd)) ** 2)
        nbnd = len(rbnd)
        it = 0
        while nbnd > 3:
            it += 1
            if it > 1000:
                raise RuntimeError('Too many interations downsampling boundary')
            rbnd, zbnd = simplify_polygon(self['RBBBS'], self['ZBBBS'], tolerance=tolerance)
            if max_bnd is None:
                tolerance = simplify_polygon(rbnd, zbnd, tolerance=None)
            else:
                tolerance = tolerance * 2.0
            if max_bnd is None and len(rbnd) >= nbnd:
                break
            elif max_bnd is not None and len(rbnd) <= max_bnd:
                break
            elif tolerance >= max_tolerance:
                break
            nbnd = len(rbnd)
        nbnd = len(rbnd)
        if max_bnd and nbnd > max_bnd:
            raise RuntimeError('After downsampling boundary has too many points: %d' % self['NBBBS'])
        if in_place:
            self['RBBBS'] = rbnd
            self['ZBBBS'] = zbnd
            self['NBBBS'] = nbnd
            printd('- Ended with %d' % nbnd, topic='omfit_geqdsk')
        return rbnd, zbnd

    def from_mdsplus(
        self,
        device=None,
        shot=None,
        time=None,
        exact=False,
        SNAPfile='EFIT01',
        time_diff_warning_threshold=10,
        fail_if_out_of_range=True,
        show_missing_data_warnings=True,
        quiet=False,
    ):
        """
        Fill in gEQDSK data from MDSplus

        :param device: The tokamak that the data correspond to ('DIII-D', 'NSTX', etc.)

        :param shot: Shot number from which to read data

        :param time: time slice from which to read data

        :param exact: get data from the exact time-slice

        :param SNAPfile: A string containing the name of the MDSplus tree to connect to, like 'EFIT01', 'EFIT02', 'EFIT03', ...

        :param time_diff_warning_threshold: raise error/warning if closest time slice is beyond this treshold

        :param fail_if_out_of_range: Raise error or warn if closest time slice is beyond time_diff_warning_threshold

        :param show_missing_data_warnings: Print warnings for missing data

        :param quiet: verbosity

        :return: self
        """

        if device is None:
            raise ValueError('Must specify device')
        if shot is None:
            raise ValueError('Must specify shot')
        if time is None:
            raise ValueError('Must specify time')

        tmp = from_mds_plus(
            device=device,
            shot=shot,
            times=[time],
            exact=exact,
            snap_file=SNAPfile,
            time_diff_warning_threshold=time_diff_warning_threshold,
            fail_if_out_of_range=fail_if_out_of_range,
            get_afile=False,
            show_missing_data_warnings=show_missing_data_warnings,
            debug=False,
            quiet=quiet,
        )['gEQDSK'][time]

        self.__dict__ = tmp.__dict__
        self.update(tmp)

        return self

    def from_rz(self, r, z, psival, p, f, q, B0, R0, ip, resolution, shot=0, time=0, RBFkw={}):
        """
        Generate gEQDSK file from r, z points

        :param r: 2D array with R coordinates with 1st dimension being the flux surface index and the second theta

        :param z: 2D array with Z coordinates with 1st dimension being the flux surface index and the second theta

        :param psival: 1D array with psi values

        :param p: 1D array with pressure values

        :param f: 1D array with fpoloidal values

        :param q: 1D array with safety factor values

        :param B0: scalar vacuum B toroidal at R0

        :param R0: scalar R where B0 is defined

        :param ip: toroidal current

        :param resolution: g-file grid resolution

        :param shot: used to set g-file string

        :param time: used to set g-file string

        :param RBFkw: keywords passed to internal Rbf interpolator

        :return: self
        """
        from scipy.interpolate import Rbf

        # a minuscule amount of smoothing prevents numerical issues
        RBFkw.setdefault('smooth', 1e-6)

        # define gEQDSK grid
        rg = np.linspace(np.min(r) - 0.2, np.max(r) + 0.2, resolution)
        zg = np.linspace(np.min(z) - 0.2, np.max(z) + 0.2, resolution)
        RG, ZG = np.meshgrid(rg, zg)

        # pick out the separatrix values
        rbbbs = r[-1, :]
        zbbbs = z[-1, :]

        # RBF does not need a regular grid.
        # we random sample the r,z grid points to limit the number of points taken based on the requested resolution
        # this is necessary because Rbf scales very poorly with number of input samples
        psi = np.array([psival] * r.shape[1]).T
        r0 = []
        z0 = []
        psi0 = []
        if (np.sum(np.abs(r[0, :] - r[0, 0])) + np.sum(np.abs(z[0, :] - z[0, 0]))) < 1e-6:
            raxis = r[0, 0]
            zaxis = z[0, 0]
            r0 = [r[0, 0]]
            z0 = [z[0, 0]]
            psi0 = [psi[0, 0]]
            r = r[1:, :]
            z = z[1:, :]
            psi = psi[1:, :]
        else:
            raxis = np.mean(r[0, :])
            zaxis = np.mean(z[0, :])
        r = np.hstack((r0, r.flatten()))
        z = np.hstack((z0, z.flatten()))
        psi = np.hstack((psi0, psi.flatten()))
        index = list(range(len(psi)))
        np.random.shuffle(index)
        index = index[: int(resolution ** 2 // 2)]  # heuristic choice to pick the max number of points used in the reconstruction

        # interpolate to EFIT grid
        PSI = Rbf(r[index], z[index], psi[index], **RBFkw)(RG, ZG)

        # case
        today = datetime.datetime.now().strftime('   %d/%m_/%Y   ').split('_')
        self['CASE'] = ['  EFITD '] + today + [' #%6d' % shot, '  %dms' % time, 'rz_2_g']

        # scalars
        self['NW'] = resolution
        self['NH'] = resolution
        self['RDIM'] = max(rg) - min(rg)
        self['ZDIM'] = max(zg) - min(zg)
        self['RLEFT'] = min(rg)
        self['ZMID'] = (max(zg) + min(zg)) / 2.0
        self['RCENTR'] = R0
        self['BCENTR'] = B0
        self['CURRENT'] = ip
        self['RMAXIS'] = raxis
        self['ZMAXIS'] = zaxis
        self['SIMAG'] = np.min(psival)
        self['SIBRY'] = np.max(psival)

        # 1d quantiites
        psibase = np.linspace(self['SIMAG'], self['SIBRY'], self['NW'])
        self['PRES'] = interpolate.interp1d(psival, p)(psibase)
        self['QPSI'] = interpolate.interp1d(psival, q)(psibase)
        self['FPOL'] = interpolate.interp1d(psival, f)(psibase)
        self['FFPRIM'] = self['FPOL'] * np.gradient(self['FPOL']) / np.gradient(psibase)
        self['PPRIME'] = np.gradient(self['PRES']) / np.gradient(psibase)

        # 2d quantities
        self['PSIRZ'] = PSI

        # square limiter
        self['RLIM'] = np.array([min(rg) + 0.1, max(rg) - 0.1, max(rg) - 0.1, min(rg) + 0.1, min(rg) + 0.1])
        self['ZLIM'] = np.array([min(zg) + 0.1, min(zg) + 0.1, max(zg) - 0.1, max(zg) - 0.1, min(zg) + 0.1])
        self['LIMITR'] = 5

        # lcfs
        self['RBBBS'] = rbbbs
        self['ZBBBS'] = zbbbs
        self['NBBBS'] = len(self['ZBBBS'])

        # add extras
        self.add_rhovn()
        self.addAuxQuantities()
        self.addFluxSurfaces()
        return self

    def from_uda(self, shot=99999, time=0.0, pfx='efm', device='MAST'):
        """
        Read in data from Unified Data Access (UDA)

        :param shot: shot number to read in

        :param time: time to read in data

        :param pfx: UDA data source prefix e.g. pfx+'_psi'

        :param device: tokamak name
        """
        self.status = False

        try:
            import pyuda
        except Exception:
            raise ImportError("No UDA module found, cannot load MAST shot")

        client = pyuda.Client()

        if pfx == 'epm':
            self.from_uda_epm(shot=shot, time=time, device='MAST')
            return self

        try:
            _psi = client.get(pfx + "_psi(r,z)", shot)
        except pyuda.ProtocolException:
            printw("Please deselect Fetch in parallel")
            return
        _r = client.get(pfx + "_grid(r)", shot)
        _z = client.get(pfx + "_grid(z)", shot)
        _psi_axis = client.get(pfx + "_psi_axis", shot)
        _psi_bnd = client.get(pfx + "_psi_boundary", shot)
        _rcent = client.get(pfx + "_bvac_R", shot)
        _cpasma = client.get(pfx + "_plasma_curr(C)", shot)
        _bphi = client.get(pfx + "_bvac_val", shot)
        _axisr = client.get(pfx + "_magnetic_axis_r", shot)
        _axisz = client.get(pfx + "_magnetic_axis_z", shot)
        _fpol = client.get(pfx + "_f(psi)_(c)", shot)
        _ppres = client.get(pfx + "_p(psi)_(c)", shot)
        _ffprime = client.get(pfx + "_ffprime", shot)
        _pprime = client.get(pfx + "_pprime", shot)
        _qprof = client.get(pfx + "_q(psi)_(c)", shot)
        _nbbbs = client.get(pfx + "_lcfs(n)_(c)", shot)
        _rbbbs = client.get(pfx + "_lcfs(r)_(c)", shot)
        _zbbbs = client.get(pfx + "_lcfs(z)_(c)", shot)
        _rlim = client.get(pfx + "_limiter(r)", shot)
        _zlim = client.get(pfx + "_limiter(z)", shot)

        tind = np.abs(_psi.time.data - time).argmin()
        _time = _psi.time.data[tind]
        tind_ax = np.abs(_psi_axis.time.data - time).argmin()
        tind_bnd = np.abs(_psi_bnd.time.data - time).argmin()
        tind_Bt = np.abs(_bphi.time.data - time).argmin()
        tind_sigBp = np.abs(_cpasma.time.data - time).argmin()
        tind_xpt = np.abs(_axisr.time.data - time).argmin()
        tind_qpf = np.abs(_qprof.time.data - time).argmin()

        # case
        self['CASE'] = ['EFIT++  ', device, ' #%6d' % shot, ' #%4dms' % int(time * 1000), '        ', '        ']

        # scalars
        self['NW'] = len(_r.data[0, :])
        self['NH'] = len(_z.data[0, :])
        self['RDIM'] = max(_r.data[0, :]) - min(_r.data[0, :])
        self['ZDIM'] = max(_z.data[0, :]) - min(_z.data[0, :])
        self['RLEFT'] = min(_r.data[0, :])
        self['ZMID'] = (max(_z.data[0, :]) + min(_z.data[0, :])) / 2.0
        self['RCENTR'] = _rcent.data[tind_Bt]
        self['BCENTR'] = _bphi.data[tind_Bt]
        self['CURRENT'] = _cpasma.data[tind_sigBp]
        self['RMAXIS'] = _axisr.data[tind_xpt]
        self['ZMAXIS'] = _axisz.data[tind_xpt]
        self['SIMAG'] = _psi_axis.data[tind_ax]
        self['SIBRY'] = _psi_bnd.data[tind_bnd]

        # 1d quantiites
        self['PRES'] = _ppres.data[tind_qpf, :]
        self['QPSI'] = _qprof.data[tind_qpf, :]
        self['FPOL'] = _fpol.data[tind_qpf, :]
        self['FFPRIM'] = _ffprime.data[tind_qpf, :]
        self['PPRIME'] = _pprime.data[tind_qpf, :]

        # 2d quantities
        self['PSIRZ'] = _psi.data[tind, :, :]

        # limiter
        self['RLIM'] = _rlim.data[0, :]
        self['ZLIM'] = _zlim.data[0, :]
        self['LIMITR'] = len(_rlim.data[0, :])

        # lcfs
        nbbbs = _nbbbs.data[tind_qpf]
        self['RBBBS'] = _rbbbs.data[tind_qpf, :nbbbs]
        self['ZBBBS'] = _zbbbs.data[tind_qpf, :nbbbs]
        self['NBBBS'] = nbbbs

        # cocosify to have AuxQuantities and fluxSurfaces created properly
        self._cocos = 3
        self.cocosify(1, calcAuxQuantities=True, calcFluxSurfaces=True)
        self.add_rhovn()
        self.status = True
        return self

    def from_uda_epm(self, shot=99999, time=0.0, device='MAST'):
        """
        Read in data from Unified Data Access (UDA) in EPM format

        :param shot: shot number to read in

        :param time: time to read in data

        :param device: tokamak name
        """
        self.status = False

        try:
            import pyuda
        except Exception:
            raise ImportError("No UDA module found, cannot load MAST shot")

        client = pyuda.Client()

        if shot < 44849:
            raise pyuda.ServerException('UDA data not available for MAST-U shots below 44849')

        _psi = client.get('/EPM/OUTPUT/PROFILES2D/POLOIDALFLUX', shot)
        _r = client.get('/EPM/OUTPUT/PROFILES2D/R', shot)
        _z = client.get('/EPM/OUTPUT/PROFILES2D/Z', shot)
        _rcent = client.get('EPM/OUTPUT/GLOBALPARAMETERS/BVACRMAG', shot)
        _bVac = client.get('/EPM/INPUT/BVACRADIUSPRODUCT', shot)
        _ppres = client.get('/EPM/OUTPUT/FLUXFUNCTIONPROFILES/STATICPRESSURE', shot)
        _qprof = client.get('/EPM/OUTPUT/FLUXFUNCTIONPROFILES/Q', shot)
        _ffprime = client.get('/EPM/OUTPUT/FLUXFUNCTIONPROFILES/FFPRIME', shot)
        _pprime = client.get('/EPM/OUTPUT/FLUXFUNCTIONPROFILES/STATICPPRIME', shot)
        _fpol = client.get('/EPM/OUTPUT/FLUXFUNCTIONPROFILES/RBPHI', shot)
        _psipr = client.get('/EPM/OUTPUT/FLUXFUNCTIONPROFILES/NORMALIZEDPOLOIDALFLUX', shot)
        _psi_axis = client.get('/EPM/OUTPUT/GLOBALPARAMETERS/PSIAXIS', shot)
        _psi_bnd = client.get('/EPM/OUTPUT/GLOBALPARAMETERS/PSIBOUNDARY', shot)
        _cpasma = client.get('/EPM/OUTPUT/GLOBALPARAMETERS/PLASMACURRENT', shot)
        _axisr = client.get('/EPM/OUTPUT/GLOBALPARAMETERS/MAGNETICAXIS/R', shot)
        _axisz = client.get('/EPM/OUTPUT/GLOBALPARAMETERS/MAGNETICAXIS/Z', shot)
        _rlim = client.get('/EPM/INPUT/LIMITER/RVALUES', shot)
        _zlim = client.get('/EPM/INPUT/LIMITER/ZVALUES', shot)
        _rbbbs = client.get('/EPM/OUTPUT/SEPARATRIXGEOMETRY/RBOUNDARY', shot)
        _zbbbs = client.get('/EPM/OUTPUT/SEPARATRIXGEOMETRY/ZBOUNDARY', shot)

        tind = np.abs(_psi.time.data - time).argmin()
        _time = _psi.time.data[tind]
        tind_ax = np.abs(_psi_axis.time.data - time).argmin()
        tind_bnd = np.abs(_psi_bnd.time.data - time).argmin()
        tind_Bt = np.abs(_bVac.time.data - time).argmin()
        tind_sigBp = np.abs(_cpasma.time.data - time).argmin()
        tind_xpt = np.abs(_axisr.time.data - time).argmin()
        tind_qpf = np.abs(_qprof.time.data - time).argmin()

        # case
        self['CASE'] = ['EFIT++  ', device, ' #%6d' % shot, ' #%4dms' % int(time * 1000), '        ', '        ']

        # scalars
        self['NW'] = len(_r.data)
        self['NH'] = len(_z.data)
        self['RDIM'] = max(_r.data) - min(_r.data)
        self['ZDIM'] = max(_z.data) - min(_z.data)
        self['RLEFT'] = min(_r.data)
        self['ZMID'] = (max(_z.data) + min(_z.data)) / 2.0
        self['RCENTR'] = _rcent.data[tind_Bt]
        self['BCENTR'] = _bVac.data[tind_Bt] / _rcent.data[tind_Bt]
        self['CURRENT'] = _cpasma.data[tind_sigBp]
        self['RMAXIS'] = _axisr.data[tind_xpt]
        self['ZMAXIS'] = _axisz.data[tind_xpt]
        self['SIMAG'] = _psi_axis.data[tind_ax]
        self['SIBRY'] = _psi_bnd.data[tind_bnd]

        # 1d quantiites
        self['PRES'] = _ppres.data[tind_qpf, :]
        self['QPSI'] = _qprof.data[tind_qpf, :]
        self['FPOL'] = _fpol.data[tind_qpf, :]
        self['FFPRIM'] = _ffprime.data[tind_qpf, :]
        self['PPRIME'] = _pprime.data[tind_qpf, :]

        # 2d quantities
        self['PSIRZ'] = np.transpose(_psi.data[tind, :, :])

        # limiter
        self['RLIM'] = _rlim.data
        self['ZLIM'] = _zlim.data
        self['LIMITR'] = len(_rlim.data)

        # lcfs
        nbbbs = np.shape(_rbbbs.data)[-1]
        self['RBBBS'] = _rbbbs.data[tind_qpf, :nbbbs]
        self['ZBBBS'] = _zbbbs.data[tind_qpf, :nbbbs]
        self['NBBBS'] = nbbbs

        # cocosify to have AuxQuantities and fluxSurfaces created properly
        self._cocos = 7
        self.cocosify(1, calcAuxQuantities=True, calcFluxSurfaces=True)
        self.add_rhovn()
        self.status = True
        return self

    def from_ppf(self, shot=99999, time=0.0, dda='EFIT', uid='jetppf', seq=0, device='JET'):
        """
        Read in data from JET PPF

        :param shot: shot number to read in

        :param time: time to read in data

        :param dda: Equilibrium source diagnostic data area

        :param uid: Equilibrium source user ID

        :param seq: Equilibrium source sequence number
        """

        self.status = False

        try:
            _times = np.squeeze(OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/PSI/' + str(seq), shot=shot).dim_of(1))
        except KeyError:
            raise OMFITexception("Data does not exist for DDA: {0}, UID: {1}, SEQ: {2}".format(dda, uid, seq))
        _r = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/PSIR/' + str(seq), shot=shot).data()
        _z = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/PSIZ/' + str(seq), shot=shot).data()
        _psi = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/PSI/' + str(seq), shot=shot).data()
        _psi = np.reshape(_psi, (-1, _r.size, _z.size))
        _psi_axis = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/FAXS/' + str(seq), shot=shot).data()
        _psi_bnd = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/FBND/' + str(seq), shot=shot).data()
        _cpasma = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/XIPC/' + str(seq), shot=shot).data()
        _bphi = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/BVAC/' + str(seq), shot=shot).data()
        _axisr = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/RMAG/' + str(seq), shot=shot).data()
        _axisz = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/ZMAG/' + str(seq), shot=shot).data()
        _fpol = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/F/' + str(seq), shot=shot).data()
        _ppres = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/P/' + str(seq), shot=shot).data()
        _ffprime = 4.0 * np.pi * 1.0e-7 * OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/DFDP/' + str(seq), shot=shot).data()
        _pprime = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/DPDP/' + str(seq), shot=shot).data()
        _qprof = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/Q/' + str(seq), shot=shot).data()
        _rbbbs = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/RBND/' + str(seq), shot=shot).data()
        _zbbbs = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/ZBND/' + str(seq), shot=shot).data()
        _nbbbs = OMFITmdsValue(server=device, TDI=uid + '@PPF/' + dda + '/NBND/' + str(seq), shot=shot).data()

        tind = np.abs(_times - time).argmin()

        # case
        self['CASE'] = ['EFIT++  ', device, ' #%6d' % shot, ' #%4dms' % int(time * 1000), '        ', '        ']

        # scalars
        self['NW'] = len(_r[0, :])
        self['NH'] = len(_z[0, :])
        self['RDIM'] = max(_r[0, :]) - min(_r[0, :])
        self['ZDIM'] = max(_z[0, :]) - min(_z[0, :])
        self['RLEFT'] = min(_r[0, :])
        self['ZMID'] = (max(_z[0, :]) + min(_z[0, :])) / 2.0
        self['RCENTR'] = (_times * 0 + 2.96)[tind]
        self['BCENTR'] = _bphi[tind]
        self['CURRENT'] = _cpasma[tind]
        self['RMAXIS'] = _axisr[tind]
        self['ZMAXIS'] = _axisz[tind]
        self['SIMAG'] = _psi_axis[tind]
        self['SIBRY'] = _psi_bnd[tind]

        # 1d quantiites
        self['PRES'] = _ppres[tind, :]
        self['QPSI'] = _qprof[tind, :]
        self['FPOL'] = _fpol[tind, :]
        self['FFPRIM'] = _ffprime[tind, :]
        self['PPRIME'] = _pprime[tind, :]

        # 2d quantities
        self['PSIRZ'] = _psi[tind, :, :]

        # limiter
        # fmt: off
        self['RLIM'] = np.array([3.28315,3.32014,3.36284,3.43528,3.50557,3.56982,3.62915,3.68080,3.72864,3.77203,3.80670,3.83648,3.85929,3.87677,3.88680,3.89095,3.88851,3.87962,3.86452,3.84270,3.81509,3.78134,3.74114,3.69522,3.67115,3.63730,3.64211,3.38176,3.33154,3.28182,3.18634,3.13665,3.00098,2.86066,2.76662,2.66891,2.56922,2.47303,2.38133,2.29280,2.19539,2.18241,2.06756,1.96130,1.94246,1.92612,1.91105,1.89707,1.88438,1.87173,1.85942,1.84902,1.84139,1.83714,1.83617,1.83847,1.84408,1.85296,1.86502,1.88041,1.89901,1.92082,1.94570,1.97056,2.00911,2.20149,2.14463,2.29362,2.29362,2.29544,2.35993,2.39619,2.40915,2.41225,2.41293,2.41293,2.41224,2.40762,2.39801,2.41921,2.42117,2.41880,2.41628,2.40573,2.31498,2.35349,2.37428,2.42744,2.44623,2.52369,2.52459,2.55911,2.55296,2.57391,2.63299,2.63369,2.69380,2.69434,2.75443,2.75517,2.81471,2.81467,2.80425,2.85703,2.87846,2.93644,2.95732,2.98698,2.89768,2.88199,2.88163,2.90045,2.89049,2.88786,2.88591,2.88591,2.88946,2.90082,2.91335,2.96348,3.00975,3.06005,3.19404,3.20225,3.30634,3.28315])
        self['ZLIM'] = np.array([-1.12439,-1.07315,-1.02794,-0.94610,-0.85735,-0.76585,-0.67035,-0.57428,-0.47128,-0.36188,-0.25689,-0.14639,-0.03751,0.07869,0.18627,0.30192,0.41715,0.52975,0.64099,0.75310,0.86189,0.96912,1.07530,1.17853,1.22759,1.33388,1.40768,1.64453,1.70412,1.73872,1.81753,1.85212,1.88341,1.94241,1.96996,1.98344,1.98201,1.96596,1.93599,1.89157,1.82284,1.82372,1.59819,1.32058,1.23457,1.14816,1.05033,0.95108,0.85152,0.75232,0.65348,0.55536,0.45663,0.35785,0.25926,0.16033,0.06101,-0.03766,-0.13519,-0.23314,-0.33022,-0.42668,-0.52195,-0.60693,-0.78399,-1.24842,-1.27494,-1.31483,-1.33144,-1.33443,-1.33443,-1.37323,-1.40030,-1.42198,-1.43148,-1.46854,-1.47678,-1.50441,-1.51641,-1.59223,-1.61022,-1.64283,-1.65610,-1.68971,-1.73870,-1.73870,-1.73504,-1.71349,-1.70983,-1.70983,-1.69997,-1.65498,-1.63799,-1.60180,-1.61714,-1.61989,-1.63550,-1.63821,-1.65481,-1.65658,-1.67203,-1.70788,-1.71158,-1.71158,-1.71602,-1.74139,-1.74595,-1.74595,-1.68233,-1.62282,-1.59160,-1.51041,-1.49841,-1.48925,-1.47397,-1.43566,-1.41714,-1.39278,-1.37624,-1.33481,-1.33481,-1.29777,-1.21404,-1.20891,-1.20891,-1.12439])
        self['LIMITR'] = len(self['RLIM'])
        # fmt: on

        # lcfs
        nbbbs = int(_nbbbs[tind])
        self['RBBBS'] = _rbbbs[tind, :nbbbs]
        self['ZBBBS'] = _zbbbs[tind, :nbbbs]
        self['NBBBS'] = nbbbs

        # cocosify to have AuxQuantities and fluxSurfaces created properly
        self._cocos = 7
        self.cocosify(1, calcAuxQuantities=True, calcFluxSurfaces=True)

        self.status = True
        return self

    def from_efitpp(self, ncfile=None, shot=99999, time=0.0, device='MAST'):
        """
        Read in data from EFIT++ netCDF

        :param filenc: EFIT++ netCDF file

        :param shot: shot number to read in

        :param time: time to read in data
        """
        try:
            from netCDF4 import Dataset
        except Exception:
            raise ImportError("Cannot load netcdf file")

        rootd = Dataset(ncfile, "r")

        try:
            _psi = np.transpose(rootd.groups['output'].groups['profiles2D'].variables['poloidalFlux'], (0, 2, 1))
            _r = rootd.groups['output'].groups['profiles2D'].variables['r']
            _z = rootd.groups['output'].groups['profiles2D'].variables['z']
            _radius = rootd.groups['output'].groups['radialProfiles'].variables['r']
            _bVac = rootd.groups['input'].groups['bVacRadiusProduct'].variables['values']
            _ppres = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['staticPressure']
            _rppres = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['rotationalPressure']
            _qprof = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['q']
            _ffprim = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['ffPrime']
            _pprime = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['staticPPrime']
            _fpol = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['rBphi']
            _psipr = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['normalizedPoloidalFlux']
            _psi_axis = rootd.groups['output'].groups['globalParameters'].variables['psiAxis']
            _psi_bnd = rootd.groups['output'].groups['globalParameters'].variables['psiBoundary']
            _cpasma = rootd.groups['output'].groups['globalParameters'].variables['plasmaCurrent']
            _axis = rootd.groups['output'].groups['globalParameters'].variables['magneticAxis']
            _rlim = rootd.groups['input'].groups['limiter'].variables['rValues']
            _zlim = rootd.groups['input'].groups['limiter'].variables['zValues']
            _rbbbs = rootd.groups['output'].groups['separatrixGeometry'].variables['boundaryCoords'][:]['R']
            _zbbbs = rootd.groups['output'].groups['separatrixGeometry'].variables['boundaryCoords'][:]['Z']
            self._timenc = np.array(rootd.variables['time'])

            tind = np.abs(self._timenc - time).argmin()

            # case
            self['CASE'] = ['EFIT++  ', device, ' #%6d' % shot, ' #%4dms' % int(time * 1000), '        ', '        ']

            # Define global parameters
            specs = utils_fusion.device_specs(device=device)

            check = np.isfinite(_psi_axis[tind])
            if not check:
                print("Skipping time slice: EFIT++ failed to converge for timeslice: ", time)
                self.status = False
                return
            # scalars
            self['NW'] = len(_r[tind, :])
            self['NH'] = len(_z[tind, :])
            self['RDIM'] = max(_r[tind, :]) - min(_r[tind, :])
            self['ZDIM'] = max(_z[tind, :]) - min(_z[tind, :])
            self['RLEFT'] = min(_r[tind, :])
            self['ZMID'] = (max(_z[tind, :]) + min(_z[tind, :])) / 2.0
            self['RCENTR'] = specs['R0']
            self['BCENTR'] = _bVac[tind] / specs['R0']
            self['CURRENT'] = _cpasma[tind]
            self['RMAXIS'] = (_axis[tind])[0]
            self['ZMAXIS'] = (_axis[tind])[1]
            self['SIMAG'] = _psi_axis[tind]
            self['SIBRY'] = _psi_bnd[tind]

            # 1d quantiites
            self['PRES'] = _ppres[tind, :]
            self['QPSI'] = _qprof[tind, :]
            self['FPOL'] = _fpol[tind, :]
            self['FFPRIM'] = _ffprim[tind, :]
            self['PPRIME'] = _pprime[tind, :]

            # 2d quantities
            self['PSIRZ'] = _psi[tind, :, :]

            # limiter
            self['RLIM'] = _rlim[:]
            self['ZLIM'] = _zlim[:]
            self['LIMITR'] = len(self['RLIM'])

            # lcfs
            self['RBBBS'] = _rbbbs[tind]
            self['ZBBBS'] = _zbbbs[tind]
            self['NBBBS'] = len(_zbbbs[tind])

            # cocosify to have AuxQuantities and fluxSurfaces created properly
            self._cocos = 7
            self.cocosify(1, calcAuxQuantities=True, calcFluxSurfaces=True)
            self.add_rhovn()
            self.status = True
        finally:
            rootd.close()

        return self

    def from_efit_epm(self, ncfile=None, shot=99999, time=0.0, device='MAST'):
        """
        Read in data from EFIT++ epm netCDF

        :param filenc: EFIT++ netCDF file

        :param shot: shot number to read in

        :param time: time to read in data
        """
        try:
            from netCDF4 import Dataset
        except Exception:
            raise ImportError("Cannot load netcdf file")

        netcdf = Dataset(ncfile, "r")

        rootd = netcdf.groups['epm']

        try:
            _psi = np.transpose(rootd.groups['output'].groups['profiles2D'].variables['poloidalFlux'], (0, 2, 1))
            _r = rootd.groups['output'].groups['profiles2D'].variables['r']
            _z = rootd.groups['output'].groups['profiles2D'].variables['z']
            _radius = rootd.groups['output'].groups['radialProfiles'].variables['r']
            _bVac = rootd.groups['input'].variables['bVacRadiusProduct']
            _ppres = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['staticPressure']
            _rppres = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['rotationalPressure']
            _qprof = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['q']
            _ffprim = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['ffPrime']
            _pprime = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['staticPPrime']
            _fpol = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['rBphi']
            _psipr = rootd.groups['output'].groups['fluxFunctionProfiles'].variables['normalizedPoloidalFlux']
            _psi_axis = rootd.groups['output'].groups['globalParameters'].variables['psiAxis']
            _psi_bnd = rootd.groups['output'].groups['globalParameters'].variables['psiBoundary']
            _cpasma = rootd.groups['output'].groups['globalParameters'].variables['plasmaCurrent']
            _raxis = rootd.groups['output'].groups['globalParameters'].groups['magneticAxis'].variables['R']
            _zaxis = rootd.groups['output'].groups['globalParameters'].groups['magneticAxis'].variables['Z']
            _rlim = rootd.groups['input'].groups['limiter'].variables['rValues']
            _zlim = rootd.groups['input'].groups['limiter'].variables['zValues']
            _rbbbs = rootd.groups['output'].groups['separatrixGeometry'].variables['rBoundary']
            _zbbbs = rootd.groups['output'].groups['separatrixGeometry'].variables['zBoundary']

            self._timenc = np.array(rootd.variables['time'])

            tind = np.abs(self._timenc - time).argmin()

            # case
            self['CASE'] = ['EFIT++  ', device, ' #%6d' % shot, ' #%4dms' % int(time * 1000), '        ', '        ']

            # Define global parameters
            specs = utils_fusion.device_specs(device=device)

            check = np.isfinite(_psi_axis[tind])
            if not check:
                print("Skipping time slice: EFIT++ failed to converge for timeslice: ", time)
                self.status = False
                return
            # scalars
            self['NW'] = len(_r)
            self['NH'] = len(_z)
            self['RDIM'] = max(_r) - min(_r)
            self['ZDIM'] = max(_z) - min(_z)
            self['RLEFT'] = min(_r)
            self['ZMID'] = (max(_z) + min(_z)) / 2.0
            self['RCENTR'] = specs['R0']
            self['BCENTR'] = _bVac[tind] / specs['R0']
            self['CURRENT'] = _cpasma[tind]
            self['RMAXIS'] = _raxis[tind]
            self['ZMAXIS'] = _zaxis[tind]
            self['SIMAG'] = _psi_axis[tind]
            self['SIBRY'] = _psi_bnd[tind]

            # 1d quantiites
            self['PRES'] = _ppres[tind, :]
            self['QPSI'] = _qprof[tind, :]
            self['FPOL'] = _fpol[tind, :]
            self['FFPRIM'] = _ffprim[tind, :]
            self['PPRIME'] = _pprime[tind, :]

            # 2d quantities
            self['PSIRZ'] = _psi[tind, :, :]

            # limiter
            self['RLIM'] = _rlim[:]
            self['ZLIM'] = _zlim[:]
            self['LIMITR'] = len(self['RLIM'])

            # lcfs
            self['RBBBS'] = _rbbbs[tind]
            self['ZBBBS'] = _zbbbs[tind]
            self['NBBBS'] = len(_zbbbs[tind])

            # cocosify to have AuxQuantities and fluxSurfaces created properly
            self._cocos = 7
            self.cocosify(1, calcAuxQuantities=True, calcFluxSurfaces=True)
            self.add_rhovn()
            self.status = True
        finally:
            netcdf.close()

        return self

    def from_aug_sfutils(self, shot=None, time=None, eq_shotfile='EQI'):
        """
        Fill in gEQDSK data from aug_sfutils, which processes magnetic equilibrium
        results from the AUG CLISTE code.

        Note that this function requires aug_sfutils to be locally installed
        (pip install aug_sfutils will do). Users also need to have access to the
        AUG shotfile system.

        :param shot: AUG shot number from which to read data

        :param time: time slice from which to read data

        :param eq_shotfile: equilibrium reconstruction to fetch (EQI, EQH, IDE, ...)

        :return: self
        """

        if shot is None:
            raise ValueError('Must specify shot')
        if time is None:
            raise ValueError('Must specify time')

        try:
            import aug_sfutils as sf
        except ImportError as e:
            raise ImportError('aug_sfutils does not seem to be installed: ' + str(e))

        # Reading equilibrium into a class
        eqm = sf.EQU(shot, diag=eq_shotfile)  # reads AUG equilibrium into a class

        # get start point for geqdsk dictionary from aug_sfutils
        geq = sf.to_geqdsk(eqm, t_in=time)

        # now  fill up OMFITgeqdsk object
        self.update(geq)

        # a few extra things to enable greater use of omfit_eqdsk
        self.add_rhovn()

        # ensure correct cocos and then calculate extra quantities
        self._cocos = eqm.cocos
        self.cocosify(1, calcAuxQuantities=True, calcFluxSurfaces=True)  # set to cocos=1

        return self


def gEQDSK_COCOS_identify(bt, ip):
    """
    Returns the native COCOS that an unmodified gEQDSK would obey, defined by sign(Bt) and sign(Ip)
    In order for psi to increase from axis to edge and for q to be positive:
    All use sigma_RpZ=+1 (phi is counterclockwise) and exp_Bp=0 (psi is flux/2.*pi)
    We want
    sign(psi_edge-psi_axis) = sign(Ip)*sigma_Bp > 0  (psi always increases in gEQDSK)
    sign(q) = sign(Ip)*sign(Bt)*sigma_rhotp > 0      (q always positive in gEQDSK)
    ::
        ============================================
        Bt    Ip    sigma_Bp    sigma_rhotp    COCOS
        ============================================
        +1    +1       +1           +1           1
        +1    -1       -1           -1           3
        -1    +1       +1           -1           5
        -1    -1       -1           +1           7
    """
    COCOS = define_cocos(1)

    # get sign of Bt and Ip with respect to CCW phi
    sign_Bt = int(COCOS['sigma_RpZ'] * np.sign(bt))
    sign_Ip = int(COCOS['sigma_RpZ'] * np.sign(ip))
    g_cocos = {
        (+1, +1): 1,  # +Bt, +Ip
        (+1, -1): 3,  # +Bt, -Ip
        (-1, +1): 5,  # -Bt, +Ip
        (-1, -1): 7,  # -Bt, -Ip
        (+1, 0): 1,  # +Bt, No current
        (-1, 0): 3,
    }  # -Bt, No current
    return g_cocos.get((sign_Bt, sign_Ip), None)


OMFITgeqdsk.volume_integral.__doc__ = fluxSurfaces.volume_integral.__doc__
OMFITgeqdsk.surface_integral.__doc__ = fluxSurfaces.surface_integral.__doc__


############################
# A-FILE CLASS OMFITaeqdsk #
############################
class OMFITaeqdsk(SortedDict, OMFITascii):
    r"""
    class used to interface A files generated by EFIT

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self, caseInsensitive=True, sorted=True)
        self.dynaLoad = True

    @dynaLoad
    def load(self, **kw):
        """
        Method used to read a-files
        """
        if self.filename is None or not os.stat(self.filename).st_size:
            return

        f1040 = fortranformat.FortranRecordReader('1x,4e16.9')
        f1041 = fortranformat.FortranRecordReader('1x,4i5')
        f1060 = fortranformat.FortranRecordReader('A1,f8.3,9x,i5,11x,i5,1x,a3,1x,i3,1x,i3,1x,a3,1x,2i5')

        def read_f1040(input_str):
            try:
                return f1040.read(input_str)
            except Exception:
                return [0.0] * 4

        self.clear()

        # use this class as iterator for debugging
        class AFILE_dbg(object):
            def __init__(self, obj):
                self.obj = obj
                self.k = 0

            def __iter__(self):
                return self

            def __next__(self):
                tmp = self.obj[self.k]
                self.k += 1
                print(tmp.rstrip())
                return tmp

        with open(self.filename, 'r') as f:
            AFILE = iter(f.readlines())

        self['__header__'] = ''
        k = 0
        for line in AFILE:
            if line[0] == '*':
                break
            else:
                self['__header__'] += line
                if k == 1:
                    self['shot'] = int(line[:7])
                k += 1
        try:

            (
                dummy,
                self['time'],
                self['jflag'],
                self['lflag'],
                self['limloc'],
                self['mco2v'],
                self['mco2r'],
                self['qmflag'],
                self['nlold'],
                self['nlnew'],
            ) = f1060.read(line)

        except Exception:

            (
                self['jflag'],
                self['lflag'],
                self['limloc'],
                self['mco2v'],
                self['mco2r'],
                self['qmflag'],
                self['nlold'],
                self['nlnew'],
            ) = line.split()[1:]
            ee('bad time in aEQDSK file: %s' % (self.filename))
            self['time'] = 0
            for k in ['jflag', 'lflag', 'mco2v', 'mco2r', 'nlold', 'nlnew']:
                self[k] = int(self[k])

        for k in ['nlold', 'nlnew']:
            if self[k] is None:
                self[k] = 0

        self['rseps'] = np.zeros(2)
        self['zseps'] = np.zeros(2)

        # fmt: off
        self['tsaisq'],   self['rcencm'],   self['bcentr'],   self['pasmat']   = read_f1040(next(AFILE))
        self['cpasma'],   self['rout'],     self['zout'],     self['aout']     = read_f1040(next(AFILE))
        self['eout'],     self['doutu'],    self['doutl'],    self['vout']     = read_f1040(next(AFILE))
        self['rcurrt'],   self['zcurrt'],   self['qsta'],     self['betat']    = read_f1040(next(AFILE))
        self['betap'],    self['ali'],      self['oleft'],    self['oright']   = read_f1040(next(AFILE))
        self['otop'],     self['obott'],    self['qpsib'],    self['vertn']    = read_f1040(next(AFILE))
        # fmt: on

        for arr, adim in (('rco2v', 'mco2v'), ('dco2v', 'mco2v'), ('rco2r', 'mco2r'), ('dco2r', 'mco2r')):
            tmp = []
            for k in range(int(np.ceil(self[adim] / 4.0))):
                tmp.extend(read_f1040(next(AFILE)))
            self[arr] = tmp[: self[adim]]

        # fmt: off
        self['shearb'],   self['bpolav'],   self['s1'],       self['s2']       = read_f1040(next(AFILE))
        self['s3'],       self['qout'],     self['olefs'],    self['orighs']   = read_f1040(next(AFILE))
        self['otops'],    self['sibdry'],   self['areao'],    self['wplasm']   = read_f1040(next(AFILE))
        self['terror'],   self['elongm'],   self['qqmagx'],   self['cdflux']   = read_f1040(next(AFILE))
        self['alpha'],    self['rttt'],     self['psiref'],   self['xndnt']    = read_f1040(next(AFILE))
        self['rseps'][0], self['zseps'][0], self['rseps'][1], self['zseps'][1] = read_f1040(next(AFILE))
        self['sepexp'], self['obots'], self['btaxp'], self['btaxv'] = read_f1040(next(AFILE))
        self['aaq1'], self['aaq2'], self['aaq3'], self['seplim'] = read_f1040(next(AFILE))
        self['rmagx'], self['zmagx'], self['simagx'], self['taumhd'] = read_f1040(next(AFILE))
        self['betapd'], self['betatd'], self['wplasmd'], self['diamag'] = read_f1040(next(AFILE))
        self['vloopt'], self['taudia'], self['qmerci'], self['tavem'] = read_f1040(next(AFILE))

        self['nsilop0'],  self['magpri0'],  self['nfcoil0'],  self['nesum0']   = f1041.read(next(AFILE))
        # fmt: on

        tmp = []
        for k in range(int(np.ceil((self['nsilop0'] + self['magpri0']) / 4.0))):
            tmp.extend(read_f1040(next(AFILE)))
        self['csilop'] = tmp[: self['nsilop0']]
        self['cmpr2'] = tmp[self['nsilop0'] : (self['nsilop0'] + self['magpri0'])]

        self['ccbrsp'] = []
        for k in range(int(np.ceil((self['nfcoil0']) / 4.0))):
            self['ccbrsp'].extend(read_f1040(next(AFILE)))

        self['eccurt'] = []
        for k in range(int(np.ceil((self['nesum0']) / 4.0))):
            self['eccurt'].extend(read_f1040(next(AFILE)))

        try:
            # fmt: off
            # Machine specific ?
            self['pbinj'],  self['rvsin'],   self['zvsin'],   self['rvsout']  = read_f1040(next(AFILE))
            self['zvsout'], self['vsurfa'],  self['wpdot'],   self['wbdot']   = read_f1040(next(AFILE))
            self['slantu'], self['slantl'],  self['zuperts'], self['chipre']  = read_f1040(next(AFILE))
            self['cjor95'], self['pp95'],    self['ssep'],    self['yyy2']    = read_f1040(next(AFILE))
            self['xnnc'],   self['cprof'],   self['oring'],   self['cjor0']   = read_f1040(next(AFILE))
            self['fexpan'], self['qqmin'],   self['chigamt'], self['ssi01']   = read_f1040(next(AFILE))
            self['fexpvs'], self['sepnose'], self['ssi95'],   self['rqqmin']  = read_f1040(next(AFILE))
            self['cjor99'], self['cj1ave'],  self['rmidin'],  self['rmidout'] = read_f1040(next(AFILE))
            self['psurfa'], self['peak'],    self['dminux'],  self['dminlx']  = read_f1040(next(AFILE))
            self['dolubaf'],self['dolubafm'],self['diludom'], self['diludomm']= read_f1040(next(AFILE))
            self['ratsol'], self['rvsiu'],   self['zvsiu'],   self['rvsid']   = read_f1040(next(AFILE))
            self['zvsid'],  self['rvsou'],   self['zvsou'],   self['rvsod']   = read_f1040(next(AFILE))
            self['zvsod'],  self['condno'],  self['psin32'],  self['psin21']  = read_f1040(next(AFILE))
            self['rq32in'], self['rq21top'], self['chilibt'], self['ali3']    = read_f1040(next(AFILE))
            self['xbetapr'],self['tflux'],   self['tchimls'], self['twagap']  = read_f1040(next(AFILE))
            # fmt: on
        except StopIteration as _excp:
            pass

        # anything extra go in the footer
        self['__footer__'] = ''
        try:
            for line in AFILE:
                self['__footer__'] += line
        except Exception:
            pass

        # add betaN calculation to a-file
        # if it is not a vacuum shot
        if self['cpasma'] != 0.0:
            i = self['cpasma'] / 1e6
            a = self['aout'] / 100.0
            bt = self['bcentr'] * self['rcencm'] / self['rout']
            i_n = i / a / bt
            self['betan'] = abs(self['betat'] / i_n)

        # lists into arrays
        for var in self:
            if isinstance(self[var], list):
                self[var] = np.array([_f for _f in self[var] if _f is not None])

        # remove NaN from aEQDSK file to allow saving
        for k in self:
            if isinstance(self[k], np.ndarray) and np.any(np.isnan(self[k])):
                self[k][np.isnan(self[k])] = 0
                printe('%s array is NaN in aEQDSK file: %s' % (k, self.filename))
            elif is_float(self[k]) and np.any(tolist(np.isnan(self[k]))):
                self[k] = 0
                printe('%s entry is NaN in aEQDSK file: %s' % (k, self.filename))

    @dynaSave
    def save(self):
        """
        Method used to write a-files
        """

        def write_f1040(list_4_items):
            if not np.all([tolist(k)[0] in self for k in list_4_items]):
                return ''
            list_4_values = []
            for item in list_4_items:
                if not isinstance(item, str):
                    list_4_values.append(self.get(item[0], [0.0] * item[1])[item[1]])
                else:
                    list_4_values.append(self.get(item, 0.0))
            return f1040.write(list_4_values) + '\n'

        f1040 = fortranformat.FortranRecordWriter('1x,4e16.9')
        f1041 = fortranformat.FortranRecordWriter('1x,4i5')
        f1060 = fortranformat.FortranRecordWriter('A1,f8.3,9x,i5,11x,i5,1x,a3,1x,i3,1x,i3,1x,a3,1x,2i5')

        tmp = self['__header__'].split('\n')
        tmps = tmp[0] + '\n'
        tmps += '%7d' % self['shot'] + tmp[1][7:] + '\n'
        tmps += fortranformat.FortranRecordWriter('1x,e16.9').write([self['time']]) + '\n'

        tmps += (
            f1060.write(
                [
                    '*',
                    self['time'],
                    self['jflag'],
                    self['lflag'],
                    self['limloc'],
                    self['mco2v'],
                    self['mco2r'],
                    self['qmflag'],
                    self['nlold'],
                    self['nlnew'],
                ]
            )
            + '\n'
        )

        tmps += write_f1040(['tsaisq', 'rcencm', 'bcentr', 'pasmat'])
        tmps += write_f1040(['cpasma', 'rout', 'zout', 'aout'])
        tmps += write_f1040(['eout', 'doutu', 'doutl', 'vout'])
        tmps += write_f1040(['rcurrt', 'zcurrt', 'qsta', 'betat'])
        tmps += write_f1040(['betap', 'ali', 'oleft', 'oright'])
        tmps += write_f1040(['otop', 'obott', 'qpsib', 'vertn'])

        for arr, adim in (('rco2v', 'mco2v'), ('dco2v', 'mco2v'), ('rco2r', 'mco2r'), ('dco2r', 'mco2r')):
            for k in range(int(np.ceil(self[adim] / 4.0))):
                tmps += f1040.write(self[arr][k * 4 : (k + 1) * 4]) + '\n'

        tmps += write_f1040(['shearb', 'bpolav', 's1', 's2'])
        tmps += write_f1040(['s3', 'qout', 'olefs', 'orighs'])
        tmps += write_f1040(['otops', 'sibdry', 'areao', 'wplasm'])
        tmps += write_f1040(['terror', 'elongm', 'qqmagx', 'cdflux'])
        tmps += write_f1040(['alpha', 'rttt', 'psiref', 'xndnt'])
        tmps += write_f1040([('rseps', 0), ('zseps', 0), ('rseps', 1), ('zseps', 1)])
        tmps += write_f1040(['sepexp', 'obots', 'btaxp', 'btaxv'])
        tmps += write_f1040(['aaq1', 'aaq2', 'aaq3', 'seplim'])
        tmps += write_f1040(['rmagx', 'zmagx', 'simagx', 'taumhd'])
        tmps += write_f1040(['betapd', 'betatd', 'wplasmd', 'diamag'])
        tmps += write_f1040(['vloopt', 'taudia', 'qmerci', 'tavem'])

        tmps += f1041.write([self['nsilop0'], self['magpri0'], self['nfcoil0'], self['nesum0']]) + '\n'

        tmp = np.hstack((self['csilop'], self['cmpr2']))
        for k in range(int(np.ceil((self['nsilop0'] + self['magpri0']) / 4.0))):
            tmps += f1040.write(tmp[k * 4 : (k + 1) * 4]) + '\n'

        for k in range(int(np.ceil((self['nfcoil0']) / 4.0))):
            tmps += f1040.write(self['ccbrsp'][k * 4 : (k + 1) * 4]) + '\n'

        for k in range(int(np.ceil((self['nesum0']) / 4.0))):
            tmps += f1040.write(self['eccurt'][k * 4 : (k + 1) * 4]) + '\n'

        tmps += write_f1040(['pbinj', 'rvsin', 'zvsin', 'rvsout'])
        tmps += write_f1040(['zvsout', 'vsurfa', 'wpdot', 'wbdot'])
        tmps += write_f1040(['slantu', 'slantl', 'zuperts', 'chipre'])
        tmps += write_f1040(['cjor95', 'pp95', 'ssep', 'yyy2'])
        tmps += write_f1040(['xnnc', 'cprof', 'oring', 'cjor0'])
        tmps += write_f1040(['fexpan', 'qqmin', 'chigamt', 'ssi01'])
        tmps += write_f1040(['fexpvs', 'sepnose', 'ssi95', 'rqqmin'])
        tmps += write_f1040(['cjor99', 'cj1ave', 'rmidin', 'rmidout'])
        tmps += write_f1040(['psurfa', 'peak', 'dminux', 'dminlx'])
        tmps += write_f1040(['dolubaf', 'dolubafm', 'diludom', 'diludomm'])
        tmps += write_f1040(['ratsol', 'rvsiu', 'zvsiu', 'rvsid'])
        tmps += write_f1040(['zvsid', 'rvsou', 'zvsou', 'rvsod'])
        tmps += write_f1040(['zvsod', 'condno', 'psin32', 'psin21'])
        tmps += write_f1040(['rq32in', 'rq21top', 'chilibt', 'ali3'])
        tmps += write_f1040(['xbetapr', 'tflux', 'tchimls', 'twagap'])

        tmps += self['__footer__']
        with open(self.filename, 'w') as f:
            f.write(tmps)

    def from_mdsplus(
        self,
        device=None,
        shot=None,
        time=None,
        exact=False,
        SNAPfile='EFIT01',
        time_diff_warning_threshold=10,
        fail_if_out_of_range=True,
        show_missing_data_warnings=True,
        quiet=False,
    ):
        """
        Fill in aEQDSK data from MDSplus

        :param device: The tokamak that the data correspond to ('DIII-D', 'NSTX', etc.)

        :param shot: Shot number from which to read data

        :param time: time slice from which to read data

        :param exact: get data from the exact time-slice

        :param SNAPfile: A string containing the name of the MDSplus tree to connect to, like 'EFIT01', 'EFIT02', 'EFIT03', ...

        :param time_diff_warning_threshold: raise error/warning if closest time slice is beyond this treshold

        :param fail_if_out_of_range: Raise error or warn if closest time slice is beyond time_diff_warning_threshold

        :param show_missing_data_warnings: Print warnings for missing data

        :param quiet: verbosity

        :return: self
        """

        if device is None:
            raise ValueError('Must specify device')
        if shot is None:
            raise ValueError('Must specify shot')
        if time is None:
            raise ValueError('Must specify time')

        tmp = from_mds_plus(
            device=device,
            shot=shot,
            times=[time],
            exact=exact,
            snap_file=SNAPfile,
            time_diff_warning_threshold=time_diff_warning_threshold,
            fail_if_out_of_range=fail_if_out_of_range,
            get_afile=True,
            show_missing_data_warnings=show_missing_data_warnings,
            debug=False,
            quiet=quiet,
        )['aEQDSK'][time]

        self.__dict__ = tmp.__dict__
        self.update(tmp)

        return self


############################
# M-FILE CLASS OMFITmeqdsk #
############################
class OMFITmeqdsk(OMFITnc):
    r"""
    class used to interface M files generated by EFIT
    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """
    signal_info = {  # Calc   measured   weight  uncert short_desc letter
        'mag': ['cmpr2', 'expmpi', 'fwtmp2', None, 'magnetics', 'm'],  # Magnetic probes
        'ecc': ['cecurr', 'eccurt', 'fwtec', None, 'E-coil current', 'e'],  # E-coil currents
        'fcc': ['ccbrsp', 'fccurt', 'fwtfc', None, 'F-coil current', 'f'],  # F-coil currents
        'lop': ['csilop', 'silopt', 'fwtsi', None, 'flux loops', 'l'],  # Flux loops
        'pre': ['cpress', 'pressr', None, 'sigpre', 'pressure', 'p'],  # Pressure constraint
        'xxj': ['aux_calxxj', 'aux_mxxj', 'aux_fwtxxj', 'aux_sigxxj', 'current density', 'j'],  # Current density
        'gam': ['cmgam', 'tangam', None, 'siggam', 'MSE tan(gamma)', 'g'],  # MSE tan(gamma)
    }

    def __init__(self, filename, **kw):
        OMFITnc.__init__(self, filename, **kw)

    def pack_it(self, x, tag, name, dim1=None, is_tmp=True):
        """
        Utility function for saving results into the mEQDSK as new OMFITncData instances.
        :param x: array of data to pack

        :param tag: string (SHORT: dictionary key is derived from this)

        :param name: string (LONG: this is a description that goes in a field)

        :param dim1: string or None: name of dimension other than time

        :param is_tmp: bool: Choose OMFITncDataTmp() instead of OMFITncData() to prevent saving
        """
        from omfit_classes.omfit_nc import OMFITncData, OMFITncDataTmp

        self[tag] = OMFITncDataTmp() if is_tmp else OMFITncData()
        self[tag]['data'] = np.array([x])
        self[tag]['long_name'] = name
        self[tag]['__dtype__'] = np.dtype(type(np.atleast_1d(x).flatten()[0]))
        self[tag]['__dimensions__'] = ('dim_time', dim1) if dim1 is not None else ('dim_time',)
        return

    def _get_signal_info(self, which):
        """Utility for pulling out signal_info while doing some checks; returns a list of items which are str or None"""
        info = self.signal_info.get(which, None)
        if info is None:
            printw('FAIL: Unrecognized normality test base quantity: {}'.format(which))
            return None
        if info[0] not in self:
            printw('FAIL: {} not found. Unable to perform residual normality test.'.format(info[0]))
            if info[0].startswith('aux_'):
                printw('This an an auxiliary quantity. You must extend the mEQDSK before you can analyze it.')
            return None
        return info

    def residual_normality_test(self, which='mag', is_tmp='some'):
        """
        Tests whether residuals conform to normal distribution and saves a P-value.
        A good fit should have random residuals following a normal distribution (due to random measurement errors
        following a normal distribution). The P-value assesses the probability that the distribution of residuals could
        be at least as far from a normal distribution as are the measurements. A low P-value is indicative of a bad
        model or some other problem.
        https://www.graphpad.com/guides/prism/5/user-guide/prism5help.html?reg_diagnostics_tab_5_3.htm
        https://www.graphpad.com/support/faqid/1577/

        :param which: string
            Parameter to do test on. Options: ['mag', 'ecc', 'fcc', 'lop', 'gam', 'pre', 'xxj']

        :param is_tmp: string
            How many of the stats quantities should be loaded as OMFITncDataTmp (not saved to disk)?
            'some', 'none', or 'all'
        """

        if which in ['pre', 'xxj']:
            printw(
                'WARNING: The test for normality of residual distribution for {} has been requested, but this '
                'quantity is an input constraint, not a measurement. Deviation between model and constraint is '
                'probably not due to normally distributed random errors in the constraint profile, so this test is '
                'not meaningful.'.format(which)
            )
            naughty = ' This test is probably not meaningful for this quantity and should be ignored.'
        else:
            naughty = ''

        info = self._get_signal_info(which)
        if info is None:
            return
        calc = self[info[0]]['data'][0]
        meas = self[info[1]]['data'][0]
        if info[2] is None:
            uncert = self[info[3]]['data'][0]
            weight = np.zeros(len(uncert))
            weight[uncert > 0] = 1.0 / uncert[uncert > 0]
        else:
            weight = self[info[2]]['data'][0]
        if np.all(weight == 0):
            printd('Skipping {} because all 0s'.format(which))
            return
        if len(np.atleast_1d(weight)) == 1:
            weight = np.atleast_1d(weight)[0] * np.ones(np.shape(meas))
        residual = (meas - calc) * weight
        residual[weight <= 0] = np.NaN

        fwt_flag = self[info[2]]['data'][0] if info[2] is not None else None
        if fwt_flag is None:
            pass
        elif len(np.atleast_1d(fwt_flag)) == len(residual):
            residual[fwt_flag <= 0] = np.NaN
        elif (len(np.atleast_1d(fwt_flag)) == 1) and (np.atleast_1d(fwt_flag) <= 0):
            residual[:] = np.NaN

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            try:
                normalstat, p_value = scipy.stats.normaltest(residual[weight > 0])
            except ValueError as exc:
                printw('WARNING: residual normality test failed for {}: {}'.format(which, exc))
                normalstat = p_value = np.NaN
            if np.any([str(wa.message).startswith('kurtosistest only valid') for wa in w]):
                # Make probability negative to indicate invalid test
                p_value *= -1
                printd('Invalid result for p value of mag replicates')

        self.pack_it(
            residual.astype(np.float),
            'stats_resid{}'.format(info[5]),
            'Residual between {} and calculation'.format(info[4]),
            self[info[0]]['__dimensions__'][1],
            is_tmp=is_tmp != 'none',
        )
        self.pack_it(
            normalstat,
            'stats_nrs{}'.format(which),
            'Combined normality statistic for {} residual, based on skewness and kurtosis.{}'.format(info[4], naughty),
            is_tmp=is_tmp != 'none',
        )
        self.pack_it(
            p_value,
            'stats_nrp{}'.format(which),
            'P-value for normality of {} residuals: probability that residuals would be at least this far '
            'from normal distribution assuming correct model and actual measurements.{}'.format(info[4], naughty),
            is_tmp=is_tmp == 'all',
        )
        return

    def rsq_test(self, which='mag', is_tmp='some'):
        """
        Calculates R^2 value for fit to a category of signals (like magnetics).
        The result will be saved into the mEQDSK instance as stats_rsq***. R^2 measures the fraction of variance in the
        data which is explained by the model and can range from 1 (model explains data) through 0 (model does no better
        than a flat line through the average) to -1 (model goes exactly the wrong way).
        https://www.graphpad.com/guides/prism/5/user-guide/prism5help.html?reg_diagnostics_tab_5_3.htm

        :param which: string (See residual_normality_test doc)

        :param is_tmp: string (See residual_normality_test doc)
        """
        info = self._get_signal_info(which)
        if info is None:
            return
        calc = self[info[0]]['data'][0]
        meas = self[info[1]]['data'][0]
        fwt = self[info[2]]['data'][0] if info[2] is not None else None
        if fwt is not None and len(np.atleast_1d(fwt)) < len(calc):
            # Handle weird stuff like scalar weight for current density (FWTXXJ)
            fwt = np.atleast_1d(fwt)[0] * np.ones(len(calc))
        uncert = self[info[3]]['data'][0] if info[3] is not None else None
        mask = np.ones(len(calc), bool)
        mask *= (fwt > 0) if fwt is not None else True
        mask *= (uncert > 0) if uncert is not None else True
        if uncert is not None:
            uncert_bad = uncert <= 0
            uncert_nz = copy.copy(uncert)
            uncert_nz[uncert_bad] = 1
            weight = 1.0 / uncert_nz
            weight[uncert_bad] = 0
            weight = weight[mask]
        else:
            weight = fwt[mask] if fwt is not None else 1

        if np.any(np.atleast_1d(mask)):
            sstot = np.sum(((meas[mask] - np.mean(meas[mask])) * weight) ** 2)
            ssres = np.sum(((meas[mask] - calc[mask]) * weight) ** 2)
            rsq = 1.0 - ssres / sstot
        else:
            sstot = ssres = np.NaN
            rsq = np.NaN

        self.pack_it(
            np.float32(sstot),
            'stats_sst{}'.format(which),
            'Sum of Squares, Total, for {}. Used for R^2 calc.'.format(info[4]),
            is_tmp=is_tmp != 'none',
        )
        self.pack_it(
            np.float32(ssres),
            'stats_ssr{}'.format(which),
            'Sum of Squares, Residual, for {}. Used for R^2 calc.'.format(info[4]),
            is_tmp=is_tmp != 'none',
        )
        self.pack_it(
            np.float32(rsq),
            'stats_rsq{}'.format(which),
            'R^2 of fit to {}: fraction of variance in {} explained by model'.format(info[4], info[4]),
            is_tmp=is_tmp == 'all',
        )
        return

    def combo_rsq_tests(self, is_tmp='some'):
        """
        Combined R^2 from various groups of signals, including 'all'.
        Needs stats_sst* and stats_ssr* and will call rsq_test to make them if not already available.

        :param is_tmp: string (See residual_normality_test doc)
        """
        groups = {
            'all': self.signal_info.keys(),
            'alm': ['mag', 'lop', 'ecc', 'fcc'],
            'mes': ['mag', 'lop', 'gam', 'ecc', 'fcc'],
            'con': ['pre', 'xxj'],
            'coi': ['ecc', 'fcc'],
        }
        descriptions = {
            'all': 'all input data',
            'alm': 'all magnetics data (probes, flux loops, coils)',
            'mes': 'all direct measurements (excluding kinetic constraint profiles)',
            'con': 'all kinetic constraint profiles',
            'coi': 'all coil currents',
        }
        for group, items in groups.items():
            sst = 0
            ssr = 0
            for item in items:
                sst_sig, ssr_sig = 'stats_sst{}'.format(item), 'stats_ssr{}'.format(item)
                if sst_sig not in self or ssr_sig not in self:
                    self.rsq_test(which=item, is_tmp=is_tmp)
                sst_inc = self.get(sst_sig, {}).get('data', [0])[0]
                ssr_inc = self.get(ssr_sig, {}).get('data', [0])[0]
                if (not np.isnan(sst_inc)) and (not np.isnan(ssr_inc)):
                    sst += sst_inc
                    ssr += ssr_inc
            rsq = (1.0 - ssr / sst) if sst > 0 else np.NaN  # TODO: is NaN allowed, or should I just use 0 or -100?
            self.pack_it(
                np.float32(rsq),
                'stats_rsq{}'.format(group),
                'R^2 of fit to {}: fraction of variance explained by model'.format(descriptions[group]),
                is_tmp=is_tmp == 'all',
            )

    def plot(self, **kw):
        """
        Function used to plot chisquares stored in m-files
        This method is called by .plot() when the object is a m-file
        """
        fig = pyplot.gcf()
        quants = ['saipre', 'saisil', 'saimpi', 'chigam']
        kw.setdefault('marker', 'o')
        kw.setdefault('linestyle', '')
        for qi, q in enumerate(quants):
            ax = fig.add_subplot(2, 2, qi + 1)
            data = self[q]['data'].flatten()
            ax.plot(list(range(1, len(data) + 1)), data, label='$\\chi^2_{\\rm tot}=%3.3g$' % (np.sum(data)), **kw)
            ax.set_title(self[q]['long_name'])
            if qi in [2, 3]:
                ax.set_xlabel('Constraint number')
            if qi in [0, 2]:
                ax.set_ylabel('$\\chi^2$')
            try:
                pyplot.legend(labelspacing=0.1, loc=0).draggable(state=True)
            except Exception:
                pass

    @dynaLoad
    def to_omas(self, ods=None, time_index=0, time_index_efit=0):
        """
        translate mEQDSK class to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added to ods

        :param time_index_efit: time index from mEQDSK

        :return: ODS
        """

        if ods is None:
            ods = ODS()

        with omas_environment(ods, cocosio=1):

            constr = ods['equilibrium.time_slice'][time_index]['constraints']

            # Magnetic probes
            if 'saimpi' in self:
                nconstr = len(self['saimpi']['data'][time_index_efit, :])
                for i in range(nconstr):
                    constr['bpol_probe'][i]['chi_squared'] = self['saimpi']['data'][time_index_efit, i]
                    constr['bpol_probe'][i]['measured'] = self['expmpi']['data'][time_index_efit, i]
                    constr['bpol_probe'][i]['reconstructed'] = self['cmpr2']['data'][time_index_efit, i]
                    constr['bpol_probe'][i]['weight'] = self['fwtmp2']['data'][time_index_efit, i]
                    constr['bpol_probe'][i]['exact'] = 0

            # MSE signal
            # Is arctan correct translation of signal?
            # Even if it is, chi^2 probably needs to be recalculated
            if 'chigam' in self:
                nconstr = len(self['chigam']['data'][time_index_efit, :])
                for i in range(nconstr):
                    constr['mse_polarisation_angle'][i]['chi_squared'] = self['chigam']['data'][time_index_efit, i]
                    constr['mse_polarisation_angle'][i]['measured'] = np.arctan(self['tangam']['data'][time_index_efit, i])
                    constr['mse_polarisation_angle'][i]['reconstructed'] = np.arctan(self['cmgam']['data'][time_index_efit, i])
                    constr['mse_polarisation_angle'][i]['weight'] = self['fwtgam']['data'][time_index_efit, i]
                    constr['mse_polarisation_angle'][i]['exact'] = 0

            # PSI loops
            nconstr = len(self['saisil']['data'][time_index_efit, :])
            if 'saisil' in self:
                for i in range(nconstr):
                    constr['flux_loop'][i]['chi_squared'] = self['saisil']['data'][time_index_efit, i]
                    constr['flux_loop'][i]['measured'] = self['silopt']['data'][time_index_efit, i]
                    constr['flux_loop'][i]['reconstructed'] = self['csilop']['data'][time_index_efit, i]
                    constr['flux_loop'][i]['weight'] = self['fwtsi']['data'][time_index_efit, i]
                    constr['flux_loop'][i]['exact'] = 0

            # Pressure profile
            if 'cpress' in self:
                nconstr = len(self['cpress']['data'][time_index_efit])
                for i in range(nconstr):
                    constr['pressure'][i]['chi_squared'] = self['saipre']['data'][time_index_efit, i]
                    constr['pressure'][i]['measured'] = self['pressr']['data'][time_index_efit, i]
                    constr['pressure'][i]['reconstructed'] = self['cpress']['data'][time_index_efit, i]
                    constr['pressure'][i]['exact'] = 0

            # E-coils
            if 'eccurt' in self:
                nconstr = len(self['eccurt']['data'][time_index_efit])
                icoil = 0
                for i in range(nconstr):
                    constr['pf_current'][icoil]['measured'] = self['eccurt']['data'][time_index_efit, i]
                    constr['pf_current'][icoil]['reconstructed'] = self['cecurr']['data'][time_index_efit, i]
                    constr['pf_current'][icoil]['weight'] = self['fwtec']['data'][time_index_efit, i]
                    icoil += 1

            # F-coils

            if 'fccurt' in self:
                nconstr = len(self['fccurt']['data'][time_index_efit])
                for i in range(nconstr):
                    constr['pf_current'][icoil]['measured'] = self['fccurt']['data'][time_index_efit, i]
                    constr['pf_current'][icoil]['reconstructed'] = self['ccbrsp']['data'][time_index_efit, i]
                    constr['pf_current'][icoil]['weight'] = self['fwtfc']['data'][time_index_efit, i]
                    icoil += 1

            # ip
            constr['ip.exact'] = 0
            constr['ip.measured'] = self['plasma']['data'][time_index_efit]

            # diamagnetic_flux
            constr['diamagnetic_flux.exact'] = 0
            constr['diamagnetic_flux.measured'] = self['diamag']['data'][time_index_efit]

        return ods


############################
# K-FILE CLASS OMFITkeqdsk #
############################
class OMFITkeqdsk(OMFITnamelist):
    r"""
    class used to interface with K files used by EFIT

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    linecycle = itertools.cycle(['--', '-.', ':'])
    markercycle = itertools.cycle(['d', 'o', '*', 'x', 'p'])

    def __init__(self, filename, **kw):
        kw0 = {}
        kw0['collect_arrays'] = {'__default__': 0}  # Collect arrays to access array data consistently within OMFIT
        kw0['outsideOfNamelistIsComment'] = True
        kw0.update(kw)
        OMFITnamelist.__init__(self, filename, **kw0)  # Takes care of setting up the class attributes
        for k in list(kw0.keys()):
            if k not in list(kw.keys()):
                self.OMFITproperties.pop(k, None)

    @dynaLoad
    def load(self, *args, **kw):
        OMFITnamelist.load(self, *args, **kw)
        self.addAuxQuantities()

    @dynaSave
    def save(self, *args, **kw):
        tmp = None
        if 'AuxQuantities' in self:
            tmp = self['AuxQuantities']
            del self['AuxQuantities']
        try:
            OMFITnamelist.save(self, *args, **kw)
        finally:
            if tmp is not None:
                self['AuxQuantities'] = tmp

    #############
    # Utilities #
    #############
    def remove_duplicates(self, keep_first_or_last='first', update_original=True, make_new_copy=False):
        """
        Searches through all the groups in the k-file namelist (IN1,
        INS,EFITIN, etc.) and deletes duplicated variables. You can keep
        the first instance or the last instance.

        :param keep_first_or_last: string ('first' or 'last')
            - If there are duplicates, only one can be kept. Should it be the first one or the last one?

        :param update_original: bool
            Set False to leave the original untouched during testing. Use with make_new_copy.

        :param make_new_copy: bool
            Create a copy of the OMFITkeqdsk instance and return it. Useful if the original is not being modified.

        :return: None or OMFITkeqdsk instance (depending on make_new_copy)
        """
        already = []  # list of variables we've seen before
        filename = self.filename.split('/')[-1]  # name of current k-file without the whole path
        subnames = [
            k for k in list(self.keys()) if isinstance(self[k], namelist.NamelistName)
        ]  # names of namelist.NamelistNames within the top level namelist
        if make_new_copy:
            new = scratch['new_k_file'] = OMFITnamelist(filename)  # make a new namelist to which we will copy original items
            other_top_level_items = [
                k for k in list(self.keys()) if not isinstance(self[k], namelist.NamelistName)
            ]  # other as in not the namelist.NamelistNames
            for otli in other_top_level_items:
                new[otli] = copy.copy(self[otli])  # copy across top level data/notes (not namelist.NamelistNames)
        else:
            new = None
        if keep_first_or_last.lower() == 'last':
            printd('going backward; the last instance of a tag will be the first one seen so it will be kept')
            direction = -1  # go backward, keeping the last instance of each tag
        else:  # keep_first_or_last=='first'
            printd('going foward; the first instance of a tag will be the first one seen so it will be kept')
            direction = 1  # go forward, keeping the first instance of each tag (default)
        for sn in subnames[::direction]:
            if make_new_copy:
                new[sn] = namelist.NamelistName()  # create sub-namelists
            for k in list(self[sn].keys())[::direction]:
                if not k.lower() in already:
                    if make_new_copy:
                        new[sn][k] = copy.copy(self[sn][k])  # save keys that haven't been seen before
                    already = already + [k.lower()]  # add key to the list of things we've seen already
                    printd('  added {:}/{:}'.format(sn, k))
                else:
                    if update_original:
                        del self[sn][k]  # remove duplicate keys
                    printd('  key {:}/{:} already seen'.format(sn, k))

        if make_new_copy:
            return new
        else:
            return None

    def _combine_namelists(self):
        """
        Combines k-file sub-namelists together so we don't have to deal
        with finding something in IN1 or INWANT, especially because some
        items in INWANT can (apparently?) go in IN1 (is this right?
        Documentation is unclear, but this combo namelist will work either way)

        :return: NamelistName instance
            Combined namelists
        """
        subnames = [k for k in list(self.keys()) if isinstance(self[k], namelist.NamelistName)]

        if len(subnames) > 1:
            combo = self[subnames[0]].copy()
            for sn in subnames[1:]:
                if sn.lower() != 'efitin':  # Exclude efitin because it's just a record of the snap file (I think)
                    combo.update(self[sn])
        else:
            combo = namelist.NamelistName()
        return combo

    ##################
    # Aux quantities #
    ##################
    def addAuxQuantities(self):
        """
        Adds ['AuxQuantities'] to the current object

        :return: SortedDict object containing auxiliary quantities
        """

        self['AuxQuantities'] = self._auxQuantities()

        return self['AuxQuantities']

    def _auxQuantities(self, combo=None):
        """
        Calculate auxiliary quantities based on the k-file contents

        :return: SortedDict object containing some auxiliary quantities
        """

        c = self._combine_namelists() if combo is None else combo
        aux = SortedDict()

        # Fit variables
        nvarys = 0
        # Look up fitting parameters  https://fusion.gat.com/theory/Efitfunc#KPPCUR
        kffcur, kfffnc, kffknt = c.get('KFFCUR', 1), c.get('KFFFNC', 0), c.get('KFFKNT', 0)  # Current density
        kppcur, kppfnc, kppknt = c.get('KPPCUR', 3), c.get('KPPFNC', 0), c.get('KPPKNT', 0)  # Pressure
        kwwcur, kwwfnc, kwwknt = c.get('KWWCUR', 0), c.get('KWWFNC', 0), c.get('KWWKNT', 0)  # Rotation
        nvarys += kffcur if kfffnc == 0 else 2 * kffknt + 1 if kfffnc == 6 else 0
        nvarys += kppcur if kppfnc == 0 else 2 * kppknt + 1 if kppfnc == 6 else 0
        nvarys += 2 * kwwknt + 1 if kwwfnc == 6 else 0

        # Constraints
        nconstrain = 0
        constrain_if_1 = ['FCURBD', 'PCURBD', 'FWTQA', 'FWTCUR']
        for thing in constrain_if_1:  # Logic based on Lao 2005 FST
            nconstrain += int(c.get(thing, 0) == 1)

        # Measurements / input data
        ndata = 0
        for enable_flag in ['FWTMP2', 'FWTSI', 'FWTFC', 'FWTEC', 'FWTGAM', 'FWTPRE', 'FWTPRW']:
            ndata += np.sum(np.atleast_1d(c.get(enable_flag, 0) > -1).astype(int))
        ndata += c.get('FWTXXJ', 0) * len(np.atleast_1d(c.get('VZEROJ', [])))

        # Record
        aux['num_input_data'] = int(ndata)
        aux['num_fit_variables'] = int(nvarys)
        aux['num_hard_constraints'] = int(nconstrain)
        aux['degrees_of_freedom'] = int(ndata - nvarys - nconstrain)
        avg_xxj_uncertainty = 0.1  # J profile is already normalized
        aux['sigxxj'] = np.ones(len(np.atleast_1d(c.get('VZEROJ', [0])))) * avg_xxj_uncertainty
        # TODO: clean up these notes once everything is figured out:
        #     0.1 or 0.01 of current (A) in the cell on axis
        #     would like to have discrepancy in current density be <= 1% of average of J_efit_norm
        #     check chi^2 assuming 1% of average current density

        return aux

    ##################
    # OMAS           #
    ##################
    def from_omas(self, ods, time_index=0, time=None):
        """
        Generate kEQDSK from OMAS data structure.

        Currently this fuction just writes from
           code_parameters. In the future, parameters including ITIME,PLASMA,EXPMP2,COILS,BTOR,DENR,DENV,
           SIREF,BRSP,ECURRT,VLOOP,DFLUX,SIGDLC,CURRC79,CURRC139,CURRC199,CURRIU30,CURRIU90,CURRIU150,
           CURRIL30,CURRIL90, CURRIL150 should be specified from ods raw parameters.

        :param ods: input ods from which data is added

        :param time_index: time index from which data is added to ods

        :param time: time in seconds where to compare the data (if set it superseeds time_index)

        :return: ODS
        """

        if time is not None:
            time_index = np.argmin(np.abs(ods['equilibrium.time'] - time))
        time = int(np.round(ods['equilibrium.time'][time_index] * 1000))

        if 'equilibrium.code.parameters' in ods:
            code_parameters = ods['equilibrium.code.parameters']
            for items in code_parameters['time_slice'][time_index]:
                self[items.upper()] = namelist.NamelistName()
                for item in code_parameters['time_slice'][time_index][items]:
                    self[items.upper()][item.upper()] = code_parameters['time_slice'][time_index][items][item]

        # figure out what index ranges are for OH coils Vs for PF coils
        names = ods['equilibrium.time_slice[0].constraints.pf_current.:.source']
        koh = [k for k, n in enumerate(names) if (n.startswith("IOH") or n.startswith("OH"))]
        koh = [koh[0], koh[-1] + 1]
        kpf = [k for k, n in enumerate(names) if not (n.startswith("IOH") or n.startswith("OH"))]
        kpf = [kpf[0], kpf[-1] + 1]

        mappings = {
            'oh': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.pf_current.{koh[0]}:{koh[-1]}.measured',
                'kfile': ['ECURRT', 'BITEC', 'FWTEC'],
                'scalar': False,
            },
            'pf_active': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.pf_current.{kpf[0]}:{kpf[-1]}.measured',
                'kfile': ['BRSP', 'BITFC', 'FWTFC'],
                'scalar': False,
            },
            'bpol_probe': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.bpol_probe.:.measured',
                'kfile': ['EXPMP2', 'BITMPI', 'FWTMP2'],
                'scalar': False,
            },
            'flux_loop': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.flux_loop.:.measured',
                'kfile': ['COILS', 'PSIBIT', 'FWTSI'],
                'scalar': False,
            },
            'ip': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.ip.measured',
                'kfile': ['PLASMA', 'BITIP', 'FWTCUR'],
                'scalar': True,
            },
            'diamagnetic_flux': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.diamagnetic_flux.measured',
                'kfile': ['DFLUX', 'SIGDLC', 'FWTDLC'],
                'norm': 1e3,
                'scalar': True,
            },
            'b_field_tor_vacuum_r': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.b_field_tor_vacuum_r.measured',
                'kfile': ['BTOR', '', ''],
                'norm': 1 / ods['tf.r0'],
                'scalar': True,
            },
        }

        if 'IN1' not in self:
            self['IN1'] = namelist.NamelistName()

        for k, (name, case) in enumerate(mappings.items()):
            if case['omas'] in ods:
                print(f"kEQDSK @ {time}ms: {case['kfile'][0]} \u00B1 {case['kfile'][2]} = {case['omas']}")
                # assign the values
                self['IN1'][case['kfile'][0]] = np.array(ods[case['omas']]) * case.get('norm', 1.0)
                # if this quantity handles uncertainties and weights
                if case['kfile'][2]:
                    if case['omas'] + '_error_upper' in ods:
                        self['IN1'][case['kfile'][1]] = ods[case['omas'] + '_error_upper'] * case.get('norm', 1.0)
                    else:
                        printe(f"Warning: Missing data in {case['omas'] + '_error_upper'} ")
                        self['IN1'][case['kfile'][1]] = self['IN1'][case['kfile'][0]] * 0.0
                    # errors in k-file are BIT errors (whatever that means, there is a factor of 10)
                    # NOTE: that's true for all entries but not the diamagnetic flux error
                    if name != 'diamagnetic_flux':
                        self['IN1'][case['kfile'][1]] *= 0.1
                    if case['kfile'][2] not in self['IN1']:
                        self['IN1'][case['kfile'][2]] = np.ones(np.shape(self['IN1'][case['kfile'][0]]))
                    # for array quantities set the weights to zero when there are NaN's
                    if not isinstance(ods[case['omas']], float):
                        self['IN1'][case['kfile'][2]] = self['IN1'][case['kfile'][2]][: len(self['IN1'][case['kfile'][0]])]
                        tmp = np.isnan(self['IN1'][case['kfile'][0]])
                        tmp = tmp | np.isnan(self['IN1'][case['kfile'][1]])
                        tmp = tmp | np.isnan(self['IN1'][case['kfile'][2]])
                        self['IN1'][case['kfile'][0]][tmp] = 0.0
                        self['IN1'][case['kfile'][1]][tmp] = 0.0
                        self['IN1'][case['kfile'][2]][tmp] = 0.0
                # turn scalars into simple floats
                if case['scalar']:
                    for k in range(3):
                        if case['kfile'][k] != '':
                            self['IN1'][case['kfile'][k]] = float(self['IN1'][case['kfile'][k]])
            else:
                printw(f"Could not set {name}: {case['kfile']} in kfile")

        if f'equilibrium.time_slice.{time_index}.constraints.mse_polarisation_angle[0].measured' in ods:
            self['INS'] = namelist.NamelistName()
            self['INS']['KDOMSE'] = 0
            self['INS']['RRRGAM'] = r = ods['mse.channel.:.active_spatial_resolution.0.centre.r']
            self['INS']['ZZZGAM'] = z = ods['mse.channel.:.active_spatial_resolution.0.centre.z']
            AAGAM = ods[f'mse.channel.:.active_spatial_resolution.0.geometric_coefficients']

            self['INS']['AA1GAM'] = AAGAM[:, 1]
            self['INS']['AA2GAM'] = AAGAM[:, 2]
            self['INS']['AA3GAM'] = AAGAM[:, 3]
            self['INS']['AA4GAM'] = AAGAM[:, 4]
            self['INS']['AA5GAM'] = AAGAM[:, 5]
            self['INS']['AA6GAM'] = AAGAM[:, 6]
            # self['INS']['AA7GAM'] = AAGAM[6] #EFIT does not like it if AA7GAM is in the k-file
            self['INS']['IPLOTS'] = 1
            self['INS']['TGAMMA'] = ods[f'equilibrium.time_slice.{time_index}.constraints.mse_polarisation_angle.:.measured']
            self['INS']['SGAMMA'] = ods[f'equilibrium.time_slice.{time_index}.constraints.mse_polarisation_angle.:.measured_error_upper']
            self['INS']['FWTGAM'] = z * 0 + 1
            self['INS']['TGAMMA_corrected_MDS'] = self['INS']['TGAMMA']

            for k in ['TGAMMA', 'SGAMMA']:
                index = np.isnan(self['INS'][k])
                self['INS'][k][index] = 0.0
                self['INS']['FWTGAM'][index] = 0.0

        return self

    def to_omas(self, ods=None, time_index=0, time=None):
        """
        Generate OMAS data structure from kEQDSK.

        Currently this fuction just reads code_parameters.
        In the future, parameters including ITIME,PLASMA,EXPMP2,COILS,BTOR,DENR,DENV,
        SIREF,BRSP,ECURRT,VLOOP,DFLUX,SIGDLC,CURRC79,CURRC139,CURRC199,CURRIU30,CURRIU90,CURRIU150,
        CURRIL30,CURRIL90, CURRIL150 should be written to ods raw parameters.

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added to ods

        :param time: time in seconds where to compare the data (if set it superseeds time_index)

        :return: ODS
        """
        if ods is None:
            ods = ODS()

        if time is not None:
            time_index = np.argmin(np.abs(ods['equilibrium.time'] - time))
        time = int(np.round(ods['equilibrium.time'][time_index] * 1000))

        code_parameters = ods['equilibrium.code.parameters']
        if 'time_slice' not in code_parameters:
            code_parameters['time_slice'] = ODS()
        code_parameters['time_slice'][time_index] = ODS()
        for items in self:
            if '__comment' not in items:
                code_parameters['time_slice'][time_index][items.lower()] = ODS()
                for item in self[items]:
                    code_parameters['time_slice'][time_index][items.lower()][item.lower()] = self[items.upper()][item.upper()]

        return ods

    def compare_omas_constraints(self, ods, time_index=None, time=None, plot_invalid=False):
        """
        Plots comparing constraints in the kEQDSK with respect to what are in an ODS

        :param ods: ods to use for comparison

        :param time_index: force time_index of the ods constraint to compare

        :param time: force time in seconds where to compare the ods data (if set it superseeds time_index)

        :param plot_invalid: toggle plotting of data points that are marked to be in kfile

        :return: figure handler
        """

        from omfit_classes import utils_plot

        if time is None and time_index is None:
            time = self['IN1']['ITIME'] / 1000.0

        if time is not None:
            time_index = np.argmin(np.abs(ods['equilibrium.time'] - time))
        time = int(np.round(ods['equilibrium.time'][time_index] * 1000))

        checks = {
            'pf_active': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.pf_current.:.measured',
                'kfile': ['BRSP', 'BITFC', 'FWTFC'],
                'names': 'pf_active.coil[:].name',
            },
            'bpol_probe': {
                'omas': f'equilibrium.time_slice.{time_index}..constraints.bpol_probe.:.measured',
                'kfile': ['EXPMP2', 'BITMPI', 'FWTMP2'],
                'names': 'magnetics.b_field_pol_probe[:].name',
            },
            'flux_loop': {
                'omas': f'equilibrium.time_slice.{time_index}..constraints.flux_loop.:.measured',
                'kfile': ['COILS', 'PSIBIT', 'FWTSI'],
                'names': 'magnetics.flux_loop[:].name',
            },
            'mse_polarisation_angle': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.mse_polarisation_angle.:.measured',
                'kfile': ['TGAMMA', 'SGAMMA', 'FWTGAM'],
                'names': 'mse.channel[:].name',
            },
            'ip': {'omas': f'equilibrium.time_slice.{time_index}.constraints.ip.measured', 'kfile': ['PLASMA', 'BITIP', 'FWTCUR']},
            'diamagnetic_flux': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.diamagnetic_flux.measured',
                'kfile': ['DFLUX', 'SIGDLC', 'FWTDLC'],
                'norm': 1e3,
            },
            'b_field_tor_vacuum_r': {
                'omas': f'equilibrium.time_slice.{time_index}.constraints.b_field_tor_vacuum_r.measured',
                'kfile': ['BTOR', '', ''],
                'norm': 1 / ods['tf.r0'],
            },
        }

        fig = pyplot.figure(num='kfile - omas comparison')
        fig.clf()

        for k, (name, case) in enumerate(list(checks.items())[:4]):
            try:
                odata = nominal_values(ods[case['omas']])
                oerr = nominal_values(ods[case['omas'] + '_error_upper'])
                n = len(odata)
                for where in ['IN1', 'INS']:
                    if where in self and case['kfile'][0] in self[where]:
                        kdata = copy.deepcopy(self[where][case['kfile'][0]])[:n]
                        kerr = copy.deepcopy(self[where][case['kfile'][1]])[:n]
                        break
                # errors in k-file are BIT errors (whatever that means, there is a factor of 10)
                # NOTE: that's true for all entries but not the diamagnetic flux error
                kerr = kerr * 10.0
                if not plot_invalid:
                    kvalid = copy.deepcopy(self[where][case['kfile'][2]])[:n]
                    kdata[kvalid == 0] = np.nan
                    kerr[kvalid == 0] = np.nan

                # regression
                ax = pyplot.subplot(2, 4, k + 1, aspect='equal')
                ax.set_title(name.replace('_', ' '))
                utils_plot.axdline(color='r', ax=ax)
                ax.errorbar(kdata, odata, yerr=oerr, xerr=kerr, marker='.', ls='')
                ax.set_aspect(1.0 / ax.get_data_ratio(), adjustable='box')
                ax.set_xlabel('kfile')
                ax.set_ylabel('omas')
                if 'names' in case and case['names'] in ods:
                    utils_plot.infoScatter(kdata, odata, ods[case['names']])

                # error histograms
                ax = pyplot.subplot(2, 4, 4 + k + 1)
                ax.hist((odata - kdata) / np.sqrt(kdata ** 2 + odata ** 2 + oerr ** 2 + kerr ** 2) * 100, 31)
                ax.set_aspect(1.0 / ax.get_data_ratio(), adjustable='box')
                ax.set_xlabel('% relative error')
            except Exception as _excp:
                print(f"error in comparison of {name}: " + repr(_excp))

        # plasma current
        print('plasma current:')
        try:
            print(
                f" * omas  = {ods[f'equilibrium.time_slice.{time_index}.constraints.ip.measured']:8.8} \u00b1 {ods[f'equilibrium.time_slice.{time_index}.constraints.ip.measured_error_upper']:8.8} [A]"
            )
            print(f" * kfile = {self['IN1']['PLASMA']:8.8} \u00b1 {self['IN1']['BITIP'] * 10:8.8} [A]")
        except Exception as _excp:
            print("error in comparison: " + repr(_excp))

        # diamagnetic flux
        print('diamagnetic flux:')
        try:
            print(
                f" * omas  = {ods[f'equilibrium.time_slice.{time_index}.constraints.diamagnetic_flux.measured']:8.8} \u00b1 {ods[f'equilibrium.time_slice.{time_index}.constraints.diamagnetic_flux.measured_error_upper']:8.8} [Wb]"
            )
            print(f" * kfile = {self['IN1']['DFLUX'] / 1E3:8.8} \u00b1 {self['IN1']['SIGDLC'] / 1E3:8.8} [Wb]")
        except Exception as _excp:
            print("error in comparison: " + repr(_excp))

        # toroidal vacuum field * R
        print('toroidal vacuum field * R:')
        try:
            print(
                f" * omas  = {ods[f'equilibrium.time_slice.{time_index}.constraints.b_field_tor_vacuum_r.measured']:8.8} \u00b1 {ods[f'equilibrium.time_slice.{time_index}.constraints.b_field_tor_vacuum_r.measured_error_upper']:8.8} [T*m]"
            )
            print(f" * kfile = {self['IN1']['BTOR'] * self['IN1']['RCENTR']:8.8} \u00b1 0.0 [T*m]")
        except Exception as _excp:
            print("error in comparison: " + repr(_excp))

        return fig

    ##################
    # Plot utilities #
    ##################
    def _bad_plot(self, name=None, ax=None, in1=None, **kw):
        """
        Placeholder / indicator for bad plots.
        Used when one of the requested subplots can't be displayed due to missing data.

        :param name: string
            Name of the thing that had a problem leading to the need to indicate a problem with this placeholder plot

        :param ax: Axes instance

        :param in1: [Optional] dict-like
            Defaults to the result of self._combine_namelists()
        """
        in1 = self._combine_namelists() if in1 is None else in1
        ax = pyplot.gca() if ax is None else ax
        if len(ax.lines) == 0:
            # If this is just an empty plot with a warning message, it looks nicer to suppress the tick labels
            ax.tick_params(axis='both', which='both', bottom=False, top=False, right=False, left=False, labelbottom=False, labelleft=False)

        ax.text(
            0.5,
            0.5,
            'Unable to find k-file data for topic: {:}\n shot {:} @ {:} ms'.format(name, in1['ISHOT'], in1['ITIME']),
            transform=ax.transAxes,
            ha='center',
            va='center',
            color='red',
        )
        return

    def _undo_bad_plot(self, ax=None):
        """
        Reverses style changes made by bad_plot.
        Use when overlaying good data onto a plot that has a notification about missing data

        :param ax: Axes instance
        """
        ax = pyplot.gca() if ax is None else ax
        ax.tick_params(axis='both', which='major', bottom=True, top=True, right=True, left=True, labelbottom=True, labelleft=True)

    def _shot_time_label(self, label='', combo=None):
        """
        Provides a generic tag for displaying shot and time in labels in the legends

        :param label: string

        :param combo: [optional] dict-like
                      Defaults to self._combine_namelists()

        :return: string
                 Blank label or label with shot, time, and some description
        """
        if label is None:
            return ''  # disable by setting label=None
        combo = self._combine_namelists() if combo is None else combo
        s = combo['ISHOT']
        t = combo['ITIME']
        if label == '':
            return '{} {} ms'.format(s, t)
        return ' {:}, {:} {:} ms'.format(label, s, t)

    def _keyword_setup(self, in1, ax, label):
        """Avoid duplication of common plot keyword setup junk"""
        in1 = self._combine_namelists() if in1 is None else in1  # Make sure we have the combined namelist
        ax = pyplot.gca() if ax is None else ax
        self._undo_bad_plot(ax=ax)
        stlab = self._shot_time_label(label=label, combo=in1)
        stlab2 = ' [{:}]'.format(stlab) if stlab else ''  # Make secondary shot time label w/ [ ] around it
        return in1, ax, stlab, stlab2

    ###########################
    # Specific plot functions #
    ###########################
    def plot_press_constraint(
        self,
        in1=None,
        fig=None,
        ax=None,
        label='',
        color=None,
        no_extra_info_in_legend=False,
        no_legend=False,
        no_marks_for_uniform_weight=True,
    ):
        """
        Plots pressure constrait in kEQDSK.
        For general information on K-FILES, see
        - https://fusion.gat.com/theory/Efitinputs
        - https://fusion.gat.com/theory/Efitin1
        Specific quantities related to extracting the pressure profile
        ------
        KPRFIT: kinetic fitting mode: 0 off, 1 vs psi, 2 vs R-Z, 3 includes rotation
        NPRESS: number of valid points in PRESSR; positive number: number of input data, negative number:
            read in data from EDAT file, 0: rotational pressure only
        RPRESS: -: input pressure profile as a function of dimensionless fluxes (psi_N), +:
            R coordinates of input pressure profile in m
        ZPRESS: gives Z coordinates to go with R coordinates in RPRESS if RPRESS>0
        PRESSR: pressure in N/m^2 (or Pa) vs. normalized flux (psi_N) for fitting
        PRESSBI: pressure at boundary
        SIGPREBI: standard deviation for pressure at boundary PRESSBI
        KPRESSB: 0: don't put a pressure point at boundary (Default), 1: put a pressure point at the boundary
        Specific quantities related to understanding KNOTS & basis functions
        ------
        KPPFNC basis function for P': 0 = polynomial, 6 = spline
        KPPCUR number of coefficients for poly representation of P', ignored if spline. Default = 3
        KPPKNT number of knots for P' spline, ignored unless KPPFNC=6
        PPKNT P' knot locations in psi_N, vector length KPPKNT, ignored unless KPPFNC=6
        PPTENS spline tension for P'. Large (like 10) ---> approaches piecewise linear. small (like 0.1)
            ---> like a cubic spline
        KPPBDRY constraint switch for P'. Vector of length KPPKNT. Ignored unless KPPFNC=6
        PPBDRY values of P' at each knot location where KPPBDRY=1
        KPP2BDRY on/off for PP2BDRY
        PP2BDRY values of (P')' at each knot location where KPP2BDRY=1

        :param in1: NamelistName instance

        :param fig: Figure instance (unused, but accepted to maintain consistent format)

        :param ax: Axes instance

        :param label: string

        :param color: Matplotlib color specification

        :param no_extra_info_in_legend: bool

        :param no_legend: bool

        :param no_marks_for_uniform_weight: bool

        :return: Matplotlib color specification
        """
        from matplotlib import pyplot

        in1, ax, stlab, stlab2 = self._keyword_setup(in1, ax, label)

        # Get the X,Y values of the constraint profile
        try:
            rpress = in1['RPRESS']  # Position basis for pressure constraint (psi_N, stored as - OR R in m, stored as +)
            press = in1['PRESSR']  # Pressure constraint (Pa)
        except KeyError:
            self._bad_plot('pressure', ax=ax)
            printw('Could not find pressure constraint in K-file IN1: RPRESS and PRESSR missing')
            return color

        # Decide if we're plotting vs. R or vs. psi_N
        if np.mean(rpress) <= 0:  # vs psi
            w = rpress <= 0  # Filter to select only R-type measurements, just in case there's a mix of psi and R.
            x = -rpress[w]
            xlab = r'$\psi_N$'
            boundary = 1
            xrangemin = 0
        else:  # vs R
            w = rpress > 0
            x = rpress[w]
            xlab = '$R$ (m)'
            xrangemin = min(x)
            boundary = None  # Don't know where the boundary is
        press = press[w]

        npress = in1.get('NPRESS', len(press))  # Get the number of constraint points
        error = in1.get('SIGPRE', None)  # Get 1 sigma uncertainty in pressure constraint (Pa)
        weight = in1.get('FWTPRE', np.ones(npress))  # Weighting factor (in addition to sigma) for press, defaults to 1
        label = 'Constraint{:}, {:} = {:}'.format(stlab, r'$\overline{weight}$', np.mean(weight))

        # Check for and get boundary pressure constraint
        # kpressb = in1.get('KPRESSB', 0)  # Boundary pressure constraint on/off
        pressbi = in1.get('PRESSBI', None)  # Boundary pressure constraint value
        sigprebi = in1.get('SIGPREBI', 0)  # Boundary pressure constraint uncertainty

        # Draw the main plot
        if error is None:
            line = ax.plot(x, press, '.-', label=label, color=color)
        else:
            line = ax.errorbar(x, press, error, label=label, color=color)
        color = line[0].get_color() if color is None else color

        ax.set_xlim(xrangemin)

        # Although uncertainty factors into the weight pretty well, there is also another weight.
        # Display the other weight with different sized diamonds, but only if there is something interesting to see
        if weight is not None and ((np.std(weight) > 0) or (no_marks_for_uniform_weight is False)):
            for i in range(np):
                lab = 'Area of diamonds is proportional to fit weight' if i == 0 else ''
                ax.plot(
                    x[i],
                    press[i],
                    linestyle=' ',
                    marker='d',
                    markersize=np.sqrt(weight[i]) * 10,
                    label=lab,
                    markeredgecolor='k',
                    color='none',
                )
                ax.legend(loc=0).draggable()

        # Mark the boundary pressure constraint if there is one
        if pressbi is not None:
            if boundary is None:
                ax.axhline(pressbi, linestyle='--', color='k', label='Boundary pressure constraint' + stlab)
            else:
                ax.errorbar(boundary, pressbi, sigprebi, marker='x', label='Boundary pressure constraint' + stlab, color=color)

        # Mark knot locations
        if in1.get('kppfnc', 0) == 6:
            xknot = in1.get('ppknt', 0)
            vlab = 'Knot locations{:}'.format(stlab)
            ls = next(self.linecycle)
            mark = next(self.markercycle)
            for xk in xknot:
                ax.axvline(xk, linestyle=ls, color=color, label=vlab, marker=mark)
                vlab = ''

        # Finish up with labels and a legend
        ax.set_xlabel(xlab)
        ax.set_ylabel('$p_{kin}$ (Pa)')
        ax.set_title('EFIT k-file kinetic pressure constraint')

        if not no_extra_info_in_legend:
            # Add some extra labels to go on the legend
            extra_info = []
            extra_info += (
                ['Kinetic fitting mode{:}: {:}'.format(stlab, ['off', r'P($\psi_N$)', 'P(R,Z)', 'Include rotation'][in1['KPRFIT']])]
                if 'KPRFIT' in in1
                else []
            )
            for ei in extra_info:
                ax.plot(-1, np.mean(press), color=color, label=ei, linestyle=' ', marker='s')

        if not no_legend:
            ax.legend(loc=0, numpoints=1).draggable()

        return color

    def plot_fast_ion_constraints(
        self, in1=None, fig=None, ax=None, label='', color=None, density=False, no_extra_info_in_legend=False, no_legend=False
    ):
        """
        Documentation on fast ion information in K-FILES:
        https://fusion.gat.com/theory/Efitin1
        https://fusion.gat.com/theory/Efitinputs
        ---
        KPRFIT: kinetic fitting mode: 0 off, 1 vs psi, 2 vs R-Z, 3 includes rotation
        NBEAM: number of points for beam data in kinetic mode (in vector DNBEAM)
        DNBEAM: beam particle density for kinetic EFIT
        PBEAM: beam pressure in Pa vs psi_N for kinetic fitting
        PNBEAM: defaults to 0. That is all we know
        SIBEAM: psi_N values corresponding to PBEAM

        :param in1: NamelistName

        :param fig: Figure instance (unused)

        :param ax: Axes instance

        :param label: string

        :param color: Matplotlib color spec

        :param density: bool

        :param no_extra_info_in_legend: bool

        :param no_legend: bool

        :return: Matplotlib color spec
        """
        in1, ax, stlab, stlab2 = self._keyword_setup(in1, ax, label)

        try:
            x = in1['SIBEAM']  # psi_N for beam pressure and density (fast ion pressure and density)
        except KeyError:
            self._bad_plot('fast ions', ax=ax)
            printw('Could not find SIBEAM: psi_N coordinates for fast ion constraint profiles in k-file')
            return color

        if density:
            # Plot fast ion density
            try:
                y = in1['DNBEAM']  # Beam density in m^-3
            except KeyError:
                self._bad_plot('fast ion density', ax=ax)
                printw('Could not find fast ion density DNBEAM in k-file')
                return color
            ax.set_ylabel('$n_{fast}$ (m$^{-3}$)')
            ax.set_title('EFIT k-file fast ion density constraint')

        else:
            # Plot fast ion pressure
            try:
                y = in1['PBEAM']  # Beam pressure in Pa
            except KeyError:
                self._bad_plot('fast ion pressure', ax=ax)
                printw('Could not find fast ion press PBEAM in k-file')
                return color
            ax.set_ylabel('$p_{fast}$ (Pa)')
            ax.set_title('EFIT k-file fast ion pressure constraint')

        ax.set_xlabel(r'$\psi_N$')
        line = ax.plot(x, y, '.-', label='Constraint{:}'.format(stlab), color=color)
        color = line[0].get_color() if color is None else color
        if not no_legend:
            ax.legend(loc=0).draggable()

        return color

    def plot_current_constraint(self, in1=None, fig=None, ax=None, label='', color=None, no_extra_info_in_legend=False, no_legend=False):
        """
        K-FILES
        see documentation on IN1 namelist in k-file: https://fusion.gat.com/theory/Efitin1
        see https://fusion.gat.com/theory/Efitinputs
        KZEROJ: constrain FF' and P' by applying constraints specified by RZEROJ
            >0: number of constraints to apply
            0: don't apply constraints (default)
        SIZEROJ: vector of locations at which Jt is constrainted when KZEROJ>0.
            When KZEROJ=1, PSIWANT can be used instead of SIZEROJ(1) by setting SIZEROJ(1)<0
            see KZEROJ, RZEROJ, VZEROJ, PSIWANT
            default SIZEROJ(1)=-1.0
        RZEROJ: vector of radii at which to apply constraints.
            For each element in vector & corresponding elements in SIZEROJ, VZEROJ, if
                RZEROJ>0: set Jt=0 @ coordinate RZEROJ,SIZEROJ
                RZEROJ=0: set flux surface average current equal to VZEROJ @ surface specified by normalized flux SIZEROJ
                RZEROJ<0: set Jt=0 @ separatrix
                    applied only if KZEROJ>0. Default RZEROJ(1)=0.0
                If KZEROJ=1, may specify SIZEROJ(1) w/ PSIWANT. If KZEROJ=1 and SIZEROJ(1)<0 then SIZEROJ(1) is set equal to PSIWANT
        PSIWANT: normalized flux value of surface where J constraint is desired.
            See KZEROJ, RZEROJ, VZEROJ.
            Default=1.0
        VZEROJ: Desired value(s) of normalized J (w.r.t. I/area) at
            the flux surface PSIWANT (or surfaces SIZEROJ).
            Must have KZEROJ = 1 or >1 and RZEROJ=0.0.
            Default=0.0
        summary: you should set k to some number of constraint points, then use the SIZEROJ and VZEROJ vectors to set up the psi_N and Jt values at the constraint points
        KNOTS & basis functions
        KFFFNC basis function for FF': 0 polynomial, 6 = spline
        ICPROF specific choice of current profile: 0 = current profile is not specified by this variable,
                                                  1 = no edge current density allowed
                                                  2 = free edge current density
                                                  3 = weak edge current density constraint
        KFFCUR number of coefficients for poly representation of FF', ignored if spline. Default = 1
        KFFKNT number of knots for FF'. Ignored unless KFFFNC=6
        FFKNT knot locations for FF' in psi_N, vector length should be KFFKNT. Ignored unless kfffnc=6
        FFTENS spline tension for FF'. Large (like 10) ---> approaches piecewise linear. small (like 0.1) ---> like a cubic spline
        KFFBDRY constraint switch for FF' (0/1 off/on) for each knot. default to zeros
        FFBDRY value of FF' for each knot, used only when KFFBDRY=1
        KFF2BDRY: on/off (1/0) switch for each knot
        FF2BDRY value of (FF')' for each knot, used only when KFF2BDRY=1

        :param in1: NamelistName

        :param fig: Figure

        :param ax: Axes

        :param label: string

        :param color: Matplotlib color spec

        :param no_extra_info_in_legend: bool

        :param no_legend: bool

        :return: Matplotlib color spec
        """
        in1, ax, stlab, stlab2 = self._keyword_setup(in1, ax, label)

        n = in1.get('KZEROJ', 0)  # Get number of points
        if n == 0:
            printw('Current constraints seem to be turned off')
            self._bad_plot('current', ax=ax)
            return color  # Stop this because the current constraints are turned off

        # Get psi_N (except apparently sometimes this variable means Z in m instead of psi_N)
        if 'SIZEROJ' in in1:
            psin = in1['SIZEROJ']
            if n == 1 and psin[0] < 0:  # Use psiwant instead of sizeroj[0]
                psin[0] = in1['PSIWANT'] if 'PSIWANT' in in1 else 1.0
        else:
            psin = np.array([-1.0])

        r = in1.get('RZEROJ', np.array([0.0]))  # Get major radius in m (not always used)
        current = in1.get('VZEROJ', 0.0)  # Get current @ constraint points given by
        #                                   psi_N (SIZEROJ) or R,Z (RZEROJ,SIZEROJ)
        weight = in1.get('FWTCUR', 1.0)  # Get the weight of the current constraint

        # Decide if the current constraint is vs. psi_N or vs. R,Z
        if r[0] == 0:
            x = psin
            y = current
            xlab = r'$\psi_N$'
            xrangemin = 0
        elif r[0] > 0:
            # This mode sets current to zero at R,Z defined by r,SIZEROJ
            # (SIZEROJ is normally psi_N but this time it's Z I guess?)
            x, z = r, psin
            y = current * 0
            xlab = '$R$ (m)'
            xrangemin = min(r)
        else:  # r[0] < 0:
            # Set Jt @separatrix
            x = 1.0  # Assume it's psi I guess
            y = 0
            xlab = r'$\psi_N$'
            xrangemin = 0

        # Plot the constraint and apply labels
        line = ax.plot(x, y, '.-', label='Constraint{:}, weight = {:}'.format(stlab, weight), color=color)
        color = line[0].get_color() if color is None else color
        ax.set_xlabel(xlab)
        ax.set_ylabel('$J_t$ $/$ $(I_p/Area)$')
        ax.set_title('EFIT k-file normalized toroidal current constraint')
        ax.set_xlim(xrangemin)

        # Mark knot locations
        if in1.get('kppfnc', 0) == 6:
            # Spline
            xknot = in1.get('ffknt', 0)
            vlab = 'Knot locations{:}'.format(stlab)
            ls = next(self.linecycle)
            mark = next(self.markercycle)
            for xk in xknot:
                ax.axvline(xk, linestyle=ls, color=color, label=vlab, marker=mark)
                vlab = ''

        if not no_extra_info_in_legend:
            # Add some extra labels to go on the legend
            extra_info = []
            extra_info += ['$B_T = {:0.2f}$ T'.format(in1['BTOR'])] if 'BTOR' in in1 else []
            extra_info += ['$I_p = {:0.2f}$ MA'.format(in1['PLASMA'] / 1e6)] if 'PLASMA' in in1 else []
            for ei in extra_info:
                ax.plot(-1, np.mean(y), color=color, label='{:}{:}'.format(ei, stlab2), linestyle=' ', marker='s')

        if not no_legend:
            ax.legend(loc=0, numpoints=1).draggable()

        return color

    def plot_mse(self, in1=None, fig=None, ax=None, label='', color=None, no_extra_info_in_legend=False, no_legend=False):
        """
        K-FILES
        plot MSE constraints
        see https://fusion.gat.com/theory/Efitinputs
        RRRGAM R in meters of the MSE observation point
        ZZZGAM Z in meters of the MSE observation point
        TGAMMA "tangent gamma". Tangent of the measured MSE polarization angle, TGAMMA=(A1*Bz+A5*Er)/(A2*Bt+...)
        SGAMMA standard deviation (uncertainty) for TGAMMA
        FWTGAM "fit weight gamma": 1/0 on/off switches for MSE channels
        DTMSEFULL full width of MSE dat time average window in ms
        AA#GAM where # is 1,2,3,...: geometric correction coefficients for MSE data, generated by EFIT during mode 5

        :param in1: NamelistName instance

        :param fig: Figure instance

        :param ax: Axes instance

        :param label: string

        :param color: Matplotlib color spec

        :param no_extra_info_in_legend: bool

        :param no_legend: bool

        :return: Matplotlib color spec
        """
        in1, ax, stlab, stlab2 = self._keyword_setup(in1, ax, label)

        try:
            r = in1['RRRGAM']
            tgamma = in1['TGAMMA']
        except KeyError:
            printw('Could not find MSE data in k-file')
            self._bad_plot('MSE', ax=ax)
            return color
        # z = in1.get('ZZZGAM', r*0)
        sgamma = in1.get('SGAMMA', tgamma * 0)  # Default to no uncertainty (no error bars displayed)
        fwtgam = in1.get('FWTGAM', tgamma * 0)  # Default to all off (fail)
        nw = min([len(sgamma), len(fwtgam)])
        w = fwtgam.astype(bool)[:nw]  # Mask
        if nw < len(sgamma):
            # Make sure w is long enough to cover tgamma and sgamma. If it is not, turn off any extra channels.
            w = np.append(w, np.zeros(len(sgamma) - nw, bool))

        if max(w) == 0:
            printw('all MSE channels are turned off')
            self._bad_plot('MSE [all channels are off]', ax=ax)
            return color

        line = ax.errorbar(r[w], tgamma[w], sgamma[w], label='Constraint{:}'.format(stlab), color=color)
        color = line[0].get_color() if color is None else color
        ax.set_xlabel('R (m)')
        ax.set_ylabel(r'tan($\gamma$)')
        ax.set_title('EFIT k-file MSE constraint')
        if not no_legend:
            ax.legend(loc=0).draggable()

        return color

    def plot_mass_density(self, combo=None, fig=None, ax=None, label='', color=None, no_legend=False):
        """
        K-files plot mass density profile
        see https://fusion.gat.com/theory/Efitin1
        NMASS: number of valid points in DMASS
        DMASS: density mass. Mass density in kg/m^3
        I am *ASSUMING* that this uses RPRESS (psi or R_major for pressure constraint) to get the position coordinates

        :param combo: NamelistName instance

        :param fig: Figure instance

        :param ax: Axes instance

        :param label: string

        :param color: mpl color spec

        :param no_legend: bool

        :return: Matplotlib color spec
        """
        combo, ax, stlab, stlab2 = self._keyword_setup(combo, ax, label)

        # Get the X,Y values of the constraint profile
        try:
            rpress = combo['RPRESS']  # Position basis for pressure constraint
            #                           (psi_N, stored as negative OR R in m, stored as positive)
            dmass = combo['DMASS']  # Density constraint (kg/m^3) #assumed to correspond to rpress
        except KeyError:
            self._bad_plot('mass density', ax=ax)
            printw('Could not find density constraint in K-file IN1: RPRESS or DMASS missing')
            return color

        # Decide if we're plotting vs. R or vs. psi_N
        if np.mean(rpress) <= 0:  # vs psi
            w = rpress <= 0
            x = -rpress[w]
            xlab = r'$\psi_N$'
            xrangemin = 0
        else:  # vs R
            w = rpress > 0
            x = rpress[w]
            xlab = '$R$ (m)'
            xrangemin = min(x)
        dmass = dmass[w]  # Just in case there was a mixture, we'll pick the dominant group
        #                              (I don't know if mixtures are even allowed)

        line = ax.plot(x, dmass, '.-', label='Constraint{:}'.format(stlab))  # Not sure how this works as a constraint
        color = line[0].get_color() if color is None else color
        ax.set_xlim(xrangemin)
        ax.set_xlabel(xlab)
        ax.set_ylabel(r'$\rho$ (kg/m$^3$)')
        ax.set_title('EFIT k-file mass density profile')
        if not no_legend:
            ax.legend(loc=0).draggable()

        return color

    def plot_pressure_and_current_constraints(
        self,
        in1=None,
        fig=None,
        ax=None,
        label='',
        color=None,
        no_extra_info_in_legend=False,
        no_legend=False,
        no_marks_for_uniform_weight=True,
    ):
        """Plot pressure and current constraints together"""
        in1 = self._combine_namelists() if in1 is None else in1

        n_rows = 3
        n_cols = 1
        n_plots = n_rows * n_cols
        base = n_rows * 100 + n_cols * 10
        # Make sure we have enough subplots in the figure
        fig = pyplot.gcf() if fig is None else fig
        ax = fig.get_axes() if ax is None else ax
        if len(np.atleast_1d(ax).flatten()) >= n_plots:
            axx = np.array(ax).flatten()
            ax1 = axx[0]
            ax2 = axx[1]
            ax3 = axx[2]
            new_plot_opened = False
        else:
            if len(np.array(ax).flatten()) >= 1:
                # We got here because len(ax)<n_plots, which means our output doesn't fit.
                # But if len(ax)=0, then we can reuse the figure we have because it's blank.
                fig = pyplot.figure()
                new_plot_opened = True  # Let the main plot script know that we need a cornernote for the new plot
            else:
                # A new plot could've been opened by pyplot.gcf(), but we already have that possibility covered below
                # in the main plot function.
                new_plot_opened = False
            ax1 = fig.add_subplot(base + 1)
            ax2 = fig.add_subplot(base + 2, sharex=ax1)
            ax3 = fig.add_subplot(base + 3, sharex=ax1)

        # Color will be updated by the first plot if it is None, and then all plots will have the same color even if
        # some subfigs are missing data for some of the k-files. If the first plot fails, the second plot can update
        # color.

        # Plot 1: pressure
        color = self.plot_press_constraint(
            in1,
            fig=fig,
            ax=ax1,
            label=label,
            color=color,
            no_extra_info_in_legend=no_extra_info_in_legend,
            no_legend=no_legend,
            no_marks_for_uniform_weight=no_marks_for_uniform_weight,
        )

        # Plot 2: current
        color = self.plot_current_constraint(
            in1, fig=fig, ax=ax2, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
        )

        # Plot 3: fast ion pressure
        self.plot_fast_ion_constraints(
            in1,
            fig=fig,
            ax=ax3,
            label=label,
            color=color,
            density=False,
            no_extra_info_in_legend=no_extra_info_in_legend,
            no_legend=no_legend,
        )

        # Make sure it's pretty
        if os.environ.get('OMFIT_NO_GUI', '0') == '0':
            import matplotlib.pyplot

            pyplot.tight_layout()

        return new_plot_opened

    def plot_everything(
        self,
        combo=None,
        fig=None,
        ax=None,
        label='',
        color=None,
        no_extra_info_in_legend=False,
        no_legend=False,
        no_marks_for_uniform_weight=True,
    ):

        """Plot pressure, mass density, current, fast ion pressure, fast ion density, MSE"""

        combo = self._combine_namelists() if combo is None else combo

        n_rows = 3
        n_cols = 2
        n_plots = n_rows * n_cols
        base = n_rows * 100 + n_cols * 10
        # Make sure we have enough subplots in the figure
        fig = pyplot.gcf() if fig is None else fig
        ax = fig.get_axes() if ax is None else ax
        if len(np.array(ax).flatten()) >= n_plots:
            axx = np.array(ax).flatten()
            ax1 = axx[0]
            ax2 = axx[1]
            ax3 = axx[2]
            ax4 = axx[3]
            ax5 = axx[4]
            ax6 = axx[5]
            new_plot_opened = False
        else:
            if len(np.array(ax).flatten()) >= 1:
                # We got here because len(ax)<n_plots, which means our output doesn't fit. But if len(ax)=0, then we
                # can reuse the figure we have because it's blank.
                fig = pyplot.figure()
                new_plot_opened = True  # Let the main plot script know that we need a cornernote for the new plot
            else:
                # a new plot could've been opened by pyplot.gcf(), but we already have that possibility covered below
                # in the main plot function
                new_plot_opened = False
            ax1 = fig.add_subplot(base + 1 + 0 * n_cols)
            ax2 = fig.add_subplot(base + 1 + 1 * n_cols, sharex=ax1)
            ax3 = fig.add_subplot(base + 1 + 2 * n_cols, sharex=ax1)
            ax4 = fig.add_subplot(base + 2 + 0 * n_cols, sharex=ax1, sharey=ax1)  # 4 and 1 are both pressure
            ax5 = fig.add_subplot(base + 2 + 1 * n_cols, sharex=ax1)  # The first 5 will typically be vs. psi
            ax6 = fig.add_subplot(base + 2 + 2 * n_cols)  # This one is always going to be vs. R

        # Plot 1: pressure
        color = self.plot_press_constraint(
            combo,  # Color will be updated by the first plot if it is None
            fig=fig,
            ax=ax1,
            label=label,
            color=color,
            no_extra_info_in_legend=no_extra_info_in_legend,
            no_legend=no_legend,
            no_marks_for_uniform_weight=no_marks_for_uniform_weight,
        )
        # Plot 2: mass density
        color = self.plot_mass_density(
            combo,  # The first plot could fail and leave color as None. We'd better try to update color at every turn
            fig=fig,
            ax=ax2,
            label=label,
            color=color,
        )
        # Plot 3: current
        color = self.plot_current_constraint(
            combo, fig=fig, ax=ax3, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
        )
        # Plot 4: fast ion pressure
        color = self.plot_fast_ion_constraints(
            combo,
            fig=fig,
            ax=ax4,
            label=label,
            color=color,
            density=False,
            no_extra_info_in_legend=no_extra_info_in_legend,
            no_legend=no_legend,
        )
        # Plot 5: fast ion density
        color = self.plot_fast_ion_constraints(
            combo,
            fig=fig,
            ax=ax5,
            label=label,
            color=color,
            density=True,
            no_extra_info_in_legend=no_extra_info_in_legend,
            no_legend=no_legend,
        )
        # Plot 6: MSE
        self.plot_mse(
            combo, fig=fig, ax=ax6, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
        )
        # Make sure it's pretty
        if os.environ.get('OMFIT_NO_GUI', '0') == '0':
            pyplot.tight_layout()

        return new_plot_opened

    #######################
    # K-FILE PLOT MANAGER #
    #######################
    def plot(self, plottype=None, fig=None, ax=None, label='', color=None, no_extra_info_in_legend=False, no_legend=False):

        """
        Plot manager for k-file class OMFITkeqdsk
        Function used to decide what real plot function to call and to apply generic plot labels.
        You can also access the individual plots directly, but you won't get the final annotations.
        EFIT k-file inputs are documented at https://fusion.gat.com/theory/Efitinputs
        :param plottype: string
            What kind of plot?
                - 'everything'
                - 'pressure and current'
                - 'pressure'
                - 'current'
                - 'fast ion density'
                - 'fast ion pressure'
                - 'mse'
                - 'mass density'

        :param fig: [Optional] Figure instance
            Define fig and ax to override automatic determination of plot output destination.

        :param ax: [Optional] Axes instance or array of Axes instances
            Define fig and ax to override automatic determination of plot output destination.
            Ignored if there are not enough subplots to contain the plots ordered by plottype.

        :param label: [Optional] string
            Provide a custom label to include in legends. May be useful when overlaying two k-files.
            Default: ''. Set label=None to disable shot and time in legend entries.

        :param no_extra_info_in_legend: bool
            Do not add extra text labels to the legend to display things like Bt, etc.

        :param no_legend: bool
            Do not add legends to the plots
        """

        combo = self._combine_namelists()

        fignums = (
            pyplot.get_fignums()
        )  # Get a list of figure numbers that are open at the start so we can detect the case where there were no figures open

        new_plot_opened = False  # This is for a specific case where a plot that needs several subplots doesn't have enough so it has to make a new window. Assume False unless set True later

        # Pick which plot we're making
        if plottype is None:
            plottype = 'everything'  # Change None to default option
        # Now find and call the appropriate function
        if plottype.lower() in ['everything', 'all', 'all plots', 'every plot']:
            # Combo plot of everything
            new_plot_opened = self.plot_everything(
                combo, fig=fig, ax=ax, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
            )
        elif plottype.lower() in ['pressure and current', 'pressure_and_current', 'presscurr', 'pc']:
            # Combo plot of kinetic pressure, fast ion pressure, and current
            new_plot_opened = self.plot_pressure_and_current_constraints(
                combo, fig=fig, ax=ax, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
            )
        elif plottype.lower() in ['pressure_constraint', 'pressure constraint', 'press', 'pressure']:
            # Total kinetic pressure
            self.plot_press_constraint(
                combo, fig=fig, ax=ax, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
            )
        elif plottype.lower() in ['current_constraint', 'current constraint', 'current', 'curr', 'curr constraint']:
            # Toroidal current
            self.plot_current_constraint(
                combo, fig=fig, ax=ax, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
            )
        elif plottype.lower() in [
            'fast_ion_density',
            'fast ion density',
            'n_fast',
            'fast density',
            'fast dens',
            'beam density',
            'beam ion density',
            'n_beam',
        ]:
            # Fast ion density
            self.plot_fast_ion_constraints(
                combo,
                fig=fig,
                ax=ax,
                label=label,
                color=color,
                density=True,
                no_extra_info_in_legend=no_extra_info_in_legend,
                no_legend=no_legend,
            )
        elif plottype.lower() in [
            'fast_ion_pressure',
            'fast ion pressure',
            'p_fast',
            'fast pressure',
            'fast press',
            'p_beam',
            'beam pressure',
            'beam ion pressure',
        ]:
            # Fast ion pressure
            self.plot_fast_ion_constraints(
                combo,
                fig=fig,
                ax=ax,
                label=label,
                color=color,
                density=False,
                no_extra_info_in_legend=no_extra_info_in_legend,
                no_legend=no_legend,
            )
        elif plottype.lower() in ['mse']:
            # MSE tan(gamma)
            self.plot_mse(
                combo, fig=fig, ax=ax, label=label, color=color, no_extra_info_in_legend=no_extra_info_in_legend, no_legend=no_legend
            )
        elif plottype.lower() in ['mass_density', 'dmass', 'density', 'dens', 'mass density']:
            # Mass density
            self.plot_mass_density(combo, fig=fig, ax=ax, label=label, color=color)
        elif plottype.lower() in ['bad_plot']:
            # Test the bad plot warning
            self._bad_plot('(TEST MISSING DATA NOTIFICATION)', ax=ax, label=label)
        else:
            printe('Unrecognized keqdsk plot type: {:}'.format(plottype))
            return

        # Final annotations
        try:
            from omfit_classes.utils_plot import cornernote
        except ImportError:
            pass
        else:
            do_cornernote = False  # By default, no cornernote
            if fignums == []:
                # If there were no plots open when we started, then we must've made a plot, so we can put a cornernote on it
                do_cornernote = True
            if new_plot_opened:
                do_cornernote = True
            if do_cornernote:
                cornernote('', '{} {} ms'.format(combo['ISHOT'], combo['ITIME']))
            else:
                cornernote(remove=True)


############################
# S-FILE CLASS OMFITseqdsk #
############################
class OMFITseqdsk(SortedDict, OMFITascii):
    r"""
    class used to interface S files generated by EFIT

    :param filename: filename passed to OMFITascii class

    :param \**kw: keyword dictionary passed to OMFITascii class
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self, caseInsensitive=False, sorted=False)
        self.dynaLoad = True

    @dynaLoad
    def load(self, **kw):
        if self.filename is None or not os.stat(self.filename).st_size:
            return

        with open(self.filename, 'r') as f:
            lines = f.read().split('\n')

        for k in ['x', 'y', 'dx', 'dy']:
            self[k] = []
        for k, line in enumerate(lines):
            try:
                x, y, dx, dy = list(map(float, line.split()))
                self['x'].append(x)
                self['y'].append(y)
                self['dx'].append(dx)
                self['dy'].append(dy)
            except Exception:
                if k < 3:
                    if k == 0:
                        self['xlabel'] = line.strip()
                    elif k == 1:
                        self['ylabel'] = line.strip()
                    elif k == 2:
                        self['title'] = line.strip()
        for k in ['x', 'y', 'dx', 'dy']:
            self[k] = np.array(self[k])

    @dynaSave
    def save(self):
        tmp = np.array([self['x'], self['y'], self['dx'], self['dy']]).T
        with open(self.filename, 'w') as f:
            if 'xlabel' in self:
                f.write(self['xlabel'] + '\n')
            if 'ylabel' in self:
                f.write(self['ylabel'] + '\n')
            if 'title' in self:
                f.write(self['title'] + '\n')
            savetxt(f, tmp, fmt='%10.5f')

    def plot(self, **kw):
        if 'ylabel' in self:
            kw.setdefault('label', self['ylabel'])
        else:
            kw.setdefault('label', os.path.split(self.filename)[1])
        errorbar(self['x'], self['y'], self['dy'], self['dx'], **kw)
        if 'xlabel' in self:
            pyplot.xlabel(self['xlabel'])
        if 'title' in self:
            pyplot.title(self['title'])
        if 'ylabel' in self:
            pyplot.legend(labelspacing=0.1, loc=0).draggable(state=True)


############################################
# Read basic equilibrium data from MDSplus #
############################################
def _prep_derived_for_read_basic_eq_from_mds(device, quiet=False, **kw):
    """
    Examines quantities requested and makes extensions as needed to support requested derived quantities

    :param device: str
        Name of the tokamak

    :param quiet: bool
        Be quiet; don't print stuff

    :param g_file_quantities: list of strings
        Quantities to read from the sub-tree corresponding with the EFIT g-file.
        Example: ['r', 'z', 'rhovn']

    :param a_file_quantities: list of strings
        Quantities to read from the sub-tree corresponding with the EFIT a-file.
        Example: ['area']

    :param measurements: list of strings
        Quantities to read from the MEASUREMENTS tree.
        Example: ['fccurt']

    :param derived_quantities: list of strings
        Derived quantities to be calculated and returned.
        This script understands a limited set of simple calculations: 'time', 'psin', 'psin1d'
        Example: ['psin', 'psin1d', 'time']

    :param other_results: list of strings
        Other quantities to be gathered from the parent tree that holds gEQDSK and aEQDSK.
        Example: ['DATE_RUN']

    :param get_all_meas: bool
        Fetch measurement signals according to its time basis which includes extra time slices that failed to fit.
        The time 'axis' will be avaliabe in ['mtimes']

    :return: tuple containing:
        g_params: list of strings
        a_params: list of strings
        d_params: list of strings
        o_params: list of strings
        measurements: list of strings
    """

    def printdq(*arg, **kw):
        if not quiet:
            printd(*arg, **kw)

    g_params = tolist(kw.pop('g_file_quantities', ['r', 'z', 'rhovn']))
    a_params = tolist(kw.pop('a_file_quantities', ['area']))
    d_params = tolist(kw.pop('derived_quantities', ['psin', 'psin1d', 'time']))
    o_params = tolist(kw.pop('other_results', ['DATE_RUN']))
    measurements = tolist(kw.pop('measurements', ['fccurt']))
    get_all_meas = kw.get('get_all_meas', False)
    if get_all_meas and ('mtime' not in measurements):
        measurements.append('mtime')
        # make sure the m file time basis get fetched

    # Sanitize measurements if we are not looking at DIII-D (they need further implementation tests).
    if not is_device(device, 'DIII-D'):
        if not quiet:
            printw(
                'WARNING: read_basic_eq_from_mds: data from the "measurements" branch are not available for the '
                'selected device: {}. The following pointnames in measurements will not be gathered: {}'.format(device, measurements)
            )
        measurements = []
        get_mfile = False
    else:
        printdq(f'  No need to suppress measurements for device {device}')

    # Add dependencies for derived quantities
    more_g = []
    more_a = []
    more_d = []
    if 'psin' in d_params:
        more_g += ['psirz', 'ssimag', 'ssibry']
    if 'psin1d' in d_params:
        more_g += ['mw']
    if any([a in d_params for a in ['br', 'bz', 'Br', 'Bz']]):
        more_g += ['r', 'z', 'psirz', 'cpasma']
    if measurements or 'nebar_r0' in a_params or 'nebar_v1' in a_params or 'nebar_v2' in a_params or 'nebar_v3' in a_params:
        more_a = ['atime']

    for gg in more_g:
        if gg not in g_params:
            g_params += [gg]
    for aa in more_a:
        if aa not in a_params:
            a_params += [aa]
    for dd in more_d:
        if dd not in d_params:
            d_params += [dd]

    # Make sure atime comes first if it is being gathered.
    a_params = list(set(a_params))  # Eliminating duplicates might change the order of keys, so do it first
    if 'atime' in a_params:
        a_params.remove('atime')
        a_params = ['atime'] + a_params

    return list(set(g_params)), a_params, list(set(d_params)), list(set(o_params)), list(set(measurements))


def read_basic_eq_from_mds(device='DIII-D', shot=None, tree='EFIT01', quiet=False, toksearch_mds=None, **kw):
    """
    Read basic equilibrium data from MDSplus
    This is a lightweight function for reading simple data from all EFIT slices at once without making g-files.

    :param device: str
        The tokamak that the data correspond to ('DIII-D', 'NSTX', etc.)

    :param server: str [Optional, special purpose]
        MDSplus server to draw data from. Use this if you are connecting to a
        server that is not recognized by the tokamak() command, like vidar,
        EAST_US, etc. If this is None, it will be copied from device.

    :param shot: int
        Shot number from which to read data

    :param tree: str
        Name of the MDSplus tree to connect to, like 'EFIT01', 'EFIT02', 'EFIT03', ...

    :param g_file_quantities: list of strings
        Quantities to read from the sub-tree corresponding with the EFIT g-file.
        Example: ['r', 'z', 'rhovn']

    :param a_file_quantities: list of strings
        Quantities to read from the sub-tree corresponding with the EFIT a-file.
        Example: ['area']

    :param measurements: list of strings
        Quantities to read from the MEASUREMENTS tree.
        Example: ['fccurt']

    :param derived_quantities: list of strings
        Derived quantities to be calculated and returned.
        This script understands a limited set of simple calculations: 'time', 'psin', 'psin1d'
        Example: ['psin', 'psin1d', 'time']

    :param other_results: list of strings
        Other quantities to be gathered from the parent tree that holds gEQDSK and aEQDSK.
        Example: ['DATE_RUN']

    :param quiet: bool

    :param get_all_meas: bool
        Fetch measurement signals according to its time basis which includes extra time slices that failed to fit.
        The time 'axis' will be avaliabe in ['mtimes']

    :param toksearch_mds: OMFITtoksearch instance
        An already fetched and loaded OMFITtoksearch object, expected to have
        fetched all of the signals for the mdsValues in this file.

    :param allow_shot_tree_translation: bool
        Allow the real shot and tree to be translated to the fake shot stored in the EFIT tree

    :return: dict
    """
    if toksearch_mds is None:
        from MDSplus import MdsException
        from omfit_classes.omfit_mds import OMFITmdsValue, OMFITmds
    else:
        OMFITmdsValue = toksearch_mds

    def printdq(*arg, **kw):
        if not quiet:
            printd(*arg, **kw)

    # Setup -------------------------------------------------------------------------------------------------------

    # Sanitize inputs and assign defaults as needed
    device = utils_fusion.tokamak(device)
    server = kw.pop('server', device)
    if server is None:
        server = device

    g_params, a_params, d_params, o_params, measurements = _prep_derived_for_read_basic_eq_from_mds(device=device, quiet=quiet, **kw)
    get_all_meas = kw.pop('get_all_meas', False)

    # Handle shot/tree translation, if needed
    if kw.pop('allow_shot_tree_translation', True) and tree.startswith(str(shot)):
        # Scratch EFITs get stored in a tree named `EFIT` with fake shot numbers that are the real shot# plus a
        # counter. However, tools for looking up EFIT trees for a given shot will return these in the list. To
        # access them, the shot and tree need to be translated.
        try:
            nom = OMFITmdsValue(server, shot=shot, treename=tree, TDI=rf'GETNCI(\top, "number_of_members")').data()
            if not nom[0]:
                raise ValueError(f'Tree {tree} has no members for {server}#{shot}')
        except Exception:  # I want (MdsException, TypeError, ValueError), but can't import MDS exceptions reliably
            real_shot = shot
            shot = tree
            tree = 'EFIT'
            printw(f'Shot {real_shot}, tree {shot} did not exist; translated to shot {shot}, tree {tree}')
        else:
            printw(f'This treename seems like it should be fake, yet it has data. Skipping translation.')

    if shot is None:
        raise ValueError('Shot number must be not be None!')

    # Make sure the tree exists
    try:
        if toksearch_mds is None:
            OMFITmds(server=server, treename=tree, shot=shot, quiet=quiet).load()
    except MdsException:
        printe('FAIL! Tree {:} does not exist for shot {:} on MDSplus server {:}'.format(tree, shot, server))
        return None

    # Some BAD PEOPLE saved nebar_* with different dimensions than everything else.
    # They interpolated path*, which GOES WITH nebar_*, but did not interpolate nebar_* itself.
    special_timebase = ['nebar_r0', 'nebar_v1', 'nebar_v2', 'nebar_v3']

    # Look up how data are organized for the device in question ---------------------------------------------------
    # Format code
    device_formats = {
        'DIII-D': 'A',
        'NSTX': 'B',
        'NSTXU': 'B',
        'CMOD': 'C',  # Format C also triggers transposition of 2D data.
        'EAST': 'B',
        'EAST_US': 'B',
        'KSTAR': 'A',
        'ST40': 'B',
    }
    default_format = 'A'  # For unrecognized devices
    device_format = device_formats.get(device, default_format)

    if is_device(device, 'CMOD') and tree == 'ANALYSIS':
        field = 'TOP.EFIT.RESULTS'
    else:
        field = 'TOP.RESULTS'

    # Format of TDI calls to MDSplus to a-file or g-file
    tree_formats = {
        'A': '\\{efit_tree:}::TOP.RESULTS.{letter:}EQDSK.{signal:}',
        'B': '\\{efit_tree:}::TOP.RESULTS.{letter:}EQDSK.{signal:}',
        'C': '\\{efit_tree:}::%s.{letter:}_EQDSK.{signal:}' % field,
    }
    # Format of TDI calls to MDSplus to top level results tree
    tree_formats_other_results = {
        'A': '\\{efit_tree:}::TOP.RESULTS.{signal:}',
        'B': '\\{efit_tree:}::TOP.RESULTS.{signal:}',
        'C': '\\{efit_tree:}::%s.{signal:}' % field,
    }
    # Each transpose plan is a list of data array dimensions to transpose
    transpose_plans = {'A': [], 'B': [], 'C': [2]}  # Don't transpose anything  # Don't transpose anything  # Transpose 2D data only
    time_axis_3d_info = {'A': 2, 'B': 0, 'C': 2}

    # Unit conversions for time are handled automatically - see below

    # Select device specific format
    form = tree_formats[device_format]
    form2 = tree_formats_other_results[device_format]
    form3 = form2.replace('RESULTS', 'MEASUREMENTS')
    transpose_plan = transpose_plans[device_format]
    time_axis_3d = time_axis_3d_info[device_format]

    # Get results ------------------------------------------------------------------------------------------------------
    results = {}

    # Always get time

    # Time is a derived quantity because it is pulled from dim_of() on psirz and the unit conversion
    # is handled automatically. I prefer to get time from psirz because psirz is so fundamental and
    # must be present in order to do anything useful, whereas some joker could've renamed time to
    # gtime or efittime or times or who knows what else.
    letter = 'G'
    signal = 'PSIRZ'
    # Step 1: look up the units of time and pick a conversion factor

    psirz_call = form.format(efit_tree=tree, letter=letter, signal=signal)
    units_obj = OMFITmdsValue(
        server=server, treename=tree, shot=shot, TDI=form.format(efit_tree=tree, letter=letter, signal=signal), quiet=quiet
    )
    units = units_obj.units_dim_of(time_axis_3d)
    printdq('units({}) = {}'.format(time_axis_3d, units))
    time_call = 'dim_of({:}, {:})'.format(form.format(efit_tree=tree, letter=letter, signal=signal), time_axis_3d)

    ucf = {'s': 1000.0, 'sec': 1000.0, 'ms': 1.0, '': -1, ' ': -1}

    psirz_sig = OMFITmdsValue(server=server, treename=tree, shot=shot, TDI=psirz_call, quiet=quiet)
    units = psirz_sig.units_dim_of(time_axis_3d)

    unit_conversion = ucf.get(units, None)
    if unit_conversion == -1:  # Blank units; we can try to look them up another way. Activate contingency plans!
        printdq('  Blank time units.')
        printdq('  Attempting contingency plan 1 to get EFIT time units...')
        # Attempt to work this out by reading the time call separately and taking .units() of it
        time_raw1 = psirz_sig.dim_of(time_axis_3d)
        try:
            units = time_raw1.units()
            unit_conversion = ucf.get(units, None)
        except Exception:
            unit_conversion = None
        if unit_conversion is None:
            printdq('  Unrecognized time units from contingency plan 1 ({}). FAIL.'.format(repr(units)))
            contingency_failed = True
        elif unit_conversion == -1:
            # Attempt to work this out by reading gtime
            printdq('  Blank time units from contingency plan 1.')
            printdq('  Attempting contingency plan 2 to get EFIT time units: read units of gtime...')
            call = form.format(efit_tree=tree, letter=letter, signal='gtime')
            gtime = OMFITmdsValue(server=server, treename=tree, shot=shot, TDI=call, quiet=quiet)
            if gtime is not None and gtime.data() is not None:
                if np.all(np.atleast_1d(time_raw1 == gtime)):
                    printdq('  gtime matches time_raw1; can use its units')
                    units = gtime.units()
                    unit_conversion = ucf.get(units, None)
                    if unit_conversion is None or unit_conversion == -1:
                        contingency_failed = True
                        printdq('  gtime had unrecognized or missing units: {}. FAIL'.format(units))
                    else:
                        # It worked; continue
                        printdq(
                            '  Contingency plan 2 for getting time units was successful. '
                            'units = {}, unit_conversion = {}'.format(units, unit_conversion)
                        )
                        contingency_failed = False
                else:
                    contingency_failed = True
                    printdq('  gtime does not match time_raw1; cannot borrow its units. Fail.')
            else:
                printdq('  Failed to read gtime. Cannot get time units that way. Out of options. Fail.')
                contingency_failed = True
        else:
            # It worked; continue
            printdq(
                '  Contingency plan 1 for getting time units was successful. units = {}, unit_conversion = {}'.format(
                    units, unit_conversion
                )
            )
            contingency_failed = False
    elif unit_conversion is None:
        # Unrecognized units
        printdq('  Unrecognized time units: {}'.format(units))
        contingency_failed = True
    else:
        printdq('  Recognized time units from first attempt. No contingency plans needed or attempted.')
        contingency_failed = False  # Contingency is not even needed
    if contingency_failed:
        if not quiet:
            printw(
                'WARNING: read_basic_eq_from_mds: Did not recognize units of time ({})! '
                'Unable to guarantee conversion to ms! '
                'Unit conversion factor has been set to 1.0 for lack of better options.'.format(repr(units))
            )
        unit_conversion = 1.0

    # Step 2 read the time and convert to ms
    printdq('  read_basic_eq_from_mds: gathering time; call = {}'.format(time_call))
    time_raw = psirz_sig.dim_of(time_axis_3d)
    printdq(
        '  read_basic_eq_from_mds: time_raw.min() = {}, time_raw.max() = {}, len(time_raw) = {}, '
        'unit_conversion = {}'.format(time_raw.min(), time_raw.max(), len(time_raw), unit_conversion)
    )

    # Now loop through A-files and G-files and get quantities
    for letter, signal in zip('G' * len(g_params) + 'A' * len(a_params), g_params + a_params):
        call = form.format(efit_tree=tree, letter=letter, signal=signal)

        if signal.lower() in special_timebase:
            printdq('  read_basic_eq_from_mds: Interpolating quantity with special_timebase: {}'.format(signal))
            tmp_res = OMFITmdsValue(server=server, treename=tree, shot=shot, TDI=call, quiet=quiet)
            try:
                tmp_res_data = tmp_res.data()
            except Exception as e:
                res = None
                tmp_units = None
                printw(
                    f"WARNING: MDSplus returned the following exception when attempting to access {call} for shot {shot} on {tree} at {server}"
                )
                printw(e)
                printw("The variable was replaced with None")
            else:
                if len(tmp_res_data) > 1:
                    res = interpolate.interp1d(tmp_res.dim_of(0), tmp_res_data, bounds_error=False, fill_value=0)(results['atime'])
                else:
                    res = tmp_res_data
        else:
            try:
                tmp_res = OMFITmdsValue(server=server, treename=tree, shot=shot, TDI=call, quiet=quiet)
                res = tmp_res.data()
                tmp_units = tmp_res.units()
            except Exception as e:  # any of the MDSplus errors, they are hard to classify
                res = None
                tmp_units = None
                printw(
                    f"WARNING: MDSplus returned the following exception when attempting to access {call} for shot {shot} on {tree} at {server}"
                )
                printw(e)
                printw("The variable was replaced with None")
        if len(np.shape(res)) in transpose_plan:
            res = res.T
        if isinstance(tmp_units, str) and is_numeric(res):
            # Units will be handled by converting all of the MDS results to m, s, MJ.
            # From there, any different units in the EFIT file specifications can be obtained.
            # Without doing this step first, there's not a robust way to know what units were
            # used when saving to MDSplus, because they are definitely not the same as the EFIT
            # files at DIII-D.
            u = tmp_units.strip()
            if u == 'cm':
                factor = 1e-2  # Convert cm to m. Quantities which are supposed to be in cm will be converted back.
            elif u == 'cm^2':
                factor = 1e-4  # Convert cm^2 to m^2
            elif u == 'cm^3':
                factor = 1e-6
            elif u in ['W', 'J']:
                factor = 1e-6  # Convert W to MW, J to MJ
            elif u == 'ms' and signal not in ['atime', 'time', 'gtime']:  # Slice times are handled differently.
                factor = 1e-3  # Convert ms to s
            elif (signal.lower() in ['atime', 'gtime']) and u.lower() in ['s', 'sec', 'seconds']:
                factor = 1e3  # time is in ms, so for consistency, atime and gtime should be, too.
            else:
                factor = 1
            res *= factor
            printdq(' read_basic_eq_from_mds() Converted units of {}EQDSK quantity {} with factor {}.'.format(letter, signal, factor))
        results[signal] = res

    # Get measurements (mostly M file quantities are here)

    # Get meas_time
    # Elements in the measurements subtree have the same time basis, but can be different from results tree
    call = form3.format(efit_tree=tree, signal='cpasma')
    cpasma = OMFITmdsValue(server=server, treename=tree, shot=shot, TDI=call, quiet=quiet)
    meas_time = cpasma.dim_of(0)

    # Get meas signals
    for signal in measurements:
        printdq('  Now processing signal {} in measurements...'.format(signal))

        if signal in ['mtime', 'm_time']:
            if get_all_meas:
                results[signal] = meas_time
            else:
                results[signal] = results['atime']  # It will be reduced to g/a files time basis
            continue
        elif signal == 'cpasma':
            res0 = cpasma  # avoid refetching to save time
        else:
            call = form3.format(efit_tree=tree, signal=signal)
            res0 = OMFITmdsValue(server=server, treename=tree, shot=shot, TDI=call, quiet=quiet)

        # Measurements can have more time-slices than results, because results can fail. We have to deal with that
        ndim = len(np.shape(res0.data()))
        if ndim == 1:
            time_axis = 0
        else:  # ndim == 2:  # There are no 3D measurements.
            time_axis = 1
        sig_time = res0.dim_of(time_axis)
        if sig_time is None:  # This var don't exist on this tree
            results[signal] = None  # Always return something for requested signals. Makes downstream
            printd(f"{signal} is missing from MDS+, skipped")
            continue
        if len(meas_time) == 1:
            # For single-time EFITs (can happen for kinetic EFITs), measurements are saved in 1xN arrays
            # and don't need to be interpolated because they are only saved for the time in question.
            res = res0.data()[0]  # : is assumed for any subsequent dimensions.  https://docs.scipy.org
        elif get_all_meas:  # Fetch measurement signals on its own time basis
            res = res0.data()
        else:
            # Interpolate. In reality, measurement contains extra times where EFIT failed to fit. (Particularly in
            # EFIT01/02). These extra times needs to be removed to fit time basis of the g/a files. Interp1e is just
            # a fast way of doing that.
            res = interp1e(sig_time, res0.data(), axis=0)(results['atime'])
            # sig_time is either None or meas_time according to how uploads at DIII-D processed, but use sig_time for
            # robustness

        if signal not in results:
            # This test prevents overwriting a signal that was found in gEQDSK or aEQDSK with a missing signal.
            if len(np.shape(res)) in transpose_plan:
                res = res.T
            results[signal] = res
        else:
            # Still attach it, but with a name suffix
            results[signal + '_meas'] = res

    for signal in o_params:
        call = form2.format(efit_tree=tree, signal=signal)
        res = OMFITmdsValue(server=server, treename=tree, shot=shot, TDI=call, quiet=quiet).data()
        if res is not None or signal not in results:
            # This test prevents overwriting a signal that was found in gEQDSK or aEQDSK with a missing signal.
            if len(np.shape(res)) in transpose_plan:
                res = res.T
            results[signal] = res

    # Calculate derived quantities --------------------------------------------------------------------------------
    if 'psin' in d_params:
        psi_norm_f = results['ssibry'] - results['ssimag']
        # Prevent divide by 0 error by replacing 0s in the denominator
        problems = psi_norm_f == 0
        psi_norm_f[problems] = 1.0
        results['psin'] = (results['psirz'] - results['ssimag'][:, np.newaxis, np.newaxis]) / psi_norm_f[:, np.newaxis, np.newaxis]
        results['psin'][problems] = 0

    if 'psin1d' in d_params:
        mw = tolist(results['mw'])[0]
        if mw is None:
            mw = np.shape(results['psirz'])[1]
        results['psin1d'] = np.linspace(0, 1, int(mw))

    if 'br' in d_params or 'bz' in d_params or 'Br' in d_params or 'Bz' in d_params:
        r = results['r']
        z = results['z']
        psirz = results['psirz'] * np.sign(results['cpasma'])[:, np.newaxis, np.newaxis]
        rr, zz = np.meshgrid(results['r'], results['z'])
        [dpsi_dz, dpsi_dr] = np.gradient(psirz, z[1] - z[0], r[1] - r[0], axis=(1, 2))
        results['Br'] = dpsi_dz / rr
        results['Bz'] = -dpsi_dr / rr

    results['time'] = time_raw * unit_conversion

    return results


##############################################
# Read basic equilibrium data from TOKSEARCH #
##############################################
# THIS FUNCTION IS ONLY SUPPORTED FOR SERVER='DIII-D'
def read_basic_eq_from_toksearch(
    device='DIII-D',
    server=None,
    shots=None,
    tree='EFIT01',
    quiet=False,
    g_file_quantities=['r', 'z', 'rhovn'],
    a_file_quantities=['area'],
    derived_quantities=['psin', 'psin1d', 'time'],
    measurements=['fccurt'],
    other_results=['DATE_RUN'],
):
    from omfit_classes.omfit_toksearch import OMFITtoksearch, TKS_MdsSignal

    signals = {}

    # Format of TDI calls to MDSplus
    g_params = tolist(g_file_quantities)
    a_params = tolist(a_file_quantities)
    d_params = tolist(derived_quantities)
    measurements = tolist(measurements)

    o_params = tolist(other_results)
    # Add dependencies for derived quantities
    more_g = []
    more_a = []
    if 'psin' in d_params:
        more_g += ['psirz', 'ssimag', 'ssibry']
    if 'psin1d' in d_params:
        more_g += ['mw']
    if measurements or 'nebar_r0' in a_params or 'nebar_v1' in a_params or 'nebar_v2' in a_params or 'nebar_v3' in a_params:
        more_a = ['atime']

    for gg in more_g:
        if gg not in g_params:
            g_params += [gg]
    for aa in more_a:
        if aa not in a_params:
            a_params += [aa]
    if 'atime' in a_params:
        a_params.remove('atime')
    if device != 'DIII-D':
        raise RuntimeError("ONLY DIII-D DEVICES ARE SUPPORTED FOR TOKSEARCH USE")
    device_format = 'A'

    # Select device specific format
    form = '\\{efit_tree:}::TOP.RESULTS.{letter:}EQDSK.{signal:}'
    form2 = '\\{efit_tree:}::TOP.RESULTS.{signal:}'
    form3 = form2.replace('RESULTS', 'MEASUREMENTS')

    time_axis_3d = 2
    dims = [str(i) for i in range(time_axis_3d + 1)]  # num dimensions to be retrieved

    letter = 'G'
    signal = 'PSIRZ'
    psirz_call = form.format(efit_tree=tree, letter=letter, signal=signal)
    signals[psirz_call] = TKS_MdsSignal(psirz_call, tree, dims=dims)
    call = form.format(efit_tree=tree, letter=letter, signal='gtime')
    signals[call] = TKS_MdsSignal(call, tree)

    for letter, signal in zip('G' * len(g_params) + 'A' * len(a_params), g_params + a_params):
        call = form.format(efit_tree=tree, letter=letter, signal=signal)
        signals[call] = TKS_MdsSignal(call, tree)
    for signal in measurements:
        call = form3.format(efit_tree=tree, signal=signal)
        signals[call] = TKS_MdsSignal(call, tree, dims=dims)
    for signal in o_params:
        call = form2.format(efit_tree=tree, signal=signal)
        signals[call] = TKS_MdsSignal(call, tree)

    ## TO DO: CREATE A LIST OF signals
    toksearch_object = OMFITtoksearch(shots, signals).load()
    results = {}
    for shot in shots:
        results[shot] = read_basic_eq_from_mds(
            device,
            server,
            shot,
            tree,
            quiet,
            g_file_quantities,
            a_file_quantities,
            derived_quantities,
            measurements,
            other_results,
            toksearch_mds=toksearch_object,
        )
    return results


###########################################
# Create G-files and A-files from MDSplus #
###########################################
# fmt: off
def from_mds_plus(
    device=None,
    shot=None,
    times=None,
    exact=False,
    snap_file='EFIT01',
    time_diff_warning_threshold=10,
    fail_if_out_of_range=True,
    get_afile=True,
    get_mfile=False,
    show_missing_data_warnings=True,
    debug=False,
    quiet=False,
    close=False,
):
    """
    Gathers EFIT data from MDSplus, interpolates to the desired times, and creates a set of g/a/m-files from the results.

    Links to EFIT documentation::
        https://fusion.gat.com/theory/Efit                Home
        https://fusion.gat.com/theory/Efitiofiles         List of input/output files
        https://fusion.gat.com/theory/Efitin1             IN1 namelist description (primary input)

    :param device: string
        Name of the tokamak or MDSserver from whence cometh the data.

    :param shot: int
        Shot for which data are to be gathered.

    :param times: numeric iterable
        Time slices to gather in ms, even if working with an MDS server that normally operates in seconds.

    :param exact: bool
        Fail instead of interpolating if the exact time-slices are not available.

    :param snap_file: string
        Description of which EFIT tree to gather from.

    :param time_diff_warning_threshold: float
        Issue a warning if the difference between a requested time slice and the closest time slice in the source EFIT
        exceeds this threshold.

    :param fail_if_out_of_range: bool
        Skip requested times that fail the above threshold test.

    :param get_afile: bool
        gather A-file quantities as well as G-file quantities.

    :param get_mfile: bool
        gather M-file quantities as well as G-file quantities.

    :param show_missing_data_warnings: bool
        Print a warning for each missing item when setting it to a default value. May not be necessary because some
        things in the a-file don't seem very important and are always missing from MDSplus.

    :param debug: bool
        Save intermediate results to the tree for inspection.

    :param quiet: bool

    :param close: bool
        Close each file at each time before going on to the next time

    :return: a dictionary containing a set of G-files in another dictioanry named 'gEQDSK', and, optionally, a set of
        A-files under 'aEQDSK' and M-filess under 'mEQDSK'
    """

    # Get angry about bad inputs
    if shot is None or device is None or times is None:
        raise ValueError('Must specify shot, times, and device for from_mds_plus()!')

    # Sanitize inputs
    times = np.atleast_1d(times)
    # device = tokamak(device)

    def printq(*arg, **kw):
        if not quiet:
            print(*arg, **kw)

    def printdq(*arg, **kw):
        if not quiet:
            printd(*arg, **kw)

    # Announcements
    printq('Gathering EFIT from MDSplus: shot = {:}, snap/tree = {:}, times = {:}'.format(shot, snap_file, times))

    # Basic setup and info
    def printw2(warning_message):
        if not quiet:
            if show_missing_data_warnings:
                printw(warning_message)
            else:
                printd(warning_message)

    f_coil_counts = {'DIII-D': 18,}  # Determines default nfcoil0 (device dependent number of F-coils).

    if exact:
        time_diff_warning_threshold = 0

    output = {}

    # PART 0: General gathering ========================================================================================

    # Part 0.1: g-file info --------------------------------------------------------------------------------------------

    # Set up translation table
    translate = {"RZERO": "RCENTR", "MH": "NH", "MW": "NW", "XDIM": "RDIM", "SSIMAG": "SIMAG", "SSIBRY": "SIBRY", "CPASMA": "CURRENT"}

    # List of time varying quantities to interpolate
    time_varying = [
        'ZDIM',
        'RMAXIS',
        'ZMAXIS',
        'BCENTR',
        'FPOL',
        'PRES',
        'FFPRIM',
        'PPRIME',
        'PSIRZ',
        'QPSI',
        'NBBBS',
        'LIMITR',
        'RBBBS',
        'ZBBBS',
        'RHOVN',
    ]

    other_quantities = ['ECASE', 'CASE', 'RGRID', 'ZMID', 'LIM', 'RLIM', 'ZLIM', 'KVTOR', 'RVTOR', 'NMASS', 'DATE_RUN', 'R', 'Z']

    # Part 0.2: a-file info --------------------------------------------------------------------------------------------

    a_time_varying = [
        'rq1',
        'rq2',
        'rq3',
        'li',
        'li3',
        'alpha',
        'area',
        'atime',
        'aminor',
        'bcentr',
        'betan',
        'betap',
        'betapd',
        'betat',
        'betatd',
        'bpolav',
        'bt0',
        'bt0vac',
        'diamgc',
        'chilibt',
        'chipre',
        'j1n',
        'j0n',
        'j95n',
        'j99n',
        'condno',
        'cprof',
        'diamag',
        'diludom',
        'diludomm',
        'dminlx',
        'dminux',
        'dolubaf',
        'dolubafm',
        'tritop',
        'tribot',
        'kappa',
        'kappa0',
        'fexpan',
        'fexpvs',
        'limloc',
        'chimse',
        'sepbot',
        'gapbot',
        'sepin',
        'gapin',
        'oring',
        'sepout',
        'gapout',
        'gaptop',
        'septop',
        'ipmeas',
        'pbinj',
        'peak',
        'pp95',
        'psin21',
        'psin32',
        'psiref',
        'psurfa',
        'qmerci',
        'qmflag',
        'ql',
        'q95',
        'qmin',
        'q0',
        'qstar',
        'ratsol',
        'rbcent',
        'rcur',
        'r0',
        'rmidin',
        'rmidout',
        'rsurf',
        'rq21top',
        'rq32in',
        'rhoqmin',
        'rttt',
        'rvsid',
        'rvsin',
        'rvsiu',
        'rvsod',
        'rvsou',
        'rvsout',
        's1',
        's2',
        's3',
        'sepexp',
        'seplim',
        'sepnose',
        'shear',
        'psibdy',
        'psi0',
        'slantl',
        'slantu',
        'drsep',
        'ssi01',
        'ssi95',
        'taudia',
        'taumhd',
        'tavem',
        'tchimls',
        'error',
        'tflux',
        'chisq',
        'twagap',
        'nindx',
        'vloopmhd',
        'volume',
        'vsurf',
        'wbdot',
        'wpdot',
        'wmhd',
        'wdia',
        'xbetapr',
        'indent',
        'xnnc',
        'yyy2',
        'zcur',
        'z0',
        'zsurf',
        'zuperts',
        'zvsid',
        'zvsin',
        'zvsiu',
        'zvsod',
        'zvsou',
        'zvsout',
        'ipmhd',
    ]

    special_a_time_varying = [  # These won't default to 0 if missing at the end (because they'll get popped out)
        'nebar_r0',
        'nebar_v1',
        'nebar_v2',
        'nebar_v3',
        'pathr0',
        'pathv1',
        'pathv2',
        'pathv3',
        'rxpt1',
        'rxpt2',
        'zxpt1',
        'zxpt2',
    ]

    a_meas = ['ccbrsp', 'csilop', 'cmpr2', 'eccurt',]

    # Part 0.3: m-file info --------------------------------------------------------------------------------------------
    m_time_varying = [
        'mtime',
        'a1gam',
        'a2gam',
        'a3gam',
        'a4gam',
        'a5gam',
        'a6gam',
        'a7gam',
        'a8gam',
        'ccbrsp',
        'cchisq',
        'cdflux',
        'cecurr',
        'cerror',
        'chigam',
        'cmgam',
        'cmpr2',
        'cpasma',
        'cpress',
        'csilop',
        'czmaxi',
        'darea',
        'diamag',
        'eccurt',
        'expmpi',
        'fccurt',
        'fixgam',
        'fwtec',
        'fwtfc',
        'fwtgam',
        'fwtmp2',
        'fwtsi',
        'mcal_gain',
        'mcal_offset',
        'mcal_scale',
        'mcal_slope',
        'msebkp',
        'msefitfun',
        'plasma',
        'pressr',
        'rpress',
        'rrgam',
        'saimpi',
        'saipre',
        'saisil',
        'sigdia',
        'siggam',
        'sigpre',
        'silopt',
        'tangam',
        'tangam_uncor',
        'vport',
        'xrsp',
        'zpress',
        'zzgam',
    ]

    # Descriptive names of the vars
    m_longnames = {
        'a1gam': 'viewing geometry coefficients of MSE channels',
        'a2gam': 'viewing geometry coefficients of MSE channels',
        'a3gam': 'viewing geometry coefficients of MSE channels',
        'a4gam': 'viewing geometry coefficients of MSE channels',
        'a5gam': 'viewing geometry coefficients of MSE channels',
        'a6gam': 'viewing geometry coefficients of MSE channels',
        'a7gam': 'viewing geometry coefficients of MSE channels',
        'a8gam': 'viewing geometry coefficients of MSE channels',
        'ccbrsp': 'calculated F-coil currents (Amp)',
        'cchisq': 'chisq vs. iteration',
        'cdflux': 'calculated diamagnetic flux',
        'cecurr': 'calculated E-coil currents (Amp)',
        'cerror': 'error vs. iteration',
        'chigam': 'chisq vs. polarimetries',
        'cmgam': 'calculated polarimetry signals',
        'cmpr2': 'calculated magnetic probes',
        'cpasma': 'calculated plasma current (Amp)',
        'cpress': 'calculated pressure vs. normalized flux (kinetic fits only)',
        'csilop': 'calculated flux loops',
        'czmaxi': 'Zm (cm) vs. iteration',
        'darea': 'plasma coefficients normalization',
        'diamag': 'measured diamagnetic flux',
        'eccurt': 'measured E-coil currents (Amp)',
        'expmpi': 'measured magnetic probes',
        'fccurt': 'measured F-coil currents (Amp)',
        'fixgam': 'radians correction of tangam for spatial averaging effects',
        'fwtec': 'weight for E-coil currents',
        'fwtfc': 'weight for F-coil currents',
        'fwtgam': 'fitting weight for MSE channels',
        'fwtmp2': 'weight for magnetic probes',
        'fwtsi': 'weight for flux loops',
        'mcal_gain': 'gain param for tangent offset function',
        'mcal_offset': 'offset param for tangent offset function',
        'mcal_scale': 'scale param for tangent offset function',
        'mcal_slope': 'slope param for tangent offset function',
        'msebkp': 'background substraction switch',
        'msefitfun': 'MSE fit function',
        'plasma': 'measured plasma current (Amp)',
        'pressr': 'measured pressure vs. normalized flux (kinetic fits only)',
        'rpress': '<0 - input pressure profile vs. flux; >0 - R coordinates ofinput pressure profile (m)',
        'rrgam': 'radius of MSE channels',
        'saimpi': 'chisq vs. magnetic probes',
        'saipre': 'chisq of pressure',
        'saisil': 'chisq vs. PSI loops',
        'shot': 'shot number',
        'sigdia': 'uncertainty of diamagnetic flux',
        'siggam': 'uncertainty of tangam',
        'sigpre': 'uncertainty for pressure',
        'silopt': 'measured flux loops',
        'tangam': 'tangent of measured MSE pitch angle',
        'tangam_uncor': 'tangent of measured MSE pitch angle w/o cer correction',
        'vport': 'view port locations of MSE system',
        'xrsp': 'plasma coefficients',
        'zpress': 'Z coordinates of input pressure profile (m)',
        'zzgam': 'Z position of MSE channels',
    }

    # only names of the second dim here, first dim is always dim_time
    m_dim_names = {
        "a1gam": "dim_nstark",
        "a2gam": "dim_nstark",
        "a3gam": "dim_nstark",
        "a4gam": "dim_nstark",
        "a5gam": "dim_nstark",
        "a6gam": "dim_nstark",
        "a7gam": "dim_nstark",
        "a8gam": "dim_nstark",
        "ccbrsp": "dim_nfcoil",
        "cchisq": "dim_nitera",
        "cdflux": None,
        "cecurr": "dim_nesum",
        "cerror": "dim_nitera",
        "chigam": "dim_nstark",
        "cmgam": "dim_nstark",
        "cmpr2": "dim_magpri",
        "cpasma": None,
        "cpress": "dim_npress",
        "csilop": "dim_nsilop",
        "czmaxi": "dim_nitera",
        "darea": None,
        "diamag": None,
        "eccurt": "dim_nesum",
        "expmpi": "dim_magpri",
        "fccurt": "dim_nfcoil",
        "fixgam": "dim_nstark",
        "fwtec": "dim_nesum",
        "fwtfc": "dim_nfcoil",
        "fwtgam": "dim_nstark",
        "fwtmp2": "dim_magpri",
        "fwtsi": "dim_nsilop",
        "mcal_gain": "dim_nstark",
        "mcal_offset": "dim_nstark",
        "mcal_scale": "dim_nstark",
        "mcal_slope": "dim_nstark",
        "msebkp": None,
        "msefitfun": None,
        "plasma": None,
        "pressr": "dim_npress",
        "rpress": "dim_npress",
        "rrgam": "dim_nstark",
        "saimpi": "dim_magpri",
        "saipre": "dim_npress",
        "saisil": "dim_nsilop",
        "shot": None,
        "sigdia": None,
        "siggam": "dim_nstark",
        "sigpre": "dim_npress",
        "silopt": "dim_nsilop",
        "tangam": "dim_nstark",
        "tangam_uncor": "dim_nstark",
        "time": None,
        "vport": "dim_nstark",
        "xrsp": "dim_npcurn",
        "zpress": "dim_npress",
        "zzgam": "dim_nstark",
    }

    dim_dict = SortedDict(
        {
            'dim_magpri': 1,
            'dim_nesum': 1,
            'dim_nfcoil': 1,
            'dim_nitera': 1,
            'dim_npcurn': 1,
            'dim_npress': 1,
            'sim_nsilop': 1,
            'dim_nstark': 1,
            'dim_scalar': 1,
            'dim_time': 1,
        }
    )

    # Part 0.4: the units and whatnot ----------------------------------------------------------------------------------
    # This is a temporary measure intended to prevent apparently bad results from MDSplus from being used normally.
    bad_a_quantities = []  # Not needed presently, so left empty.

    # Unit conversion factors. There is not a clean way to assign these automatically because the EFIT files use a
    # mixture of m and cm. The units of each signal have to be assigned on a case-by-case basis.
    # These are the names BEFORE translation! <-- !!!!
    ucf = {
        1e2: [  # List quantities which need a unit conversion factor of 1e2, such as from cm to m
            # This following set was determined by reading the EFIT documentation for the A-file:
            'rq1',
            'rq2',
            'rq3',
            'aminor',
            'gapbot',
            'sepbot',
            'gapin',
            'sepin',
            'gapout',
            'sepout',
            'gaptop',
            'septop',
            'rbcent',
            'rco2r',
            'rco2v',
            'rcur',
            'r0',
            'rsurf',
            'rseps',
            'rvsin',
            'rvsout',
            'rxpt1',
            'rxpt2',
            'sepexp',
            'seplim',
            'sepnos',
            'slantl',
            'slantu',
            'drsep',
            'zcur',
            'z0',
            'zsurf',
            'zxpt1',
            'zxpt2',
            'zvsin',
            'zvsout',
            # Units not listed in EFIT A-file documentation as being cm, but which seem to need to be converted to cm:
            'diludom',
            'diludomm',
            'dminlx',
            'dminux',
            'dolubaf',
            'dolubafm',
            'rvsid',
            'rvsiu',
            'rvsod',
            'rvsou',
            'sepnose',
            'zuperts',
            'zvsid',
            'zvsiu',
            'zvsod',
            'zvsou',
            'zxpt1',
            'zxpt2',
        ],
        1e3: [  # List quantities which need a conversion factor of 1e3, such as would be needed to go from s to ms.
            'taumhd',
            'taudia',
            'tavem',
        ],
        1e4: ['area',],
        1e6: ['wmhd', 'wdia', 'volume',],
    }

    # Transform the unit conversion factors into something easier to use in a loop through quantities
    aeqdsk_unit_factors = {}
    for factor in list(ucf.keys()):
        for quantity in ucf[factor]:
            aeqdsk_unit_factors[quantity] = factor

    # List of quantities which should be positive
    absolute = ['wplasm',]

    # Part 0.x: gather it ----------------------------------------------------------------------------------------------

    # Determine what we need from measurements
    meas = []
    if get_afile:
        meas = copy.copy(a_meas)
    if get_mfile:
        meas += copy.copy(m_time_varying)

    # Read data from MDSplus. read_basic_eq_from_mds() will handle transposes and unit conversions.
    efit_info = read_basic_eq_from_mds(
        device=device,
        server=None,
        shot=shot,
        tree=snap_file,
        g_file_quantities=time_varying + list(translate.keys()) + other_quantities,
        a_file_quantities=a_time_varying + special_a_time_varying if get_afile else [],
        measurements=meas,
        get_all_meas=get_mfile,  # If we are getting m files, get real m times to determine strict time matching, because in theory a-file time might not be in measurement time at all.
        derived_quantities=['time'],
        other_results=['DATE_RUN', 'CODE_VERSION'],
        quiet=quiet,
    )
    # It's okay for DATE_RUN to be in two places; DATE_RUN from other_results will overwrite DATE_RUN from
    # g_file_quantities if it exists, but if other_results/DATE_RUN returns None, it won't overwrite
    # g_file_quantities/DATE_RUN.

    if debug:
        output.setdefault('debug', {})['efit_info'] = efit_info

    if efit_info is None:
        raise OMFITexception('Fail! Could not gather EFIT data from MDSplus for shot = {}, snap = {}.'.format(shot, snap_file))

    # Get timing
    efit_time = efit_info['time']
    nte = efit_time.shape[0]  # Number of time slices in the source EFIT

    # nt = len(times)  # Number of time slices in the desired output

    # PART 1: G-FILE ===================================================================================================

    # Get the case information. This is a string array
    case = efit_info['ECASE']
    if case is None:  # read_basic_eq_from_mds() returns None for things it can't find.
        case = efit_info['CASE']
    if debug:
        output['debug']['case'] = case

    if case is not None and hasattr(case, 'shape'):
        # handle the case where CASE is stored as a string
        if case.shape == (1,):
            case = np.array(case[0].split('\n'))

        # handle the case where CASE is stored as a unidimensional array
        if efit_time.shape[0] not in case.shape:
            case = case.reshape((nte, -1))

        if isinstance(case[0], str):
            efit_code_ver = case[0].split()[0]
            efit_month_day = '/'.join(case[0].split()[1].split('/')[:2])
            if is_device(device, 'CMOD'):
                efit_year = '/' + case[0].split()[2].split('/')[1]
                efit_shot_string = case[0].split()[3]
            else:
                efit_year = '/' + case[0].split()[1].split('/')[2]
                efit_shot_string = case[0].split()[2]
            efit_unused = ''
        else:
            efit_code_ver = case[0][0]
            efit_month_day = case[0][1]
            efit_year = case[0][2]
            efit_shot_string = case[0][3]
            # efit_first_time_string = case[0][4]
            efit_unused = case[0][5]

    else:
        efit_code_ver = '  EFITD '
        efit_shot_string = '#' + str(shot)
        # efit_first_time_string = str(efit_time[0]) + 'ms'
        efit_unused = '        '
        if efit_info['DATE_RUN'] is not None:
            # Make sure it's string, not a 1 element array holding a string
            date_run = ' '.join(tolist(efit_info['DATE_RUN']))
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month = str(months.index(date_run.split()[1]))
            efit_month_day = month + '/' + date_run.split()[2]
            efit_year = '/' + date_run.split()[-1]
        else:
            efit_year = efit_month_day = None

    efit_time_string = '{:6}ms'  # The {:6} field will be filled in later, using .format(t)
    # Assemble the new version of the case field
    new_case = [efit_code_ver, efit_month_day, efit_year, efit_shot_string, efit_time_string, efit_unused]
    new_case[-1] = snap_file
    # Field index 4 of new_case is a string with {:} ready to accept time.

    # Set up interpolating functions. This is done before the time loop and the results evaluated in the time loop.
    interpolations = {}
    dummy_interpolation = interpolate.interp1d([0, 1], [np.NaN] * 2, bounds_error=False, axis=0)  # Handle missing / None

    class JustReturn(object):
        """
        A sort of dummy interpolation to make it simple to deal with things that only have one time-slice
        Give it the value you want it to return all the time. Call it like it's an interpolation, but it ignores the
        independent coordiante you pass to __call__ and just returns the value you initialized with.
        """

        def __init__(self, y):
            self.y = y

        def __call__(self, x):
            return self.y

    for item in translate:
        if efit_info[item] is None:
            interpolations[item] = dummy_interpolation
        else:
            if len(efit_info[item]) == 1:
                # Handle cases where there is only one sample, which could happen with a special EFIT of only one slice.
                interpolations[item] = JustReturn(efit_info[item][0])
            else:
                interpolations[item] = interpolate.interp1d(efit_time, efit_info[item], bounds_error=False, axis=0)
    for item in time_varying:
        if efit_info[item] is None:
            interpolations[item] = dummy_interpolation
        else:
            if len(efit_info[item]) == 1:
                # Handle cases where "time varying" data have only one sample, because they are not really time varying.
                # For example: LIMITR at EAST. Solve by making a simple, two-point dummy interpolation to eval later.
                interpolations[item] = JustReturn(efit_info[item][0])
            else:
                interpolations[item] = interpolate.interp1d(efit_time, efit_info[item], bounds_error=False, axis=0)

    # Set up a collection to contain output
    out = output.setdefault('gEQDSK', {})

    # Loop through the requested times and make a G-file for each one
    for t in times:
        g_file_name = 'g' + format(int(shot), "06d") + "." + format(int(t), "05d")
        if t - int(t) >= 1e-3:
            # Handle sub-ms timing to adding _000 to the filename
            g_file_name += '_{:03d}'.format(int((t - int(t)) * 1000))
        if min(abs(t - efit_time)) > time_diff_warning_threshold:
            closest_efit = efit_time[closestIndex(efit_time, t)]
            if fail_if_out_of_range:
                note = 'FAIL'
            else:
                note = 'WARNING'
            printw(
                '{:}: requested time {:} ms is more than {:} ms away from closest time ({:} ms) in source EFIT!'.format(
                    note, t, time_diff_warning_threshold, closest_efit
                )
            )
            if fail_if_out_of_range:
                printe('Skipped {:} because time difference was too large.'.format(g_file_name))
                continue

        printq('  Loading {:}:'.format(g_file_name), end='')
        printq('CASE', end='')

        # Initialize the new g-file
        out[t] = g_file = OMFITgeqdsk(g_file_name)
        g_case = copy.copy(new_case)
        g_case[4] = g_case[4].format(t)
        g_file['CASE'] = g_case

        # Handle items that need tag name translation and time interpolation
        for item in translate:
            printq(',' + item, end='')
            g_file[translate[item]] = interpolations[item](t)

        # Items which do not vary with time - simple copy
        printq(', RLEFT', end='')
        g_file['RLEFT'] = efit_info['RGRID'][0]
        if isinstance(g_file['RLEFT'], np.ndarray):
            g_file['RLEFT'] = g_file['RLEFT'][0]

        printq(',ZMID', end='')
        if efit_info['ZMID'] is not None:
            g_file['ZMID'] = efit_info['ZMID'][0]
            if isinstance(g_file['ZMID'], np.ndarray):
                g_file['ZMID'] = g_file['ZMID'][0]
        else:
            g_file['ZMID'] = 0  # I don't know

        if efit_info['LIM'] is not None:
            printq(', RLIM', end='')
            g_file['RLIM'] = efit_info['LIM'][:, 0]
            printq(', ZLIM', end='')
            g_file['ZLIM'] = efit_info['LIM'][:, 1]
        else:
            printq(', RLIM', end='')
            g_file['RLIM'] = efit_info['RLIM'][0, :]
            printq(', ZLIM', end='')
            # Is this 1 index correct if LIM is already split into RLIM and ZLIM?
            g_file['ZLIM'] = efit_info['ZLIM'][1, :]

        if is_device(device, 'CMOD'):
            # limiter surface description in EFIT output is incomplete. Load rlim & zlim explicitely from MDSplus:
            g_file['RLIM'] = OMFITmdsValue('CMOD', 'analysis', shot, '\\analysis::top.limiters.wall.rlim').data()
            g_file['ZLIM'] = OMFITmdsValue('CMOD', 'analysis', shot, '\\analysis::top.limiters.wall.zlim').data()

        g_file['KVTOR'] = 0.0
        g_file['RVTOR'] = g_file['RCENTR']
        g_file['NMASS'] = 0.0

        # Time varying items which require interpolation
        for item in time_varying:
            printq(',' + item, end='')
            g_file[item] = interpolations[item](t)
        printq('')

        # Replace NaNs with 0s
        for item in g_file:
            if is_numeric(g_file[item]) and np.atleast_1d(~np.isfinite(g_file[item])).all():
                g_file[item] = np.zeros(np.shape(g_file[item]))

        # Convert length 1 arrays to floats
        for item in g_file.keys():
            if item not in ['AuxNamelist', 'AuxQuantities', 'fluxSurfaces'] and np.atleast_1d(g_file[item]).shape[0] == 1:
                if is_numeric(np.atleast_1d(g_file[item])[0]):
                    g_file[item] = float(g_file[item])
                else:
                    g_file[item] = np.atleast_1d(g_file[item])[0]

        # Convert floats to integers
        for item in g_file.keys():
            if (
                np.atleast_1d(is_numeric(g_file[item])).all()
                and np.atleast_1d(np.isfinite(g_file[item])).all()
                and isinstance(g_file[item], (float, np.floating))
                and g_file[item] == int(g_file[item])
            ):
                g_file[item] = int(g_file[item])

        # Touch ups
        if ('NBBBS' not in g_file) or (g_file['NBBBS'] is None) or ~np.isfinite(g_file['NBBBS']):
            # The R grid never reaches all the way to the machine axis, so points at R=0 are padding or junk.
            with np.errstate(invalid='ignore'):
                g_file['NBBBS'] = np.sum(g_file['RBBBS'] > 0) if len(g_file['RBBBS']) else 0
        try:
            g_file['NBBBS'] = int(g_file['NBBBS'])
        except ValueError:
            g_file['NBBBS'] = 0

        printdq("omfit_eqdsk/from_mds_plus: g_file['NBBBS'] = {}".format(g_file['NBBBS']))
        g_file['RBBBS'] = g_file['RBBBS'][: g_file['NBBBS']]
        g_file['ZBBBS'] = g_file['ZBBBS'][: g_file['NBBBS']]
        if debug:
            output['g_file_debug'] = g_file

        if g_file['NH'] == 0:
            # These are always square and sometimes transposed, so I'm not 100% sure which is 0 and which is 1. Sorry.
            g_file['NH'] = np.shape(g_file['PSIRZ'])[0]
        if g_file['NW'] == 0:
            g_file['NW'] = np.shape(g_file['PSIRZ'])[1]

        if g_file['ZDIM'] == 0:
            g_file['ZDIM'] = efit_info['Z'].max() - efit_info['Z'].min()
        if g_file['RDIM'] == 0:
            g_file['RDIM'] = efit_info['R'].max() - efit_info['R'].min()
        if g_file['LIMITR'] == 0:
            g_file['LIMITR'] = len(g_file['RLIM'])

        # Cleanup
        must_be_array = ['RHOVN']
        for mba in must_be_array:
            # Delete invalid entries: items that must be arrays in order to be valid
            try:
                lmba = len(g_file.get(mba, None))
            except TypeError:

                lmba = 0
            if lmba < 2:
                printq('Removing quantity {} because it is supposed to be an array but its value is {}'.format(mba, g_file.get(mba, None)))
                g_file.pop(mba, None)

        # COCOS
        if (g_file['CURRENT'] == 0) or (g_file['BCENTR'] == 0):
            printw('Skipping COCOS transforms for G-file {} @ {} because CURRENT or BCENTR is zero'.format(shot, t))
            if close:
                g_file.close()
        else:
            cocosnum = 1
            g_file._cocos = g_file.native_cocos()
            if close:
                g_file.cocosify(cocosnum, calcAuxQuantities=False, calcFluxSurfaces=False)
                g_file.close()
            else:
                g_file.cocosify(cocosnum, calcAuxQuantities=True, calcFluxSurfaces=True)

    printq('Done getting G-files from MDSplus: {shot:}, {snap:}, {times:}'.format(shot=shot, snap=snap_file, times=times))

    # PART 2: A-FILE ===================================================================================================

    if get_afile:
        a_time = efit_info['atime']
        if get_mfile:
            m_time = efit_info['mtime']

        a_interpolations = {}
        a_take_nearest = {}
        for item in a_time_varying + special_a_time_varying:
            if item in efit_info and efit_info[item] is not None and len(tolist(efit_info[item])) and item not in bad_a_quantities:
                if is_string(tolist(efit_info[item])[0]) or (len(a_time) < 2):
                    # Handle strings or cases where there is only one time-slice
                    printdq(' A-file: taking nearest value for {}'.format(item))
                    a_take_nearest[item] = efit_info[item]
                else:
                    printdq(' A-file: interpolating {}'.format(item))
                    # Unit conversion has to happen on the way in to avoid interacting with default values.
                    u_factor = aeqdsk_unit_factors.get(item, 1.0)
                    a_interpolations[item] = interpolate.interp1d(a_time, efit_info[item] * u_factor, bounds_error=False, axis=0)
                    if (u_factor != 1.0) and (not quiet):
                        printd('   Applied unit conversion factor of {} to {}'.format(u_factor, item))
            else:
                if (item in bad_a_quantities) and (not quiet):
                    printd(' A-file: suppressing {} because it is flagged as being recorded badly in MDSplus.'.format(item))
                else:
                    printdq(' A-file: SKIPPING {} because it is missing or is None.'.format(item))

        printdq("np.shape(efit_info['csilop']) = {}".format(np.shape(efit_info['csilop'])))
        for item in a_meas:
            if len(a_time) < 2:
                # Dummy interpolation to make it return the value we want all the time, since there is only one slice
                a_interpolations[item] = JustReturn(np.atleast_1d(efit_info[item])[0])
            elif get_mfile:  # that would mean get_all_meas was set
                a_interpolations[item] = interpolate.interp1d(m_time, efit_info[item], bounds_error=False, axis=0)
            else:
                a_interpolations[item] = interpolate.interp1d(a_time, efit_info[item], bounds_error=False, axis=0)

        # Set up a collection to contain output
        out = output.setdefault('aEQDSK', {})

        # Loop through the requested times and make an A-file for each one
        for t in times:
            a_file_name = 'a' + format(shot, "06d") + "." + format(int(t), "05d")
            if t - int(t) >= 1e-3:
                # Handle sub-ms timing to adding _000 to the filename
                a_file_name += '_{:03d}'.format(int(t - int(t) * 1000))
            if min(abs(t - a_time)) > time_diff_warning_threshold:
                closest_efit = a_time[closestIndex(a_time, t)]
                if fail_if_out_of_range:
                    note = 'FAIL'
                else:
                    note = 'WARNING'
                printw(
                    '{:}: requested time {:} ms is more than {:} ms away from closest time ({:} ms) in source EFIT!'.format(
                        note, t, time_diff_warning_threshold, closest_efit
                    )
                )
                if fail_if_out_of_range:
                    printe('Skipped {:} because time difference was too large.'.format(a_file_name))
                    continue

            # Initialize the new a-file
            out[t] = a_file = OMFITaeqdsk(a_file_name)
            printdq('Initial keys in aeqdsk: {}'.format(list(a_file.keys())))

            printq('  Loading {:}:'.format(a_file_name), end='')
            printq('CASE', end='')

            # Header
            a_file['__header__'] = '{datetime:} {code_version:}\n{shot:7d}{one:16d}\n{time:}'.format(
                shot=shot,
                time=t,
                one=1,
                datetime=np.atleast_1d(efit_info['DATE_RUN'])[0],
                code_version=np.atleast_1d(efit_info['CODE_VERSION'])[0],
            )
            a_file['__footer__'] = ''

            # Time varying items which require interpolation or selecting nearest slice
            for item in a_time_varying + special_a_time_varying:
                if item in a_interpolations:
                    printq(',' + item, end='')
                    a_file[item.lower()] = a_interpolations[item](t)
                elif item in a_take_nearest:
                    printq(',' + item, end='')
                    a_file[item.lower()] = a_take_nearest[item][closestIndex(a_time, t)]
                if item in a_file and len(np.atleast_1d(a_file[item])) == 1:
                    a_file[item.lower()] = np.atleast_1d(a_file[item])[0]

            printq('')
            printdq('Keys in aeqdsk after loading basics: {}'.format(list(a_file.keys())))

            # Measurements
            for item in a_meas:
                a_file[item.lower()] = a_interpolations[item](t)

            # Things that need to be renamed and/or converted (old, gathered in MDSplus : new, saved in A-file)
            translations = {
                'area': 'areao',  # Cross sectional area in old: m2, new: cm2
                'bt0': 'btaxp',  # Toroidal magnetic field at magnetic axis in Tesla
                'bt0vac': 'btaxv',  # Vacuum toroidal magnetic field at magnetic axis in Tesla
                'atime': 'time',  # Time in ms
                'zcur': 'zcurrt',  # Z in cm at current centroid
                'rcur': 'rcurrt',
                'kappa': 'eout',
                'drsep': 'ssep',
                'vsurf': 'vsurfa',
                'rhoqmin': 'rqqmin',
                'q95': 'qpsib',
                'chisq': 'tsaisq',
                'septop': 'otops',
                'li': 'ali',
                'li3': 'ali3',
                'sepout': 'orighs',
                'chimse': 'chigamt',
                'ipmeas': 'pasmat',
                'sepin': 'olefs',
                'gapin': 'oleft',
                'psi0': 'simagx',
                'wdia': 'wplasmd',
                'wmhd': 'wplasm',
                'z0': 'zmagx',
                'rbcent': 'rcencm',
                'sepbot': 'obots',
                'gapbot': 'obott',
                'indent': 'xndnt',
                'gaptop': 'otop',
                'vloopmhd': 'vloopt',
                'volume': 'vout',
                'q0': 'qqmagx',
                'r0': 'rmagx',
                'gapout': 'oright',
                'ql': 'qout',
                'ipmhd': 'cpasma',
                'aminor': 'aout',
                'j1n': 'cj1ave',
                'qmin': 'qqmin',
                'qstar': 'qsta',
                'rq1': 'aaq1',
                'nindx': 'vertn',
                'rq3': 'aaq3',
                'rq2': 'aaq2',
                'j0n': 'cjor0',
                'shear': 'shearb',
                'diamgc': 'cdflux',  # Computed diamagnetic flux in Volt-sec
                'kappa0': 'elongm',
                'error': 'terror',
                'tritop': 'doutu',
                'tribot': 'doutl',
                'zsurf': 'zout',
                'psibdy': 'sibdry',
                'j99n': 'cjor99',
                'j95n': 'cjor95',
                'rsurf': 'rout',
            }  # MDS : EFIT

            '''
            # The translation table may be obtained by using this code snippet in the command box:
            shot = 173237
            device = 'DIII-D'
            a = OMFITmds(treename='efit01', shot=shot, server=device)['RESULTS']['AEQDSK']
            high_priority = {}
            low_priority = {}
            if True:  # Change to False for repeats to save time
                for k in a.keys():
                    if 'EFIT_NAME' in a[k] and np.atleast_1d(a[k]['EFIT_NAME'].data())[0]:
                        high_priority[np.atleast_1d(a[k]['EFIT_NAME'].data())[0]] = k
                    else:
                        low_priority[k] = k
                things = copy.deepcopy(low_priority)
                things.update(high_priority)
            print(repr(things))
            for k, v in things.items():
                if k != v and k.strip():
                    print("'{}': '{}',".format(v.lower(), k.lower()))
            '''

            for old, new in list(translations.items()):
                if old in a_file:
                    a_file[new] = a_file.pop(old)
                elif not quiet:
                    printw('WARNING: {} missing from A-file. Cannot translate {} --> {}!'.format(old, old, new))

            # Other information
            a_file['shot'] = shot

            # Error flags. I am setting these to their no-error state on the assumption that the case wouldn't be in MDS
            # if there were an error.
            a_file.setdefault('jflag', 1)  # This would be 0 if there were an error.
            a_file.setdefault('lflag', 0)  # Another error flag, this one is bad if > 0.

            # Handle some special quantities
            a_file['rseps'] = np.array([a_file.pop('rxpt1'), a_file.pop('rxpt2')])
            a_file['zseps'] = np.array([a_file.pop('zxpt1'), a_file.pop('zxpt2')])

            # CO2 density measurements---
            # CO2 radial system; just one chord as of 20171013, so just fill it in.
            # The complexity is from turning it into an array and converting units.
            if 'nebar_r0' in a_file:
                # Line average electron density in cm3 from radial CO2 chord
                a_file['dco2r'] = np.array([a_file.pop('nebar_r0')])
                a_file['mco2r'] = len(a_file['dco2r'])  # Number of radial CO2 density chords
            else:
                a_file['mco2r'] = 1
                a_file['dco2r'] = np.zeros(a_file['mco2r'])
                printw2(' A-file: Missing radial CO2 density information, setting MCO2R=1 and DCO2R=[0].')
            if 'pathr0' in a_file:
                a_file['rco2r'] = np.array([a_file.pop('pathr0') * 100.0])  # Path len (cm), radial CO2 density chord
            else:
                a_file['rco2r'] = np.zeros(a_file['mco2r'])
                printw2(' A-file: Missing radial CO2 density path length RCO2R, filling in with [0].')

            # CO2 vertical system; three chords as of 20171013. Allow for the possibility that some but not all
            # densities are missing, and a different subset of path lengths may be missing.
            a_file['mco2v'] = 0
            a_file['dco2v'] = np.array([])
            a_file['rco2v'] = np.array([])
            for i, vert in enumerate(['v1', 'v2', 'v3']):
                if 'nebar_{}'.format(vert) in a_file or 'path{}'.format(vert) in a_file:
                    # Either the density or the path length is recorded, so we have to deal with this one.
                    a_file['mco2v'] += 1  # Number of vertical CO2 density chords

                    # Line avg electron density in cm3 from vertical CO2 chord
                    if 'nebar_{}'.format(vert) in a_file:
                        a_file['dco2v'] = np.append(a_file['dco2v'], a_file.pop('nebar_{}'.format(vert)))
                    else:
                        printw2(
                            ' A-file: Missing CO2 density for chord {} (DCO2V[{}]), '
                            'although path length is available; filling with 0.'.format(vert, i)
                        )
                        a_file['dco2v'] = np.append(a_file['dco2v'], 0)

                    # Path length in cm of vertical CO2 density chord
                    if 'path{}'.format(vert) in a_file:
                        a_file['rco2v'] = np.append(a_file['rco2v'], a_file.pop('path{}'.format(vert)) * 100.0)
                    else:
                        printw2(
                            ' A-file: Missing CO2 path length for chord {} (DCO2V[{}]), '
                            'although density is available; filling with 0.'.format(vert, i)
                        )
                        a_file['rco2v'] = np.append(a_file['rco2v'], 0)

            if a_file['mco2v'] == 0:
                printw(' A-file: Missing vertical CO2 density information MCO2V and DCO2V, filling in with 1 and [0].')
                a_file['mco2v'] = 1
                a_file['dco2v'] = np.zeros(a_file['mco2v'])

            # Undocumented EFIT parameters that are needed for the format, but don't seem to be saved in MDSplus by
            # default.
            lengths_of_things = {'magpri0': 'cmpr2', 'nesum0': 'eccurt', 'nfcoil0': 'ccbrsp', 'nsilop0': 'csilop',}
            for length, thing in list(lengths_of_things.items()):
                if thing in a_file:
                    a_file[thing] = np.atleast_1d(a_file[thing])
                    a_file.setdefault(length, len(a_file[thing]))
                else:
                    a_file.setdefault(length, 0)
            filler = ['nlnew', 'nlold']
            for fill in filler:
                a_file.setdefault(fill, 0)
            a_file.setdefault('cmpr2', np.zeros(76))  # Length of array may vary.

            # Fill in non-zero defaults
            def_100s = ['aaq1', 'aaq2', 'aaq3']  # Minor radius of q = 1, 2, 3 surfaces in cm, 100 if not found.
            for item in def_100s:
                if item not in a_file and item not in list(translations.keys()):
                    a_file[item] = 100.0  # cm
                    printw2(' A-file: {} was missing, so was filled in with 100.0.'.format(item))

            # If anything else is still missing, fill it with zeros
            for item in a_time_varying + a_meas + list(translations.values()):
                if item not in a_file and item not in list(translations.keys()) and item not in special_a_time_varying:
                    a_file[item] = 0.0
                    printw2(' A-file: {} was missing, so was filled in with zero.'.format(item))

            if len(np.atleast_1d(a_file['zseps'])) == 1:
                a_file['zseps'] = np.array([a_file['zseps'], 0.0])  # Z of x point in cm
                printw2(' A-file: ZSEPS had 1 element, so 0-padded to 2 elements & is now {}'.format(a_file['zseps']))

            if len(a_file['ccbrsp']) == 1 and a_file['ccbrsp'][0] == 0:
                # Computed external coil currents in Ampere; should be an array, should have len = 18 for DIII-D because
                # 18 F-coils in DIII-D.
                if a_file['nfcoil0'] < f_coil_counts.get(device, 18):
                    a_file['nfcoil0'] = f_coil_counts.get(device, 18)
                a_file['ccbrsp'] = np.zeros(a_file['nfcoil0'])
                printw2(' A-file: CCBRSP was 0, so padded out to [0] * {} since it should be an array.'.format(nfcoil0))

            if len(a_file['csilop']) == 1 and a_file['csilop'][0] == 0:
                # Computed flux loop signals in Weber. Length of array may vary.
                if a_file['nsilop0'] == 0:
                    a_file['nsilop0'] = 44  # Just guess that there might be 44 flux loops. There were at one point in
                    #                         DIII-D. I don't think it's critical to get this right because it's just
                    #                         getting zero filled at this point, anyway.
                a_file['csilop'] = np.zeros(a_file['nsilop0'])
                printw2(' A-file: CSILOP was 0, so padded out to [0] * {} since it should be an array'.format(nsilop0))

            for absl in absolute:
                a_file[absl] = abs(a_file[absl])

            if close:
                a_file.close()

        printq('Done getting A-files from MDSplus: {shot:}, {snap:}, {times:}'.format(shot=shot, snap=snap_file, times=times))
    # PART 3: M-FILE ===================================================================================================
    if get_mfile:
        m_time = efit_info.pop('mtime')

        m_interpolations = {}
        m_take_nearest = {}
        for item in m_time_varying:
            if item in efit_info and efit_info[item] is not None and len(tolist(efit_info[item])):
                if is_string(tolist(efit_info[item])[0]) or (len(m_time) < 2):
                    # Handle strings or cases where there is only one time-slice
                    printdq(' M-file: taking nearest value for {}'.format(item))
                    m_take_nearest[item] = efit_info[item]
                else:
                    printdq(' M-file: interpolating {}'.format(item))
                    y = efit_info[item]
                    if len(y) != len(m_time):
                        y = efit_info[
                            item + '_meas'
                        ]  # There are identicaly named vars on a file and meas trees, this disambigous-izes the issue
                    m_interpolations[item] = interpolate.interp1d(m_time, y, bounds_error=False, axis=0)
            else:
                printdq(' M-file: SKIPPING {} because it is missing or is None.'.format(item))

        # Find out the dimentions
        dim_dict['dim_magpri'] = efit_info['expmpi'].shape[1]  # n mag probles
        dim_dict['dim_nesum'] = efit_info['eccurt'].shape[1]  # n e coils
        dim_dict['dim_nfcoil'] = efit_info['fccurt'].shape[1]  # n f coils
        dim_dict['dim_nitera'] = efit_info['cchisq'].shape[1]  # n iterations
        dim_dict['dim_npcurn'] = efit_info['xrsp'].shape[1]  # ??
        dim_dict['dim_nsilop'] = efit_info['silopt'].shape[1]  # n flux loops
        dim_dict['dim_nstark'] = efit_info['a1gam'].shape[1]  # n max MSE views EFIT can accomodate
        try:
            dim_dict['dim_npress'] = efit_info['pressr'].shape[1]  # n pressure constraints
        except IndexError:  # if there is no kinetic constraint, pressr will be 1D (dim_time only), and shape[1] will fail
            # a1gam don't have this issue, it will always be a 2D array even with no MSE
            dim_dict['dim_npress'] = 1

        # Set up a collection to contain output
        out = output.setdefault('mEQDSK', {})

        for t in times:
            # Figure out name and time window things
            m_file_name = 'm' + format(shot, "06d") + "." + format(int(t), "05d")
            if t - int(t) >= 1e-3:
                # Handle sub-ms timing to adding _000 to the filename
                m_file_name += '_{:03d}'.format(int(t - int(t) * 1000))
            if min(abs(t - m_time)) > time_diff_warning_threshold:
                closest_efit = m_time[closestIndex(m_time, t)]
                if fail_if_out_of_range:
                    note = 'FAIL'
                else:
                    note = 'WARNING'
                printw(
                    '{:}: requested time {:} ms is more than {:} ms away from closest time ({:} ms) in source EFIT!'.format(
                        note, t, time_diff_warning_threshold, closest_efit
                    )
                )
                if fail_if_out_of_range:
                    printe('Skipped {:} because time difference was too large.'.format(m_file_name))
                    continue
            out[t] = m_file = OMFITmeqdsk(m_file_name)
            printdq('Initial keys in meqdsk: {}'.format(list(m_file.keys())))

            # Save dimensions
            m_file['__dimensions__'] = dim_dict

            printq('  Loading {:}:'.format(m_file_name), end='')
            printq('CASE', end='')
            # Now stuff m file vars in.
            warn_mes = ''
            for item in m_time_varying:

                if item == 'mtime':
                    continue  # mtime is special, not a real var in m-files

                if item in m_interpolations:
                    printq(',' + item, end='')
                    x = m_interpolations[item](t)
                elif item in m_take_nearest:
                    printq(',' + item, end='')
                    x = m_take_nearest[item][closestIndex(a_time, t)]
                else:
                    # Var was not uploaded to MDS+, implying it was arrays of 0
                    warn_mes += ' M-file: {} was missing, so was filled in with zero.\n'.format(item)
                    # Don't want to interrupt the printq strings
                    x = np.array([0])
                x = np.atleast_1d(x)

                # check dimensions
                dim_name = m_dim_names[item]
                if dim_name is not None:
                    dim = dim_dict[dim_name]
                    if len(x) < dim:
                        # pad out with 0
                        x = np.pad(x, (0, dim - len(x)))
                    elif len(x) > dim:
                        printw(f"WARNING: {item} as stored on MDS+ is too large an array. It will be trimmed down!")
                        # This should never happen unless the uploader hit a bug!
                        x = x[0:dim]
                else:
                    # if dim_name is None -> there is no secondary dimention, only dimension is time
                    # x needs to be an array of one element then

                    x = np.atleast_1d(x)
                    if len(x) > 1:
                        printw(f"WARNING: {item} as stored on MDS+ is too large an array. It will be trimmed down!")
                        x = x[0]
                    elif len(x) < 0:  # empty array is also not allowed
                        x[0] = 0.0

                # Make sure it is in float32, that what m files like their vars as.
                x = x.astype(np.float32)  # shot is the only exception
                m_file.pack_it(x, item, m_longnames[item], dim1=dim_name, is_tmp=False)  # Yes, dim1=None is ok

                # ----
                # End of variable packing loop

            # 'Pack' special vars in the m file
            from omfit_classes.omfit_nc import OMFITncData

            m_file['shot'] = OMFITncData()
            m_file['shot']['data'] = np.array([shot]).astype(np.int32)
            m_file['shot']['long_name'] = 'shot number'
            m_file['shot']['__dimensions__'] = ('dim_scalar',)
            m_file['shot']['__dtype__'] = np.dtype(np.int32)

            m_file['time'] = OMFITncData()
            m_file['time']['data'] = np.array([t]).astype(np.float32)
            m_file['time']['units'] = 'msec'  # yes, this the only var in the mfile with a unit
            m_file['time']['__dimensions__'] = ('dim_time',)
            m_file['time']['__dtype__'] = np.dtype(np.float32)

            printw2(warn_mes)

            # save and maybe close
            m_file.save()
            if close:
                m_file.close()
        printq('Done getting M-files from MDSplus: {shot:}, {snap:}, {times:}'.format(shot=shot, snap=snap_file, times=times))

    printq('Done gathering EFIT from MDSplus.')

    return output
# fmt: on


class OMFIT_pcs_shape(OMFITascii, SortedDict):
    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self, **kw)
        self.load()
        self['boundary'] = fluxSurface.BoundaryShape(rbbbs=self['Rbdry'], zbbbs=self['Zbdry'])

    def load(self):
        with open(self.filename) as f:
            lines = f.readlines()
        bdry = False
        R = []
        Z = []
        for l in lines:
            if ':' in l:
                k, v = l.split(':', 2)
                v = v.strip()
                try:
                    v = float(v)
                except Exception:
                    pass
                self[k.strip()] = v
                continue
            if 'Xpoint 2' in self and l.strip() == '':
                bdry = True
                continue
            if bdry:
                if 'R' in l and 'Z' in l:
                    continue
                i, r, z = list(map(float, l.split()[0:3]))
                R.append(r)
                Z.append(z)
                continue
            if l.strip() == '':
                continue
            print(l, 'not parsed')
        self['Rbdry'] = np.array(R)
        self['Zbdry'] = np.array(Z)


############################################
if '__main__' == __name__:
    test_classes_main_header()
    tmp = OMFITgeqdsk(OMFITsrc + '/../samples/g128913.01500')
