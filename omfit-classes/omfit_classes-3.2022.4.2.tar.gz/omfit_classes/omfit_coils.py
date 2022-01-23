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
import scipy as scipy
from omfit_classes.omfit_ascii import OMFITascii

__all__ = ['OMFITcoils', 'OMFITfocuscoils', 'OMFITGPECcoils']


class OMFITcoils(SortedDict, OMFITascii):
    """
    OMFITobject used to interface with coils ascii files used in FOCUS and STELLOPT codes.

    :param filename: filename passed to OMFITascii class

    All additional key word arguments passed to OMFITascii

    """

    def __init__(self, filename, **kwargs):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kwargs)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """Load the file and parse it into a sorted dictionary"""
        with open(self.filename) as f:
            lines = f.readlines()

        # allow class to be initialized with a new (empty) file
        if len(lines) == 0:
            return

        # first three lines are global parameters
        # only the first line has meanings
        for i in range(1):
            k, v = lines[i].split()
            if v.isdigit():
                self[k] = int(v)
            else:
                self[k] = v

        self['num_coils'] = 0

        # find end of data
        nlines = len(lines)
        end_line = 3
        for i in range(-1, -nlines, -1):
            if lines[i].lstrip().lower().startswith('end'):
                end_line = nlines + i
                break

        # if no 'end' detected, use the last line
        if end_line == 3:
            end_line = nlines

        # find the start, stop of each coil
        start = 3
        check = 0
        num_coil = 0
        while start < end_line:
            # defend against runaway while loops
            check += 1
            if check > 1e6:
                raise RuntimeError("Found over 1e6 coils. That is too many!")

            # read each coil
            xyzc = []
            for i in range(start, end_line):
                xyzc.append(list(map(np.float, lines[i].split()[:4])))
                if len(lines[i].split()) != 4:  # detect new coil
                    group, name = lines[i].split()[4:6]
                    num_coil += 1
                    # assign labels for each coil, even they have the same names
                    if name not in self:
                        label = name  # default name
                    else:
                        for icoil in range(1, 10001):
                            label = '{:}_{:}'.format(name, icoil)
                            if label not in self:
                                break
                            if icoil == 10000:
                                raise OMFITexception('Only 10000 or fewer coils can have the same name.')

                    xyzc = np.array(xyzc)
                    self[label] = SortedDict()
                    self[label]['x'] = xyzc[:, 0]
                    self[label]['y'] = xyzc[:, 1]
                    self[label]['z'] = xyzc[:, 2]
                    self[label]['I'] = xyzc[0, 3]  # coil current is just a float value
                    self[label]['group'] = int(group)
                    self[label]['name'] = name
                    start = i + 1
                    break
        self['num_coils'] = num_coil  # total number of coils
        return

    @dynaSave
    def save(self):
        """Write the data in standard ascii format"""
        with open(self.filename, 'w') as f:
            # write the defining parameters
            periods = list(self.keys())[0]

            f.write('{:} {:}\n'.format(periods, self[periods]))  # the first line with periods
            f.write('{:} {:}\n'.format('begin', 'filament'))
            f.write('{:} {:}\n'.format('mirror', 'NIL'))

            # write each coil
            for key, coil in list(self.items()):
                if not isinstance(coil, dict):
                    continue
                for i in range(len(coil['x']) - 1):
                    f.write('{:23.15E}{:23.15E}{:23.15E}{:23.15E}\n'.format(coil['x'][i], coil['y'][i], coil['z'][i], coil['I']))
                i = len(coil['x']) - 1
                f.write(
                    '{:23.15E}{:23.15E}{:23.15E}{:23.15E} {:>11} {:>11}\n'.format(
                        coil['x'][i], coil['y'][i], coil['z'][i], 0.0, coil['group'], coil['name']
                    )
                )
            f.write('end\n')
        return

    @dynaLoad
    def plot(self, ax=None, nd=3, cmap='coolwarm_r', vmin=None, vmax=None, colorbar=True, **kwargs):
        r"""
        Plot the coils in 3D, colored by their current values.

        :param ax: Axes. Axis into which the plot will be made.

        :param cmap: string. A valid matplolib color map name.

        :param vmin: float. Minimum of the color scaling.

        :param vmax: float. Maximum of the color scaling.

        :param colorbar: bool. Draw a colorbar for the currents.

        :param \**kwargs: dict. All other key word arguments are passed to the mplot3d plot function.

        :return: list of Line3D objects. The line plotted for each coil.

        """
        if nd == 3:
            projection = '3d'
        else:
            projection = None
        if ax is None:
            # extra logic to handle OMFIT's auto-figure making when double-clicked in tree
            f = pyplot.gcf()
            if len(f.axes):
                # normal situation in which existing figures should be respected and left alone
                try:
                    f, ax = pyplot.subplots(subplot_kw={'aspect': 'equal', 'projection': projection})
                except NotImplementedError:  # python3 matplolib did not have this for some reason
                    pyplot.close(pyplot.gcf())  # will have opened a figure than failed to set the aspect
                    f, ax = pyplot.subplots(subplot_kw={'projection': projection})
            else:
                # OMFIT (or the gcf needed to check OMFIT) made a empty figure for us
                ax = f.add_subplot(111, projection=projection)
                try:
                    ax.set_aspect('equal')
                except NotImplementedError:
                    pass
            # aesthetics
            if nd == 3:
                ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
                ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
                ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
                ax.set_xlabel('x (m)')
                ax.set_ylabel('y (m)')
                ax.set_zlabel('z (m)')
                ax.set_axis_off()
        else:
            f = ax.get_figure()

        # defaults
        kwargs.setdefault('linewidth', 3)
        if 'lw' in kwargs:
            kwargs['linewidth'] = kwargs.pop('lw')

        keys = list(self.keys())
        curs, lines = [], []
        bound = 0
        for key, coil in list(self.items()):
            if not isinstance(coil, dict):
                continue
            curs.append(coil['I'])
            if nd == 3:
                lines.append(ax.plot(coil['x'], coil['y'], coil['z'], label=key, **kwargs)[0])
                bound = max(bound, np.max(np.abs(np.hstack((coil['x'], coil['y'], coil['z'])))))
            elif nd == 1:
                r = np.sqrt(coil['x'] ** 2 + coil['y'] ** 2)
                lines.append(ax.plot(r, coil['z'], label=key, **kwargs)[0])
                bound = max(bound, np.max(np.abs(np.hstack((r, coil['z'])))))
            else:
                raise OMFITexception("Only 3D and 1D plots are available")
        # color by current
        from omfit_classes.utils_plot import set_linearray

        sm = set_linearray(lines, values=curs, vmin=vmin, vmax=vmax, cmap=cmap)
        if colorbar:
            cb = f.colorbar(sm, ax=ax, shrink=0.8)
            cb.set_label('Current (A)')

        # force equal aspect
        if nd == 3:
            bound *= 0.6
            ax.set_xlim(-bound, bound)
            ax.set_ylim(-bound, bound)
            ax.set_zlim(-bound, bound)
            ax.auto_scale_xyz((-bound, bound), (-bound, bound), (-bound, bound))

        return lines

    @dynaLoad
    def to_OMFITfocuscoils(self, filename, nfcoil=8, target_length=0, coil_type=1, coil_symm=0, nseg=None, i_flag=1, l_flag=0):
        """
        Convert to the  OMFITfocuscoils ascii file format, which stores Fourier Harmonics
        of the coils. These files have additional settings, which can be set using key
        word arguments. Be sure to sync these with the focus input namelist!

        :param filename: str. Name of new file

        :param nfcoil: int. Number of harmonics in decomposition

        :param target_length: float. Target length of coils. Zero targets the initial length.

        :param coil_type: int.

        :param coil_symm: int. 0 for no symmetry. 1 for toroidal symmetry matching the boundary bnfp.

        :param nseg: int. Number of segments. Default (None) uses the number of segments in the original file

        :param i_flag: int.

        :param l_flag: int.

        :return: OMFITcoils

        """
        coils = SortedDict()
        ckeys = [k for k, v in self.items() if isinstance(v, dict)]
        for i, key in enumerate(ckeys):
            # decompose x,y,z
            A = []
            theta = np.linspace(0, 2 * np.pi, len(self[key]['x']))
            for t in theta:
                A.append(np.ravel([(np.cos(m * t), np.sin(m * t)) for m in range(nfcoil + 1)]))
            A = np.array(A)
            csx = scipy.linalg.lstsq(A, self[key]['x'], 1e-2)[0]
            csy = scipy.linalg.lstsq(A, self[key]['y'], 1e-2)[0]
            csz = scipy.linalg.lstsq(A, self[key]['z'], 1e-2)[0]
            length = np.sum(np.sqrt(np.diff(self[key]['x']) ** 2 + np.diff(self[key]['y']) ** 2 + np.diff(self[key]['z']) ** 2))
            # fill in info
            coils[key] = SortedDict()
            coils[key]['coil_type'] = coil_type  # todo: learn what this is
            coils[key]['coil_symm'] = coil_symm
            if nseg is None:
                coils[key]['nseg'] = len(self[key]['x']) - 1
            else:
                coils[key]['nseg'] = nseg
            coils[key]['current'] = self[key]['I']
            coils[key]['i_flag'] = i_flag
            coils[key]['length'] = length
            coils[key]['l_flag'] = l_flag
            if target_length < 0:
                coils[key]['target_length'] = length
            else:
                coils[key]['target_length'] = target_length
            coils[key]['nfcoil'] = nfcoil
            coils[key]['xc'] = csx[0::2]
            coils[key]['xs'] = csx[1::2]
            coils[key]['yc'] = csy[0::2]
            coils[key]['ys'] = csy[1::2]
            coils[key]['zc'] = csz[0::2]
            coils[key]['zs'] = csz[1::2]

        # Use the OMFIT class to create an empty file and then update it in memory
        result = OMFITfocuscoils(filename)
        result.update(coils)

        return result

    @dynaLoad
    def to_OMFITGPECcoils(self, filename):
        """
        Convert OMFITcoils to the OMFITGPECcoils ascii file format, which writes x,y,z points
        but no current information.

        :param filename: str. Name of new file

        :return: OMFITGPECcoils

        """
        # Use the OMFIT class to create an empty file and then update it in memory
        result = OMFITGPECcoils(filename)
        result.update(self)

        return result


