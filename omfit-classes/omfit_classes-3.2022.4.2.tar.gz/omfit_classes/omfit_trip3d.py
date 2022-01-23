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
from omfit_classes.omfit_matrix import OMFITmatrix
from omfit_classes.omfit_eqdsk import OMFITgeqdsk

from traceback import extract_stack
from warnings import filterwarnings
import numpy as np
import xarray as xr
import pandas as pd

__all__ = ['OMFITtrip3Dcoil', 'OMFITtrip3Dlines', 'OMFITtrip3Dhits', 'OMFITtrip3Dstart', 'OMFITtrip3Dprobeg']


def foot_on_line(xp, yp, x1, x2, y1, y2):
    r"""
    Given a point (P) and a segment (1), (2), compute the foot (F) on the line and the point-to-line distance d.

             (P) \                  (P) \
              :  |                   :  |
              :  | d                 :  | d
              :  |                   :  |
              :  /                   :  /
        (1)==(F)===========(2)      (F)------(1)=======(2)

    An array of points P is allowed, but there can only be one line segment.

    :param xp: numeric
        X-coordinate of point P or array of X-coordinates of several points

    :param yp: numeric
        Y-coordinate of point P or array of Y-coordinates of several points (must be scalar or match the shape of xp)

    :param x1: float
        X-coordinate of one end of the line segment (point 1)

    :param x2: float
        X-coordinate of the other end of the line segment (point 2)

    :param y1: float
        Y-coordinate of one end of the line segment (point 1)

    :param y2: float
        Y-coordinate of the other end of the line segment (point 2)

    :return: tuple
        X-coordinate(s) of the foot point as a float or array (matching the shape of xp or yp)
        Y-coordinate(s) of the foot point as a float or array (matching the shape of xp or yp)
        Distance between the point(s) P and the line as a float or array (matching the shape of xp or yp)
    """

    if x1 == x2 and y1 == y2:
        raise ValueError('(x1,y1) == (x2,y2)')

    elif x1 == x2:  # vertical

        xf = x1 * xp ** 0
        yf = yp * xp ** 0

    elif y1 == y2:  # horizontal

        xf = xp * xp ** 0
        yf = y1 * xp ** 0

    else:  # diagonal

        # (1) and (2)
        mm = (y2 - y1) / (x2 - x1)
        qq = y1 - mm * x1

        # (p) and (f)
        nn = -1.0 / mm
        pp = yp - nn * xp

        # foot
        xf = (pp - qq) / (mm - nn)
        yf = nn * (xf - xp) + yp

    # distance
    dd = np.hypot(xf - xp, yf - yp)

    return xf, yf, dd


def sshape(d):
    return 'x'.join([str(s) for s in np.shape(d)])


# Created by wuwen at 2015/01/22 15:50
class OMFITtrip3Dcoil(SortedDict, OMFITascii):
    def __init__(self, filename, **kw):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    def __tree_repr__(self):

        myrepr = 'FILE: %s   (%s' % (os.path.split(self.filename)[1], sizeof_fmt(self.filename, ' '))
        if not self.dynaLoad:
            myrepr += ', {} loops'.format(len(self) - 2)
        myrepr += ')'
        return myrepr, []

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        self['device'] = lines[0].strip()
        self['coil'] = lines[1].strip()

        nloops = int(lines[2].split()[0])

        k = 3
        for l in range(nloops):
            nitems = int(lines[k].split()[0])
            titem = lines[k].split()[1]
            k += 1
            loop = SortedDict()
            for s in range(nitems):
                loop[s] = [float(i) for i in lines[k].split()]
                k += 1
            self[l, titem] = loop

    @dynaSave
    def save(self):
        with open(self.filename, 'w') as f:
            f.write(self['device'].strip() + '\n')
            f.write(self['coil'].strip() + '\n')
            f.write('%3d   loops\n' % (len(self) - 2))
            for k in list(self.keys())[2:]:
                f.write('%3d   %s\n' % (len(self[k]), k[1]))
                for c in list(self[k].keys()):
                    f.write(('  % f' * len(self[k][c]) + '\n') % tuple(self[k][c]))