class OMFITfocuscoils(SortedDict, OMFITascii):
    """
    OMFITobject used to interface with focus ascii files used to describe coils in native FOCUS
    decomposition.

    :param filename: filename passed to OMFITascii class

    All additional key word arguments passed to OMFITascii

    """

    def __init__(self, filename, **kwargs):
        SortedDict.__init__(self)
        OMFITascii.__init__(self, filename, **kwargs)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """Load the file and parse it into a sorted dictionary"""
        with open(self.filename) as f:
            lines = f.readlines()

        # allow class to be initialized with a new (empty) file
        if len(lines) == 0:
            return

        ncoils = int(lines[1].strip())

        for i in range(ncoils):
            start = 2 + i * 14
            ctype, csym, cname = lines[start + 2].split()
            self[cname] = SortedDict()
            self[cname]['coil_type'] = int(ctype)
            self[cname]['coil_symm'] = int(csym)
            keys = lines[start + 3].split()[1:]
            vals = lines[start + 4].split()
            self[cname]['nseg'] = int(vals[0])
            self[cname]['current'] = float(vals[1])
            self[cname]['i_flag'] = int(vals[2])
            self[cname]['length'] = float(vals[3])
            self[cname]['l_flag'] = int(vals[4])
            self[cname]['target_length'] = float(vals[5])
            self[cname]['nfcoil'] = int(lines[start + 6].strip())
            for j, key in enumerate(['xc', 'xs', 'yc', 'ys', 'zc', 'zs']):
                self[cname][key] = np.array(lines[start + 8 + j].split(), dtype=float)
        return

    @dynaSave
    def save(self):
        """Write the data in standard ascii format"""
        with open(self.filename, 'w') as f:
            # write the total number
            f.write(' # ncoils\n')
            f.write('{:12}\n'.format(len(self)))
            for i, key in enumerate(self.keys()):
                f.write(' #--------------------------------------------\n')
                f.write(' #   coil_type    coil_symm    coil_name\n')
                f.write('  {:12} {:12} {:>12}\n'.format(self[key]['coil_type'], self[key]['coil_symm'], key))
                keys = ['nseg', 'current', 'i_flag', 'length', 'l_flag', 'target_length']
                vals = [self[key][k] for k in keys]
                f.write(' # {:>6} {:>18} {:>6} {:>18} {:>6} {:>18}\n'.format(*keys))
                f.write('   {:6} {:18.9E} {:6} {:18.9E} {:6} {:18.9E}\n'.format(*vals))
                f.write(' #      nfcoil\n')
                f.write('  {:12}\n'.format(self[key]['nfcoil']))
                f.write(' # Fourier harmonics for coils ( xc; xs; yc; ys; zc; zs)\n')
                for k in ['xc', 'xs', 'yc', 'ys', 'zc', 'zs']:
                    f.write((' {:23.15E}' * len(self[key][k]) + '\n').format(*self[key][k]))
        return

    @dynaLoad
    def plot(self, bnfp=1, ax=None, cmap='coolwarm_r', vmin=None, vmax=None, colorbar=True, **kwargs):
        r"""
        Plot the coils in 3D, colored by their current values.

        :param bnfp: int. Toroidal mode number of symmetry used if coil_symm is 1

        :param ax: Axes. Axis into which the plot will be made.

        :param cmap: string. A valid matplolib color map name.

        :param vmin: float. Minimum of the color scaling.

        :param vmax: float. Maximum of the color scaling.

        :param colorbar: bool. Draw a colorbar for the currents.

        :param \**kwargs: dict. All other key word arguments are passed to the mplot3d plot function.

        :return: list of Line3D objects. The line plotted for each coil.

        """

        if ax is None:
            # extra logic to handle OMFIT's auto-figure making when double-clicked in tree
            f = pyplot.gcf()
            if len(f.axes):
                # normal situation in which existing figures should be respected and left alone
                try:
                    f, ax = pyplot.subplots(subplot_kw={'aspect': 'equal', 'projection': '3d'})
                except NotImplementedError:  # python3 matplolib did not have this for some reason
                    pyplot.close(pyplot.gcf())  # will have opened a figure than failed to set the aspect
                    f, ax = pyplot.subplots(subplot_kw={'projection': '3d'})
            else:
                # OMFIT (or the gcf needed to check OMFIT) made a empty figure for us
                ax = f.add_subplot(111, projection='3d')
                try:
                    ax.set_aspect('equal')
                except NotImplementedError:
                    pass
            # aesthetics
            ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.set_xlabel('x (m)')
            ax.set_ylabel('y (m)')
            ax.set_zlabel('z (m)')
            ax.set_axis_off()
        else:
            f = ax.get_figure()

        curs, lines = [], []
        bound = 0
        for k, v in list(self.items()):
            curs.append(v['current'])
            nseg = v['nseg']
            eta = np.linspace(0, 2 * np.pi, nseg + 1, True)
            ms = np.arange(v['nfcoil'] + 1)
            x = np.real(np.sum((v['xc'] - 1j * v['xs'])[:, None] * np.exp(1j * ms[:, None] * eta), 0))
            y = np.real(np.sum((v['yc'] - 1j * v['ys'])[:, None] * np.exp(1j * ms[:, None] * eta), 0))
            z = np.real(np.sum((v['zc'] - 1j * v['zs'])[:, None] * np.exp(1j * ms[:, None] * eta), 0))
            lines.append(ax.plot(x, y, z, label=k, **kwargs)[0])
            bound = max(bound, np.max(np.abs(np.hstack((x, y, z)))))
            if v['coil_symm'] == 1:
                for isym in range(1, bnfp):
                    sx = np.real(x * np.exp(1j * 2 * np.pi * isym / bnfp))
                    sy = np.real(y * np.exp(1j * 2 * np.pi * isym / bnfp))
                    sz = z * 1.0
                    curs.append(v['current'])
                    lines.append(ax.plot(sx, sy, sz, label=f'{k}_symm{isym}', **kwargs)[0])
                    bound = max(bound, np.max(np.abs(np.hstack((sx, sy, sz)))))
        # color by current
        from omfit_classes.utils_plot import set_linearray

        sm = set_linearray(lines, values=curs, vmin=vmin, vmax=vmax, cmap=cmap)
        if colorbar:
            cb = f.colorbar(sm, ax=ax, shrink=0.8)
            cb.set_label('Current (A)')

        # force equal aspect
        bound *= 0.6
        ax.set_xlim(-bound, bound)
        ax.set_ylim(-bound, bound)
        ax.set_zlim(-bound, bound)
        ax.auto_scale_xyz((-bound, bound), (-bound, bound), (-bound, bound))

        return lines

    @dynaLoad
    def _to_OMFITcoils(self, filename, bnfp=1, gpec_format=False):
        """
        Convert to the standard OMFITcoils ascii file format, which stores x,y,z,i points
        by inverse Fourier transforming the FOCUS coil decompositions.

        :param filename: str. Name of new file

        :param bnfp: int. Toroidal mode number of symmetry used if coil_symm is 1

        :param gpec_format: bool. Convert to OMFITGPECcoils ascii formatting instead

        :return: OMFITcoils or OMFITGPECcoils

        """
        coils = SortedDict()
        coils['periods'] = 1
        coils['num_coils'] = len(list(self.keys()))

        for i, (key, coil) in enumerate(list(self.items())):
            nseg = coil['nseg']
            eta = np.linspace(0, 2 * np.pi, nseg + 1, True)
            ms = np.arange(coil['nfcoil'] + 1)
            x = np.real(np.sum((coil['xc'] - 1j * coil['xs'])[:, None] * np.exp(1j * ms[:, None] * eta), 0))
            y = np.real(np.sum((coil['yc'] - 1j * coil['ys'])[:, None] * np.exp(1j * ms[:, None] * eta), 0))
            z = np.real(np.sum((coil['zc'] - 1j * coil['zs'])[:, None] * np.exp(1j * ms[:, None] * eta), 0))

            coils[key] = SortedDict()
            coils[key]['x'] = x
            coils[key]['y'] = y
            coils[key]['z'] = z
            coils[key]['I'] = coil['current'] * 1.0
            coils[key]['group'] = i + 1  # todo: can we get the group from FOCUS coils?
            coils[key]['name'] = key

            # if there is symmetry we need to add appropriately rotated coils
            if coil['coil_symm'] == 1:
                for isym in range(1, bnfp):
                    skey = f'{key}_symm{isym}'
                    coils[skey] = SortedDict()
                    coils[skey]['x'] = np.real(x * np.exp(1j * 2 * np.pi * isym / bnfp))
                    coils[skey]['y'] = np.real(y * np.exp(1j * 2 * np.pi * isym / bnfp))
                    coils[skey]['z'] = z * 1.0
                    coils[skey]['I'] = coil['current'] * 1.0
                    coils[skey]['group'] = i + 1  # todo: Confirm this should match for symm coils
                    coils[skey]['name'] = skey

        # Use the OMFIT class to create an empty file and then update it in memory
        if gpec_format:
            result = OMFITGPECcoils(filename)
        else:
            result = OMFITcoils(filename)
        result.update(coils)

        return result

    def to_OMFITcoils(self, filename, bnfp=1):
        """
        Convert to the standard OMFITcoils ascii file format, which stores x,y,z,i points
        by inverse Fourier transforming the FOCUS coil decompositions.

        :param filename: str. Name of new file

        :param bnfp: int. Toroidal mode number of symmetry used if coil_symm is 1

        :param gpec_format: bool. Convert to OMFITGPECcoils ascii formatting instead

        :return: OMFITcoils or OMFITGPECcoils

        """
        # Use a central functions so we do not duplicate complicated
        # inverse Fourier transformation code
        result = self._to_OMFITcoils(filename, bnfp=bnfp, gpec_format=False)

        return result

    @dynaLoad
    def to_OMFITGPECcoils(self, filename):
        """
        Convert OMFITcoils to the OMFITGPECcoils ascii file format, which writes x,y,z points
        but no current information.

        :param filename: str. Name of new file

        :param bnfp: int. Toroidal mode number of symmetry used if coil_symm is 1

        :return: OMFITGPECcoils

        """
        # Use a central functions so we do not duplicate complicated
        # inverse Fourier transformation code
        result = self._to_OMFITcoils(filename, bnfp=bnfp, gpec_format=True)

        return result


class OMFITGPECcoils(OMFITcoils):
    """
    Class that reads ascii GPEC .dat coil files and converts them to the standard coil file format used by
    the FOCUS and STELLOPT codes.

    NOTE: This will clobber the original ascii formatting!! Do not connect to original file paths!!

    """

    @dynaLoad
    def load(self):
        """Load the file and parse it into a sorted dictionary"""
        # read the ascii file
        try:
            with open(self.filename, 'r') as f:
                line1 = f.readline()
                ncoil, s, nsec, nw = list(map(int, list(map(float, line1.split()))))
            x, y, z = np.genfromtxt(self.filename, skip_header=1).T.reshape(3, ncoil, s, nsec)
            c = nw

            # fill in all the info needed for a coil file
            coils = self
            coils['periods'] = 1
            coils['num_coils'] = ncoil
            nc = 0
            for i in range(ncoil):
                for j in range(s):
                    key = 'coil_{:}'.format(nc)
                    coils[key] = SortedDict()
                    coils[key]['x'] = x[i, j, :]
                    coils[key]['y'] = y[i, j, :]
                    coils[key]['z'] = z[i, j, :]
                    coils[key]['I'] = nw  # should be multiplied by nominal current
                    coils[key]['group'] = i + 1
                    coils[key]['name'] = os.path.split(self.filename)[-1].split('.')[0]
                    nc += 1
            # coils['num_coils'] = nc  # why was this here? already set ncoil above... why was this ncoil + 1?
        except Exception:
            OMFITcoils.load(self)

    @dynaSave
    def save(self):
        """Write the data in standard ascii format"""
        print(self.filename)
        with open(self.filename, 'w') as f:
            # write the defining parameters
            ncoil = self['num_coils']
            s = 1  # have to assume this?
            nsec = len(self[list(self.keys())[-1]]['x'])
            nw = self[list(self.keys())[-1]]['I']
            if nsec < 1e4:
                f.write('{:>5}{:>5}{:>5}{:8.2f}\n'.format(ncoil, s, nsec, nw))  # the first line with periods
            else:
                f.write('{:>5}{:>5} {:}{:8.2f}\n'.format(ncoil, s, nsec, nw))  # the first line with periods
            # write each coil x, y, z
            for key, coil in list(self.items()):
                if not isinstance(coil, dict):
                    continue
                for i in range(len(coil['x'])):
                    f.write('{:13.4e}{:13.4e}{:13.4e}\n'.format(coil['x'][i], coil['y'][i], coil['z'][i]))
        return

    @dynaLoad
    def to_OMFITcoils(self, filename):
        """
        Convert to the standard OMFITcoils ascii file format, which stores x,y,z,i points.

        :param filename: str. Name of new file

        :return: OMFITcoils

        """

        # Use the OMFIT class to create an empty file and then update it in memory
        result = OMFITcoils(filename)
        result.update(self)

        return result