# Created by Trevisan at 05 Dec 2016  15:49
class OMFITtrip3Dlines(OMFITmatrix):

    """
    The OMFITtrip3Dlines class parses and handles the TRIP3D 'lines.out' output file.
    A self-described xarray object is stored under self['data'].
    """

    # file descriptors
    columns = {
        2: ['psimin', 'psimax'],
        # 8: ['phi','rho','ith','the','bmag','brot','psin','mlen'],
        9: ['phi', 'rho', 'ith', 'the', 'brho', 'bthe', 'bphi', 'mlen', 'psin'],
    }
    for c in [9]:
        columns[c + 2] = list(columns[c])
        columns[c + 2].extend(['rr', 'zz'])
        columns[c + 4] = list(columns[c + 2])
        columns[c + 4].extend(['psimin', 'psimax'])

    def __getitem__(self, key):

        try:
            return SortedDict.__getitem__(self, key)
        except Exception:
            if key == 'data':
                raise
        try:
            return self['data'].loc[:, :, key].values
        except Exception:
            return self['data'].attrs[key]

    def __mul__(self, other, quiet=False):

        # sanity checks
        if not isinstance(other, self.__class__):
            raise TypeError('class mismatch: {} vs {}.'.format(other.__class__.__name__, self.__class__.__name__))
        if self['data'].shape[0] != other['data'].shape[0]:
            raise ValueError(
                'shape mismatch: {} vs {} (full dims: {}, {}).'.format(
                    self['data'].shape[0], other['data'].shape[0], self['data'].shape, other['data'].shape
                )
            )

        # psiN arrays
        self['data'].loc[:, :, 'psimin'] = (self['psin'].transpose() ** 0 * np.nanmin(other['data'][:, 0, :], axis=-1)).transpose()
        self['data'].loc[:, :, 'psimax'] = (self['psin'].transpose() ** 0 * np.nanmax(other['data'][:, 0, :], axis=-1)).transpose()

        if not quiet:
            _print(self, 'updated psimin and psimax.')

        return self

    @dynaLoad
    def load(self, bin=None, zip=None, geqdsk=None, verbose=False, quiet=False):

        p = False
        t = tstart = time.time()

        # read file
        bin, zip = OMFITmatrix.load(
            self, bin=bin, zip=zip, header=None, comment='%', delim_whitespace=True, index_col=False, na_filter=False, engine='c'
        )

        if not quiet and verbose:
            p = _print(self, '%.2f s, %s, read from file.' % (time.time() - tstart, sshape(self.get('data', None))), p=p)

        if not bin:

            # reshape to 3D
            tstart = time.time()
            self.to3d()
            if not quiet and verbose:
                p = _print(self, '%.2f s, %s, reshaped to 3D.' % (time.time() - tstart, sshape(self.get('data', None))), p=p)

            if np.shape(self['data'])[-1] in [8, 9]:

                # add attributes
                tstart = time.time()
                stat = self.addattrs(geqdsk=geqdsk)
                if not quiet and verbose:
                    if stat is None:
                        p = _print(self, '%.2f s, did not read gEQDSK data.' % (time.time() - tstart), tag='w', p=p)
                    else:
                        p = _print(self, '%.2f s, read gEQDSK data.' % (time.time() - tstart), p=p)

                # add columns
                tstart = time.time()
                self.addcols()
                if not quiet and verbose:
                    p = _print(self, '%.2f s, %s, added columns.' % (time.time() - tstart, sshape(self['data'])), p=p)

        # summary
        if not quiet:
            if zip:
                z = 'zlibbed' if bin else 'gzipped'
            else:
                z = 'plain'
            p = _print(
                self, '%.2f s, %s, loaded %s %s.' % (time.time() - t, sizeof_fmt(self.filename, ' '), z, 'NetCDF' if bin else 'ASCII'), p=p
            )

    def to3d(self):

        old = self['data'].values
        s = np.shape(old)
        if s[-1] == 2:
            lidx = np.array(list(range(s[0]))).astype(int)
            llen = lidx ** 0
        elif s[-1] in [8, 9]:
            lidx = np.where(old[:, -2] == 0)[0].astype(int)
            llen = np.diff(np.append(lidx, s[-2])).astype(int)
        else:
            raise ValueError('unexpected shape: ' + str(s))

        new = np.nan * np.zeros((np.size(lidx), np.max(np.append(llen, 1)), s[-1]))
        for idx, (at, len) in enumerate(zip(lidx, llen)):
            new[idx, :len, :] = old[at : at + len, :]

        self.toxr(new)

    def addattrs(self, geqdsk=None):

        if geqdsk is None:
            try:
                geqdsk = eval(treeLocation(self)[-3])['INPUTS']['gEQDSK']
            except Exception:
                pass
        try:
            rmax = geqdsk['RMAXIS']
            zmax = geqdsk['ZMAXIS']
            rlim = geqdsk['RLIM']
            zlim = geqdsk['ZLIM']
            stat = True
        except Exception:
            rmax = np.nan
            zmax = np.nan
            rlim = np.nan
            zlim = np.nan
            stat = None
        finally:
            self['data'].attrs['rmax'] = rmax
            self['data'].attrs['zmax'] = zmax
            self['data'].attrs['rlim'] = rlim
            self['data'].attrs['zlim'] = zlim
            return stat

    def addcols(self):

        filterwarnings('ignore', r'All-NaN (slice|axis) encountered')

        old = self['data'].values
        s = np.shape(old)
        try:
            rmax = self['rmax']
            zmax = self['zmax']
            if np.isnan(rmax) or np.isnan(zmax):
                raise ValueError
        except Exception:
            rmax = zmax = 0.0

        new = np.nan * np.zeros((s[0], s[1], s[2] + 4))

        new[:, :, :-4] = old[:, :, :]
        new[:, :, s[2] + 0] = rmax + self['rho'] * np.cos(np.deg2rad(self['the']))
        new[:, :, s[2] + 1] = zmax + self['rho'] * np.sin(np.deg2rad(self['the']))
        new[:, :, s[2] + 2] = (self['psin'].transpose() ** 0 * np.nanmin(self['psin'], axis=-1)).transpose()
        new[:, :, s[2] + 3] = (self['psin'].transpose() ** 0 * np.nanmax(self['psin'], axis=-1)).transpose()

        self.toxr(new)

    def toxr(self, data, attrs=None):

        s = np.shape(data)
        l = list(range(s[0]))
        p = list(range(s[1]))
        c = self.columns[s[2]]
        if attrs is None:
            attrs = self['data'].attrs

        self['data'] = xr.DataArray(data, name='lines', dims=['L', 'P', 'C'], coords=[l, p, c], attrs=attrs)

    @dynaSave
    def save(self, zip=True, quiet=False):

        t = time.time()

        bin, zip = OMFITmatrix.save(self, bin=True, zip=zip)

        if not quiet:
            if zip:
                z = 'zlibbed' if bin else 'gzipped'
            else:
                z = 'plain'
            _print(self, '%.2f s, %s, saved %s %s.' % (time.time() - t, sizeof_fmt(self.filename, ' '), z, 'NetCDF' if bin else 'ASCII'))

    def prep(self, type, prefix=True, quiet=False):

        # disable method for non-line instances
        if np.shape(self['data'])[-1] == 2:
            return

        # prep type
        if type not in ['poincare', 'contour', 'control']:
            raise TypeError('unexpected value for prep type')

        # load before starting the stopwatch
        if self.dynaLoad:
            self.load(prefix=prefix, quiet=quiet)

        # stopwatch and summary
        tstart = time.time()

        # check data
        if '__%s__' % type in self:
            return

        # prepare data
        data = self['data']
        if type == 'poincare':

            la = r"poloidal angle, $\vartheta$ [deg]"
            aa = self['the'].copy()
            numsi, numsj = np.where(np.isnan(aa) == False)
            high = np.where(aa[numsi, numsj] > 180)[0]
            aa[numsi[high], numsj[high]] -= 360
            lb = r"normalized poloidal flux, $\Psi_N$"
            bb = self['psin'].copy()

        elif type == 'contour':

            la = r"$R - R_{ax}$ [m]"
            aa = self['rr'].copy()
            lb = r"$Z - Z_{ax}$ [m]"
            bb = self['zz'].copy()

        elif type == 'control':

            la = r"normalized toroidal angle, $\phi \% 360$ [deg]"
            aa = self['phi'] % 360
            lb = r"toroidal angle, $\phi$ [deg]"
            bb = self['phi'].copy()

        # initial psin
        lc = r"initial $\Psi_N$"
        cc = np.transpose(np.transpose(self['psin']) ** 0 * self['psin'][:, 0])

        # minimum psin
        ld = r"min $\Psi_N$"
        dd = self['psimin'].copy()

        # store data
        self['__%s__' % type] = np.transpose([np.transpose(aa), np.transpose(bb)])
        self['__colors__'] = np.transpose([np.transpose(cc), np.transpose(dd)])
        labels = self.setdefault('__labels__', {})
        labels[type] = [la, lb]
        labels['colors'] = [lc, ld]

        # stopwatch and summary
        if not quiet:
            _print(self, '%s: prepared data in %.3f s.' % (type.ljust(8), time.time() - tstart), prefix=prefix)

    def doplot(
        self,
        type,
        geqdsk=None,
        lines=(None, None, None),
        points=(None, None, None),
        limx=(None, None),
        limy=(None, None),
        col='min',
        cbar=True,
        prefix=True,
        quiet=False,
        **kw,
    ):

        # disable method for non-line instances
        if np.shape(self['data'])[-1] == 2:
            return

        # printed
        p = False

        # plot type
        if type not in ['poincare', 'contour', 'control']:
            raise TypeError('unexpected value for plot type: %s' % type)

        # color type
        if col not in ['min', 'ini']:
            raise TypeError('unexpected value for color: %s' % col)

        # prepare data
        self.prep(type=type, prefix=prefix, quiet=quiet)

        # retrieve data
        aa = self['__%s__' % type][:, :, 0]
        bb = self['__%s__' % type][:, :, 1]
        [la, lb] = self['__labels__'][type][:2]
        if col == 'ini':
            c = 0
        elif col == 'min':
            c = 1
        cc = self['__colors__'][:, :, c]
        lc = self['__labels__']['colors'][c]

        # stopwatch and summary
        tstart = time.time()

        # line slicing
        if isinstance(lines, tuple):
            lsli = slice(*lines)
            if not quiet and lines != (None, None, None):
                p = _print(self, '%s: slicing lines  as %s.' % (type.ljust(8), repr(lines)), prefix=prefix, p=p)
        elif isinstance(lines, list) and np.size(lines):
            lsli = lines
            if not quiet:
                p = _print(self, '%s: selecting %d lines.' % (type.ljust(8), np.size(lines)), prefix=prefix, p=p)
        else:
            raise TypeError('unexpected value for lines')

        # point slicing
        if isinstance(points, tuple):
            psli = slice(*points)
            if not quiet and points != (None, None, None):
                p = _print(self, '%s: slicing points as %s.' % (type.ljust(8), repr(points)), prefix=prefix, p=p)
        elif isinstance(points, list) and np.size(points):
            psli = points
            if not quiet:
                p = _print(self, '%s: selecting %d points.' % (type.ljust(8), np.size(points)), prefix=prefix, p=p)
        else:
            raise TypeError('unexpected value for points')

        # default boundaries
        kw.setdefault('vmin', np.nanmin(cc[lsli, psli].reshape(-1)))
        kw.setdefault('vmax', np.nanmax(cc[lsli, psli].reshape(-1)))

        # default colormap
        if 'cmap' not in kw:

            intmid = int(1e4)
            inthig = int(intmid * kw['vmin'])
            intlow = int(intmid * kw['vmax'])

            higbar = intmid > inthig
            lowbar = intlow > intmid
            if higbar:
                hi = pyplot.cm.autumn(np.linspace(0, 1, intmid - inthig))
            if lowbar:
                lo = pyplot.cm.winter_r(np.linspace(0, 1, intlow - intmid))
            if higbar and lowbar:
                mi = int((intlow - inthig) // 100) * [[0, 0, 0, 1]]
                bar = np.vstack((hi, mi, lo))
            else:
                bar = hi if higbar else lo

            kw['cmap'] = matplotlib.colors.LinearSegmentedColormap.from_list('cmapall', bar)
            kw['vmin'] = 1.0 * inthig / intmid
            kw['vmax'] = 1.0 * intlow / intmid

        # contour plot
        refa = 0
        refb = 0
        if type == 'contour':

            pyplot.gca().set_aspect('equal')

            # try to locate the gEQDSK in INPUTS
            if geqdsk is None:
                try:
                    geqdsk = eval(treeLocation(self)[-3])['INPUTS']['gEQDSK']
                    if not isinstance(geqdsk, OMFITgeqdsk):
                        raise TypeError
                except Exception:
                    geqdsk = None
            try:
                refa = self['rmax']
                refb = self['zmax']
                la = r'$R$ [m]'
                lb = r'$Z$ [m]'
                pyplot.plot(self['rlim'], self['zlim'], 'k-')
            except Exception:
                if not quiet:
                    p = _print(self, '%s: R/ZLIM will not be plotted.' % type.ljust(8), tag='w', prefix=prefix, p=p)

            pyplot.plot(refa, refb, 'k+')

        # plot
        kw.setdefault('s', 1)
        kw.setdefault('edgecolor', '')
        kw.setdefault('rasterized', True)
        scatter(aa[lsli, psli], bb[lsli, psli], c=cc[lsli, psli], **kw)

        # set limits
        if limx != (None, None):
            pyplot.xlim(limx)
        elif type == 'poincare':
            pyplot.xlim(-180, 180)
        if limy != (None, None):
            pyplot.ylim(limy)

        # set labels
        pyplot.xlabel(la)
        pyplot.ylabel(lb)

        if cbar:
            cb = colorbar()
            cb.ax.set_title(lc)
            if kw['vmin'] < 1.0 and 1.0 < kw['vmax']:
                try:
                    ticks = np.around(np.linspace(kw['vmin'], kw['vmax'], 7), decimals=3)
                    (tisep,) = np.where(abs(ticks - 1) == min(abs(ticks - 1)))
                    ticks += 1 - ticks[tisep]
                    cb.set_ticks(ticks)
                except Exception:
                    if not quiet:
                        p = _print(self, '%s: could not set colorbar ticks.' % type.ljust(8), tag='w', prefix=prefix, p=p)

        # stopwatch and summary
        tstop = time.time()
        num = np.size(aa[lsli, psli]) - np.sum(np.isnan(aa[lsli, psli]))
        if not quiet:
            p = _print(self, '{}: plotted {:,d} points in {:.3f} s.'.format(type.ljust(8), num, tstop - tstart), prefix=prefix, p=p)

    def plot(self, type='summary', **kw):

        # disable method for non-line instances
        if np.shape(self['data'])[-1] == 2:
            return

        # prefix
        me = self.__class__.__name__ + '.plot'
        blankme = ' ' * len(me)

        # quiet keyword
        quiet = kw.setdefault('quiet', False)

        # plot type
        if type in ['poincare', 'contour', 'control']:

            self.doplot(type=type, **kw)
            return

        elif type != 'summary':

            raise TypeError('unexpected value for plot type: %s' % type)

        # prepare data
        p = False
        for t in ['poincare', 'contour', 'control']:
            if '__%s__' % t in self:
                continue
            self.prep(type=t, prefix=blankme if p else True, quiet=quiet)
            p = True

        # default slicing
        p = False
        if 'lines' not in kw and 'points' not in kw:

            # line slicing: toroidal planes
            kw['lines'] = (None, None, None)
            (planes,) = np.where(self['data'][:, 0, 0] > self['data'][0, 0, 0])
            if len(planes):
                stop = planes[0]
                kw['lines'] = (None, stop, None)
                if not quiet:
                    p = _print(
                        self,
                        '%s: detected %d starting planes with step of %.1f deg.'
                        % (type.ljust(8), np.shape(self['data'])[0] / stop, self['data'][stop, 0, 0]),
                        p=p,
                    )
            else:
                if not quiet:
                    p = _print(self, '%s: detected 1 starting plane at %.1f deg.' % (type.ljust(8), self['data'][0, 0, 0]), p=p)

            # point slicing: poincare planes
            kw['points'] = (None, None, None)
            step = 0
            for idx in [0, int(np.shape(self['data'])[1] // 2)]:
                try:
                    diff = abs(self['data'][0, idx + 1, 0] - self['data'][0, idx, 0])
                    step = int(round(360.0 / diff))
                    break
                except Exception:
                    pass
            if step == 0:
                if not quiet:
                    p = _print(self, '%s: could not detect toroidal step.' % type.ljust(8), tag='w', p=p)
            elif step == 1:
                if not quiet:
                    p = _print(self, '%s: detected 1 poincare plane at %.1f deg.' % (type.ljust(8), self['data'][0, idx, 0]), p=p)
            else:
                kw['points'] = (None, None, step)
                if not quiet:
                    p = _print(self, '%s: detected %d poincare planes with step of %.1f deg.' % (type.ljust(8), step, round(diff)), p=p)

        else:

            kw.setdefault('points', (None, None, None))
            kw.setdefault('lines', (None, None, None))
            if not quiet:
                p = _print(self, '%s: overriding default slicing.' % type.ljust(8), p=p)

        # colormaps
        gg = matplotlib.colors.LinearSegmentedColormap.from_list('g', 2 * [[0.7, 0.7, 0.7, 1]])
        kk = matplotlib.colors.LinearSegmentedColormap.from_list('k', 2 * [[0, 0, 0, 1]])

        # composite plot
        ioff()
        suptitle(treeLocation(self)[-1])

        # control plots
        pyplot.subplot(2, 2, 1)
        if 'points' in kw and kw['points'] != (None, None, None):

            kwa = kw.copy()
            kwa['points'] = (None, None, None)
            kwa['cmap'] = gg
            kwa.pop('quiet')
            kwa['cbar'] = False

            # downsample lines for performance
            if isinstance(kw['lines'], tuple):
                lsli = slice(*kw['lines'])
            elif isinstance(kw['lines'], list) and np.size(kw['lines']):
                lsli = kw['lines']
            lidx = list(range(np.shape(self['data'])[0]))[lsli]
            got = np.count_nonzero(~np.isnan(self['data'][lidx, :, 0]))
            want = 123456
            if got > want:
                step = got / want + int(got % want > 0)
                kwa['lines'] = lidx[::step]
                if not quiet:
                    p = _print(self, '{:s}: downsampled control for performance.'.format(type.ljust(8)), p=p)

            self.doplot(type='control', quiet=True, **kwa)

        kwb = kw.copy()
        kwb['s'] = 6
        kwb['cmap'] = kk
        kwb['cbar'] = False
        self.doplot(type='control', prefix=blankme, **kwb)

        # poincare plot
        pyplot.subplot(2, 2, 3)
        kwc = kw.copy()
        kwc['cbar'] = False
        self.doplot(type='poincare', prefix=blankme, **kwc)

        # contour plot
        pyplot.subplot(1, 2, 2)
        self.doplot(type='contour', prefix=blankme, **kw)

        # interactive plotting
        ion()
        draw()
        show()


# Created by Trevisan at 11 Aug 2017  16:03
class OMFITtrip3Dhits(OMFITmatrix):

    """
    The OMFITtrip3Dhits class parses and handles the TRIP3D 'hit.out' output file.
    A self-described xarray object is stored under self['data'].
    """

    def __getitem__(self, key):

        try:
            return SortedDict.__getitem__(self, key)
        except Exception:
            if key == 'data':
                raise
        try:
            return self['data'].loc[:, :, key].values
        except Exception:
            return self['data'].attrs[key]

    @dynaLoad
    def __invert__(self):

        s = copy.deepcopy(self)
        s['data'].attrs = self['data'].attrs.copy()
        for att in 'abc':
            s['data'].attrs.pop(att, None)
        s['data'].loc[:, 0, :] = self['data'].loc[:, 2, :].copy()
        s['data'].loc[:, 2, :] = self['data'].loc[:, 0, :].copy()
        s['data'].loc[:, :, 'mlen'] = self['data'].loc[:, :, 'mlen'].copy()
        s['data'][:, 1, :].data *= np.nan
        s.filename = s.link = OMFITascii('hit.inv').filename
        if self.readOnly:
            s.readOnly = False
            s.save()
            s.readOnly = True
        return s

    @dynaLoad
    def load(self, bin=None, zip=None, inverse=True, geqdsk=None, verbose=False, quiet=False):

        p = False
        t = tstart = time.time()

        # read file
        bin, zip = OMFITmatrix.load(self, bin=bin, zip=zip)

        if not quiet and verbose:
            p = _print(self, '%.2f s, %s, read from file.' % (time.time() - tstart, sshape(self['data'])), p=p)

        if not bin:

            # reshape to 3D
            tstart = time.time()
            self.to3d()
            if not quiet and verbose:
                p = _print(self, '%.2f s, %s, reshaped to 3D.' % (time.time() - tstart, sshape(self['data'])), p=p)

            # add attributes
            tstart = time.time()
            stat = self.addattrs(inverse=inverse, geqdsk=geqdsk)
            if not quiet and verbose:
                if stat is None:
                    p = _print(self, '%.2f s, did not read gEQDSK data.' % (time.time() - tstart), tag='w', p=p)
                else:
                    p = _print(self, '%.2f s, read %s gEQDSK data.' % (time.time() - tstart, 'inverted' if stat else 'normal'), p=p)

            # add columns
            tstart = time.time()
            self.addcols()
            if not quiet and verbose:
                p = _print(self, '%.2f s, %s, added columns.' % (time.time() - tstart, sshape(self['data'])), p=p)

        # summary
        if not quiet:
            if zip:
                z = 'zlibbed' if bin else 'gzipped'
            else:
                z = 'plain'
            p = _print(
                self, '%.2f s, %s, loaded %s %s.' % (time.time() - t, sizeof_fmt(self.filename, ' '), z, 'NetCDF' if bin else 'ASCII'), p=p
            )

    def to3d(self):

        old = self['data'].values
        s = np.shape(old)
        idx = old[:, 0].astype(int)
        cols = int((s[-1] - 1) // 3)

        new = np.nan * np.zeros((s[0], 3, cols))
        for p in range(3):
            new[:, p, :cols] = old[:, 1 + p * cols : 1 + (p + 1) * cols]

        self.toxr(new, attrs={'index': idx})

    def addattrs(self, inverse=True, geqdsk=None):

        if geqdsk is None:
            try:
                geqdsk = eval(treeLocation(self)[-3])['INPUTS']['gEQDSK']
            except Exception:
                pass
        try:
            rmax = geqdsk['RMAXIS']
            zmax = geqdsk['ZMAXIS']
            rlim = geqdsk['RLIM'][-1 if inverse else None :: -1 if inverse else None]
            zlim = geqdsk['ZLIM'][-1 if inverse else None :: -1 if inverse else None]
            slim = np.insert(np.cumsum(np.hypot(np.diff(rlim[:]), np.diff(zlim[:]))), 0, 0)
            stat = inverse
        except Exception:
            rmax = np.nan
            zmax = np.nan
            rlim = np.nan
            zlim = np.nan
            slim = np.nan
            stat = None
        finally:
            self['data'].attrs['rmax'] = rmax
            self['data'].attrs['zmax'] = zmax
            self['data'].attrs['rlim'] = rlim
            self['data'].attrs['zlim'] = zlim
            self['data'].attrs['slim'] = slim
            return stat

    def addcols(self):

        filterwarnings('ignore', r'All-NaN (slice|axis) encountered')

        old = self['data'].values
        s = np.shape(old)
        try:
            rmax = self['rmax']
            zmax = self['zmax']
            if np.isnan(rmax) or np.isnan(zmax):
                raise ValueError
        except Exception:
            rmax = zmax = 0.0

        new = np.nan * np.zeros((s[0], s[1], s[2] + 2))

        new[:, :, :-2] = old[:, :, :]
        new[:, :, s[2] + 0] = rmax + self['rho'] * np.cos(np.deg2rad(self['the']))
        new[:, :, s[2] + 1] = zmax + self['rho'] * np.sin(np.deg2rad(self['the']))

        self.toxr(new)

    def toxr(self, data, attrs=None):

        s = np.shape(data)
        l = list(range(s[0]))
        p = list(range(s[1]))
        c = OMFITtrip3Dlines.columns[s[2]]
        if attrs is None:
            attrs = self['data'].attrs

        self['data'] = xr.DataArray(data, name='hits', dims=['L', 'P', 'C'], coords=[l, p, c], attrs=attrs)

    @dynaSave
    def save(self, zip=False, quiet=False):

        t = time.time()

        bin, zip = OMFITmatrix.save(self, bin=True, zip=zip)

        if not quiet:
            if zip:
                z = 'zlibbed' if bin else 'gzipped'
            else:
                z = 'plain'
            _print(self, '%.2f s, %s, saved %s %s.' % (time.time() - t, sizeof_fmt(self.filename, ' '), z, 'NetCDF' if bin else 'ASCII'))

    def prep(self, project=False, force=False, save=None, prefix=True, quiet=False):

        if not force and np.all([w in self['data'].attrs for w in 'abc']):
            return
        if self.dynaLoad:
            self.load()

        # ignore all-nan warnings
        filterwarnings('ignore', r'All-NaN (slice|axis) encountered')

        if np.all(np.isnan(self['data'][:, 1, :].data)):
            project = True

        if np.any(np.isnan([self['rmax'], self['zmax']])) or np.any(np.isnan([self['rlim'], self['zlim'], self['slim']])):
            raise ValueError('missing gEQDSK data.')

        # shortcuts
        data = self['data'].data
        rlim = self['rlim']
        zlim = self['zlim']
        ss = self['slim']
        c = {v: k for k, v in enumerate(self['data'].coords['C'].data)}

        # total number of points
        tot = np.shape(data)[0]
        myformat = '{:' + str(len('{:,d}'.format(tot))) + ',d}'
        tstart = time.time()

        # hit points
        iih = np.zeros(tot).astype('int')
        rrh = np.nan * np.zeros(tot)
        zzh = np.nan * np.zeros(tot)
        phh = np.nan * np.zeros(tot)
        mah = np.nan * np.zeros(tot)

        # detect phi step
        dphi = np.abs(np.diff(data[:, 1:, c['phi']], axis=1)).squeeze()
        dphi[np.where(dphi[:] == 0.0)] = np.nan
        dpinit = np.nanmin(dphi)
        if not quiet:
            p = _print(self, (myformat + ' total points, step is {:.2f} deg.').format(tot, dpinit), prefix=prefix)

        # index lists
        ko = []
        try1 = []
        try2 = []

        # 1st TRY: USE SECOND-TO-LAST AND LAST POINT
        for t in range(tot):

            xx = data[t, 1:, c['rr']]
            yy = data[t, 1:, c['zz']]
            ph = data[t, 1:, c['phi']]
            ma = data[t, 1:, c['mlen']]

            try:

                # this is NOT the second-to-last point
                if np.isnan(dphi[t]) or dphi[t] > dpinit * 1.5:
                    raise ValueError

                # discard kicks greater than 50 cm
                if np.hypot(np.diff(xx), np.diff(yy)) > 0.5:
                    raise ValueError

                # compute intersection
                result, index = line_intersect(np.vstack((rlim, zlim)).T, np.vstack((xx, yy)).T, return_indices=True)
                rrh[t], zzh[t] = result[0]
                iih[t] = index[0][0]

            except (ValueError, IndexError):

                # discard second-to-last point
                ko.append(t)
                continue

            # compute normalized distance
            ddh = np.hypot(rrh[t] - xx[1], zzh[t] - yy[1])
            ddh /= np.hypot(xx[0] - xx[1], yy[0] - yy[1])

            # inteporlate phi, mag
            phh[t] = ph[1] + ddh * (ph[0] - ph[1])
            mah[t] = ma[1] + ddh * (ma[0] - ma[1])

            try1.append(t)

        # 2nd TRY: USE ONLY LAST POINT
        if project and np.size(ko):

            kos = np.array(ko).astype('int')
            ko = []

            # limiter-to-last point distance
            limd = np.nan * np.zeros((len(rlim), np.size(kos), 3))

            # for each divertor segment
            for l in range(len(rlim) - 1):

                if rlim[l] == rlim[l + 1] and zlim[l] == zlim[l + 1]:
                    continue

                # distance from segment center
                xc = np.mean([rlim[l], rlim[l + 1]])
                yc = np.mean([zlim[l], zlim[l + 1]])
                rc = np.hypot(xc - rlim[l], yc - zlim[l])
                (cpu,) = np.where(np.hypot(data[kos[:], 2, c['rr']] - xc, data[kos[:], 2, c['zz']] - yc) <= rc * 1.5)
                if not np.size(cpu):
                    continue

                # compute foot (xf,yf) and distance dd
                xf, yf, dd = foot_on_line(
                    xp=data[kos[cpu], 2, c['rr']], x1=rlim[l], x2=rlim[l + 1], yp=data[kos[cpu], 2, c['zz']], y1=zlim[l], y2=zlim[l + 1]
                )
                limd[l, cpu[:], 0] = xf[:]
                limd[l, cpu[:], 1] = yf[:]
                limd[l, cpu[:], 2] = dd[:]

            # for each point
            for k in range(len(kos)):
                (result,) = np.where(limd[:, k, 2] == np.nanmin(limd[:, k, 2]))
                try:
                    iih[kos[k]] = result[0]
                    try2.append(kos[k])
                except IndexError:
                    ko.append(kos[k])

            rrh[try2] = limd[iih[try2], list(range(len(try2))), 0]
            zzh[try2] = limd[iih[try2], list(range(len(try2))), 1]
            phh[try2] = data[try2, 2, c['phi']].copy()
            mah[try2] = data[try2, 2, c['mlen']].copy()

        # s: based on hit data
        ssh = ss[iih[:]] + np.hypot(rrh[:] - rlim[iih[:]], +zzh[:] - zlim[iih[:]])

        # store data
        self['data'].attrs['a'] = phh[:] * -1 % 360
        self['data'].attrs['b'] = ssh[:]
        self['data'].attrs['c'] = mah[:]

        # summary
        if np.size(try1):
            p = _print(self, (myformat + ' intersections.').format(np.size(try1)), tag='i', prefix=prefix, p=p)
        if np.size(try2):
            p = _print(self, (myformat + ' projections.').format(np.size(try2)), tag='w', prefix=prefix, p=p)
        if np.size(ko):
            p = _print(self, (myformat + ' errors.').format(np.size(ko)), tag='e', prefix=prefix, p=p)
        p = _print(self, 'computed hit data in {:.3f} s.'.format(time.time() - tstart), prefix=prefix, p=p)

        # save data
        if save is True or (save is None and self.OMFITproperties['bin'] is True):
            ro = self.readOnly
            self.readOnly = False
            self.save()
            self.readOnly = ro

    def plot(self, mlen=100, sol=False, cbar=True, inverse=False, prefix=True, quiet=False, **kw):
        r"""
        The OMFITtrip3Dhits.plot plots the footprint based on the data prepared by OMFITtrip3Dhits.prep.

        :param mlen: if None, select all the data points,
                     if MIN, select points with MIN <= mlen,
                     if (MIN,MAX),              MIN <= mlen <= MAX.

        :param cbar: if True,  the colorbar will be plotted,
                     if False,                      hidden.

        :param inverse: if False, y-axis is normal,
                        if True,            inverted.

        :param quiet: if False, output to console is normal,
                      if True,                       suppressed.

        :param \**kw: keyword dictionary to be passed to scatter().

        :return: None
        """

        filterwarnings('ignore', r'invalid value encountered in (less|greater)_equal')

        if not np.all([w in self['data'].attrs for w in 'abc']):
            self.prep(prefix=prefix, quiet=quiet)

        cc = self['data'].attrs['c']
        if sol and np.nanmin(cc) < mlen and mlen < np.nanmax(cc):

            i = isinteractive()
            if i:
                ioff()
            gs = GridSpec(2, 16)
            gs.update(wspace=1, hspace=0)
            ct = pyplot.subplot(gs[0, -1])
            cb = pyplot.subplot(gs[1, -1])
            ax = pyplot.subplot(gs[:, :-1])

            vmin = kw.pop('vmin', 0)
            vmax = kw.pop('vmax', None)
            cmap = kw.pop('cmap', None)
            if cmap is None or not np.iterable(cmap):
                cmapb = 'gist_earth_r'
                cmapt = 'plasma'
            else:
                cmapb = cmap[0]
                cmapt = cmap[1]

            self.plot(mlen=mlen, sol=False, cmap=cmapt, cbar=False, vmin=mlen, vmax=vmax, inverse=inverse, prefix=prefix, quiet=quiet, **kw)
            ct.set_title('len [m]')
            colorbar(cax=ct, format='%d', ticks=pyplot.MaxNLocator(nbins=5, prune='both'))

            self.plot(
                mlen=(vmin, mlen),
                sol=False,
                cmap=cmapb,
                cbar=False,
                vmin=vmin,
                vmax=mlen,
                inverse=inverse,
                prefix=prefix,
                quiet=quiet,
                **kw,
            )
            colorbar(cax=cb, format='%d', ticks=pyplot.MaxNLocator(nbins=5))

            if i:
                ion()
                draw()
                show()
            return ax, (cb, ct)

        # shortcuts
        p = False
        aa = self['data'].attrs['a']
        bb = self['data'].attrs['b']
        cc = self['data'].attrs['c']
        ss = self['slim']
        rlim = self['rlim']
        zlim = self['zlim']

        # total number of points
        tot = np.size(self['data'][:, 0])
        myformat = '{:' + str(len('{:,d}'.format(tot))) + ',d}'
        tstart = time.time()

        # magnetic length threshold
        if mlen is None:
            select = list(range(len(cc)))
        elif np.size(mlen) == 1:
            (select,) = np.where(cc >= mlen)
        elif np.iterable(mlen) and np.size(mlen) == 2:
            ave = np.mean(mlen)
            (dif,) = np.diff(mlen) / 2.0
            (select,) = np.where(abs(cc[:] - ave) <= dif)
        else:
            raise ValueError('unsupported magnetic length format: {:s} x {:d}.'.format(mlen.__class__.__name__, np.size(mlen)))
        if not np.size(select):
            if np.size(mlen) == 1:
                if not quiet:
                    p = _print(self, 'no points with length of {:.0f} m.'.format(mlen), tag='w', prefix=prefix, p=p)
                select = list(range(len(cc)))
            else:
                if not quiet:
                    p = _print(self, 'no points with length of [{:.0f}, {:.0f}] m.'.format(*mlen), tag='e', prefix=prefix, p=p)
                return None
        if not quiet:
            p = _print(self, 'magnetic length in [{:.0f}, {:.0f}] m.'.format(nanmin(cc[select]), nanmax(cc[select])), prefix=prefix, p=p)

        # limits
        pyplot.xlim(0, 360)
        pyplot.ylim(np.nanmin(bb[select]), np.nanmax(bb[select]))

        # default keywords
        kw.setdefault('cmap', 'plasma')
        kw.setdefault('s', 1)
        kw.setdefault('edgecolor', '')
        kw.setdefault('alpha', 0.75)
        kw.setdefault('rasterized', True)

        # plot
        scatter(aa[select], bb[select], c=cc[select], **kw)
        ax = pyplot.gca()

        # axes
        if inverse:
            pyplot.gca().invert_yaxis()
        pyplot.xlabel(r'toroidal angle, $\phi$ [deg]')
        pyplot.ylabel('hit parameter, $s$ [m]')
        ticklabel_format(useOffset=False)
        if cbar:
            cb = colorbar(format='%d', ticks=pyplot.MaxNLocator(prune='upper'))
            cb.ax.set_title('len [m]')

        # summary
        if not quiet:
            p = _print(
                self, 'plotted {:,d} points in {:.3f} s.'.format(np.sum(~np.isnan(bb[select])), time.time() - tstart), prefix=prefix, p=p
            )

        return ax, [cb.ax] if cbar else []


# Created by Trevisan at 01 May 2018  15:43
class OMFITtrip3Dstart(OMFITmatrix):

    """
    The OMFITtrip3Dstart class parses and handles the TRIP3D start points input file.
    A self-described xarray object is stored under self['data'].
    """

    @dynaLoad
    def load(self):

        t = time.time()

        OMFITmatrix.load(self, bin=False, zip=False, skiprows=1, comment='!')

        if self['data'] is not None:
            self.toxr()
            _print(self, '%.2f s, %s, load from file.' % (time.time() - t, sizeof_fmt(self.filename, ' ')))

    @dynaSave
    def save(self):

        t = time.time()

        na = np.shape(self['data'])[0]
        nb = np.max([1, np.size(np.where(self['data'][:, -1] == self['data'][0, -1]))])
        nc = na / nb
        with open(self.filename, 'w') as f:
            f.write(3 * '%d ' % (na, nb, nc) + '\n')

        OMFITmatrix.save(self, bin=False, zip=False, mode='a', na_rep='nan')

        _print(self, '%.2f s, %s, saved to file.' % (time.time() - t, sizeof_fmt(self.filename, ' ')))

    def toxr(self, data=None):

        if data is None:
            try:
                data = self['data'].values
            except Exception:
                data = self['data']

        self['data'] = xr.DataArray(data, name='startfile', dims=['P', 'C'], coords=[list(range(np.shape(data)[0])), ['rad', 'the', 'phi']])

    def plot(self, radvar=None, geqdsk=None, pol=True, tor=True, lim=True, surf=True, **kw):

        if radvar is None:
            radvar = eval(treeLocation(self)[-2])['trip3d.in']['input']['iRadVar']

        if geqdsk is None:
            try:
                geqdsk = eval(treeLocation(self)[-2])['gEQDSK']
            except Exception:
                pass
        try:
            rmax = geqdsk['RMAXIS']
            zmax = geqdsk['ZMAXIS']
        except Exception:
            rmax = np.nan
            zmax = np.nan
        try:
            rlim = geqdsk['RLIM']
            zlim = geqdsk['ZLIM']
        except Exception:
            rlim = np.nan
            zlim = np.nan

        suptitle(treeLocation(self)[-1])
        kw = {'rasterized': True}

        if pol:

            if tor:
                pyplot.subplot(122)
            pyplot.title('poloidal view')

            if radvar == 1:

                # rho
                rr = rmax + self['data'].loc[:, 'rad'] * np.cos(np.deg2rad(self['data'].loc[:, 'the']))
                zz = zmax + self['data'].loc[:, 'rad'] * np.sin(np.deg2rad(self['data'].loc[:, 'the']))

                if surf and geqdsk['NBBBS']:
                    geqdsk.plot(only2D=True)
                    pyplot.gca().autoscale(tight=True)
                    kw['color'] = pyplot.gca().lines[-2].get_color()
                if lim:
                    pyplot.plot(rlim, zlim, 'k-')
                    pyplot.gca().set_aspect('equal')

                pyplot.xlabel('R [m]')
                pyplot.ylabel('Z [m')

                pyplot.plot(rr, zz, '.', **kw)

            elif radvar == 3:

                # psi normal
                pyplot.plot(self['data'].loc[:, 'the'], self['data'].loc[:, 'rad'], '.', **kw)

                pyplot.xlabel('theta [deg]')
                pyplot.ylabel('psin')

        if tor:

            if pol:
                pyplot.subplot(121)
            pyplot.title('toroidal view')

            if radvar == 1:

                # rho
                rr = rmax + self['data'].loc[:, 'rad'] * np.cos(np.deg2rad(self['data'].loc[:, 'the']))
                pyplot.plot(
                    rr * np.cos(np.deg2rad(self['data'].loc[:, 'phi'])), rr * np.sin(np.deg2rad(self['data'].loc[:, 'phi'])), '.', **kw
                )

                if lim:
                    t = np.arange(361) * np.pi / 180.0
                    rmin = np.min(rlim)
                    rmax = np.max(rlim)
                    pyplot.plot(rmin * np.cos(t), rmin * np.sin(t), 'k-')
                    pyplot.plot(rmax * np.cos(t), rmax * np.sin(t), 'k-')

                pyplot.gca().set_aspect('equal')

            elif radvar == 3:

                # psi normal
                pyplot.plot(self['data'].loc[:, 'phi'], self['data'].loc[:, 'rad'], '.', **kw)

                pyplot.xlabel('phi [deg]')
                pyplot.ylabel('psin')


# Created by Trevisan at 01 May 2018  16:20
class OMFITtrip3Dprobeg(OMFITmatrix):

    """
    The OMFITtrip3Dprobeg class parses and handles the TRIP3D 'probe_gb.out' output file.
    A self-described xarray object is stored under self['data'].
    """

    @dynaLoad
    def load(self):

        t = time.time()

        OMFITmatrix.load(self, bin=False, zip=False, comment='%')

        if self['data'] is not None:
            self.toxr()
            _print(self, '%.2f s, %s, load from file.' % (time.time() - t, sizeof_fmt(self.filename, ' ')))

    @dynaSave
    def save(self):

        t = time.time()

        with open(self.filename, 'w') as f:
            f.write('%' + ' '.join(self['data'].coords['C'].values) + '\n')

        OMFITmatrix.save(self, bin=False, zip=False, mode='a', float_format='%.11e', na_rep='nan')

        _print(self, '%.2f s, %s, saved to file.' % (time.time() - t, sizeof_fmt(self.filename, ' ')))

    def toxr(self, data=None):

        if data is None:
            try:
                data = self['data'].values
            except Exception:
                data = self['data']

        self['data'] = xr.DataArray(
            data,
            name='probeg',
            dims=['P', 'C'],
            coords=[list(range(np.shape(data)[0])), ['phi', 'rr', 'zz', 'Bphi', 'Brr', 'Bzz', 'Bpol', 'Bmag']],
        )

    def plot(self, cols=['Bpol', 'Bmag'], phi=None, geqdsk=None, stats=True, **kw):

        if geqdsk is None:
            try:
                geqdsk = eval(treeLocation(self)[-3])['INPUTS']['gEQDSK']
            except Exception:
                pass
        try:
            rlim = geqdsk['RLIM']
            zlim = geqdsk['ZLIM']
        except Exception:
            rlim = np.nan
            zlim = np.nan

        if phi is None:
            phi = self['data'].loc[0, 'phi']
        (idx,) = np.where(self['data'].loc[:, 'phi'] == phi)
        if len(idx):
            printi('{:,d} points at phi = {:.1f} deg'.format(np.size(idx), phi.values))

        suptitle(treeLocation(self)[-1])

        kw.setdefault('cmap', 'plasma')
        kw.setdefault('s', 10)
        kw.setdefault('edgecolor', '')
        kw.setdefault('rasterized', True)

        i = 0
        for c in cols:

            if np.size(cols) > 1:
                i += 1
                pyplot.subplot(1, np.size(cols), i)

            if geqdsk:
                pyplot.plot(rlim, zlim, 'k-')

            scatter(self['data'].loc[idx, 'rr'], self['data'].loc[idx, 'zz'], c=self['data'].loc[idx, c], **kw)

            pyplot.gca().set_aspect('equal')
            pyplot.gca().autoscale(tight=True)
            pyplot.title(c)
            colorbar()

            if stats:
                printi(
                    c
                    + ' min = %g %s'
                    % (np.nanmin(self['data'].loc[idx, c]), '(NaNs excluded)' if np.isnan(self['data'].loc[idx, c]).any() else '')
                )
                printi(
                    ' ' * len(c)
                    + ' max = %g %s'
                    % (np.nanmax(self['data'].loc[idx, c]), '(NaNs excluded)' if np.isnan(self['data'].loc[idx, c]).any() else '')
                )


def _print(who, message, prefix=True, tag='i', p=False):

    # short versions of tag_print's tags
    tags = {
        'o': 'STDOUT',
        'e': 'STDERR',
        'd': 'DEBUG',
        'u': 'PROGRAM_OUT',
        'r': 'PROGRAM_ERR',
        'i': 'INFO',
        't': 'HIST',
        'h': 'HELP',
        'w': 'WARNING',
    }

    if prefix:

        # set the prefix
        if prefix == True:
            name = who.__class__.__name__
            method = extract_stack()[-2][2]
            if method == 'doplot':
                method = 'plot'
            if '__' in method:
                method = method[1:5]
            pref = '%s.%s' % (name, method)
        else:
            pref = str(prefix)
        message = '%s: %s' % (pref, message)

        # printed mask
        if p:
            msgs = message.split(': ')
            message = ' ' * len(': '.join(msgs[:-1])) + ': ' + msgs[-1]

    # print the message
    tag_print(message, tag=tags[tag])

    return True
