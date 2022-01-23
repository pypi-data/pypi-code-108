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
from omfit_classes.sortedDict import SortedDict
from omfit_classes.utils_plot import View2d, View3d

import numpy as np

__all__ = ['OMFITuFile']


class OMFITuFile(SortedDict, OMFITascii):
    r"""
    Class used to interface with TRANSP U-files

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """

        if self.filename is None or not os.stat(self.filename).st_size:
            self.reset()
            return

        with open(self.filename, 'r') as f:
            fl = f.readlines()

        # if file is empty, make bare bones structure
        if not len(fl):
            self.reset()
            return

        self['SHOT'] = int(re.sub(r'\s*([0-9]+)\s*\w+\s+[0-9]\s+[0-9]\s+[0-9]*.*', r'\1', fl[0]))
        self['DEVICE'] = re.sub(r'\s*[0-9]+\s*(\w+)\s+[0-9]\s+[0-9]\s+[0-9]*.*', r'\1', fl[0]).strip()
        self['NDIM'] = int(re.sub(r'\s*[0-9]+\s*\w+\s+([0-9])\s+[0-9]\s+[0-9]*.*', r'\1', fl[0]))
        self['COMPRESSION'] = int(re.sub(r'\s[0-9]+\s*\w+\s+[0-9]\s+([0-9])\s+[0-9]*.*', r'\1', fl[0]))
        try:
            self['LSHOT'] = max(6, int(re.sub(r'\s*[0-9]*\w+\s+[0-9]\s+[0-9]\s+([0-9]*).*', r'\1', fl[0])))
        except Exception:
            self['LSHOT'] = ''

        self['DATE'] = fl[1].split(';')[0].strip()
        nscal = int(fl[2].split(';')[0].strip())
        self['SCALARS'] = SortedDict()
        n = 2
        end_scalars = 3
        for k in range(nscal):
            value = float(fl[3 + 2 * k].split(';')[0].strip())
            name, desc = fl[3 + 2 * k + 1].split(';')[0].split(':')
            self['SCALARS'][k] = SortedDict()
            self['SCALARS'][k]['data'] = value
            self['SCALARS'][k]['name'] = name.strip()
            self['SCALARS'][k]['desc'] = desc.strip()
            n = 3 + 2 * k + 1
            end_scalars = 3 + 2 * k + 2

        # check dimensionality
        ndim = -1
        for i, line in enumerate(fl[end_scalars:]):
            try:
                int(line.split(';')[0].strip())
                break
            except Exception:
                ndim += 1

        # generic variable line reader
        def setvar(k, line):
            tmp = [line[:21].strip(), line[21:31].strip()]
            self[k] = {'name': tmp[0], 'units': tmp[1]}

        # label independent then dependent variables
        dims = []
        for i in range(ndim):
            setvar('X{:}'.format(i), fl[end_scalars + i])
            dims.append(int(fl[end_scalars + ndim + 2 + i].split(';')[0]))
        setvar('F', fl[end_scalars + ndim])

        # proc code
        self['PROCESSING_CODE'] = int(fl[end_scalars + ndim + 1].split(';')[0])

        # keep the whole header
        end_header = end_scalars + ndim * 2 + 2
        for i, line in enumerate(fl[:end_header]):
            self['__header%04d__' % i] = line.rstrip('\n')

        # find the trailer
        start_trailer = end_header
        for i, line in enumerate(fl[end_header:]):
            if 'END-OF-DATA' in line:
                start_trailer = end_header + i
                break

        # read data as array (TRANSP scruncher has non-critical bug where format leaves no space between negatives)
        flat = ' '.join(fl[end_header:start_trailer])
        flat = flat.replace('E-', 'E~').replace('e-', 'e~').replace('-', ' -').replace('E~', 'E-').replace('e~', 'e-')
        flat = np.array(flat.split(), dtype=float)
        for i in range(ndim):
            start = int(np.sum(dims[:i]))
            self['X{:}'.format(i)]['data'] = flat[start : start + dims[i]]
        # data read in fortran conventional order?
        self['F']['data'] = flat[int(np.sum(dims)) :].reshape(dims[::-1]).T

        self['COMMENTS'] = []
        for i, line in enumerate(fl[start_trailer + 1 :]):
            if 'Beams used:' in line:
                self['BEAMS'] = [_f for _f in [k.strip(', \n') for k in (line + fl[start_trailer + 2 + i]).split(' ')[3:]] if _f]
            if len(line.strip('\n')):
                self['COMMENTS'].append(line.rstrip('\n'))

    @dynaSave
    def save(self):
        """
        Save Ufile to the file specified in the .filename attribute

        :return: None
        """
        # write empty line if an empty ufile
        if not (self['SHOT'] and self['DEVICE'] and self['NDIM']):
            with open(self.filename, 'w') as f:
                f.write('')  # adds leading space to all lines
            return

        tmp = []
        if self['LSHOT']:
            tmp.append(
                '{:>6}{:<4} {:} {:} {:}              ;-SHOT #- F(X) DATA WRITEUF OMFIT'.format(
                    self['SHOT'], self['DEVICE'], self['NDIM'], self['COMPRESSION'], max(6, self['LSHOT'])
                )
            )
            fmt = '12.5e'
        else:
            tmp.append(
                '{:>6}{:<4} {:} {:}               ;-SHOT #- F(X) DATA WRITEUF OMFIT'.format(
                    self['SHOT'], self['DEVICE'], self['NDIM'], self['COMPRESSION']
                )
            )
            fmt = '11.4E'
        tmp.append('{:<11}                   ;-SHOT DATE-  UFILES ASCII FILE SYSTEM'.format(self['DATE']))
        tmp.append('{:3}                           ;-NUMBER OF ASSOCIATED SCALAR QUANTITIES-'.format(len(self['SCALARS'])))
        for k in list(self['SCALARS'].keys()):
            tmp.append('{:11.4E}                   ;-SCALAR, LABEL FOLLOWS:'.format(self['SCALARS'][k]['data']))
            tmp.append('{:10}{:20}'.format(self['SCALARS'][k]['name'] + ':', self['SCALARS'][k]['desc']))
        for i in range(len(self['F']['data'].shape)):
            k = 'X{:}'.format(i)
            tmp.append('{:<20}{:<10};-INDEPENDENT VARIABLE LABEL: {:}-'.format(self[k]['name'], self[k]['units'], k))
        tmp.append('{:<20}{:<10};-DEPENDENT VARIABLE LABEL-'.format(self['F']['name'], self['F']['units']))
        tmp.append('{:<3}                           ;-PROC CODE- 0:RAW 1:AVG 2:SM 3:AVG+SM'.format(self['PROCESSING_CODE']))
        for i in range(len(self['F']['data'].shape)):
            k = 'X{:}'.format(i)
            tmp.append('{:>10}                    ;-# OF X{:} PTS-'.format(len(self[k]['data']), i))
        tmp[-1].replace('PTS-', 'PTS- F(X) DATA FOLLOW:')

        for i in range(len(self['F']['data'].shape)):
            data = self['X{:}'.format(i)]['data']
            dlen = len(data)
            for i in range(0, dlen, 6):
                j = min(6, dlen - i)
                tmp.append((('{:' + fmt + '} ') * j).format(*data[i : i + j]).rstrip(' '))
        data = self['F']['data'].T.flatten()
        dlen = len(data)
        for i in range(0, dlen, 6):
            j = min(6, dlen - i)
            tmp.append((('{:' + fmt + '} ') * j).format(*data[i : i + j]).rstrip(' '))

        tmp.append(';----END-OF-DATA-----------------COMMENTS:-----------;')
        for line in tolist(self['COMMENTS']):
            tmp.append(line.strip())

        with open(self.filename, 'w') as f:
            f.write(' ' + '\n '.join(tmp) + '\n')  # adds leading space to all lines
        return

    @dynaLoad
    def plot(self, axes=None, figure=None, cmap=None, **kw):
        r"""
        Plot Ufile content

        :param axes: Axes object or None

        :param figure: Figure object or None

        :param cmap: Color map name used for multi-dimensional plots.

        :param \**kw: Extra key word arguments passed to matplotlib plot function.

        :return: Figure
        """
        newf = False
        if axes is None and figure is None:
            fig, axes = pyplot.subplots()
            newf = True
        elif axes is None and figure is not None:
            fig = figure
            if fig.axes:
                axes = fig.axes[0]
            else:
                axes = fig.add_subplot(111)
        elif axes is not None:
            fig = axes.get_figure()

        im_opt = {}
        if cmap is not None:
            im_opt['cmap'] = cmap

        xlabels = []
        for i in range(len(self['F']['data'].shape)):
            xlabels.append('{:} [{:}]'.format(self['X{:}'.format(i)]['name'], self['X{:}'.format(i)]['units']))
            xlabels[-1] = xlabels[-1].replace('[]', '')
        name = '{:} [{:}]'.format(self['F']['name'], self['F']['units']).replace(' []', '')

        # 1D data
        if len(np.squeeze(self['F']['data']).shape) == 1:
            kw.setdefault('label', name)
            kw.setdefault('marker', '.' * (len(self['X0']['data']) < 100))
            axes.plot(self['X0']['data'], self['F']['data'], **kw)
            axes.set_xlabel(xlabels[0])
            if self['F']['units'] == self['X0']['units'] and self['X0']['units']:
                axes.set_aspect('equal')
            leg = axes.legend()
            if leg:
                leg.draggable(True)

        # 2D data
        elif len(np.squeeze(self['F']['data']).shape) == 2:
            view = View2d(
                self['F']['data'],
                coords=[self['X0']['data'], self['X1']['data']],
                dims=xlabels,
                name=name.split()[-1],
                axes=axes,
                im_opt=im_opt,
                **kw,
            )
            view.colorbar.set_label(name)
            fig, axes = view.fig, view.axm
            fig.view = view

        # 3D data
        elif len(np.squeeze(self['F']['data']).shape) == 3:
            view = View3d(
                self['F']['data'],
                coords=[self['X0']['data'], self['X1']['data'], self['X2']['data']],
                dims=xlabels,
                name=name.split()[-1],
                axes=axes,
                im_opt=im_opt,
                **kw,
            )
            view.colorbar.set_label(name)
            fig, axes = view.fig, view.axm
            fig.view = view
        else:
            'Plotting not available above 3D'

        if 'BEAMS' in self and newf:  # make a special beam overview
            fig2, axes = pyplot.subplots()
            for i in range(len(self['BEAMS'])):
                axes.plot(self['X0']['data'], self['F']['data'][:, i] / 1e6, label=self['BEAMS'][i])
            axes.plot(self['X0']['data'], np.sum(self['F']['data'][:, : len(self['BEAMS'])], 1) / 1e6, 'k--', label='Total')
            axes.set_xlabel('Time $[s]$')
            axes.set_ylabel('Power $[MW]$')
            axes.set_title('Neutral beams power from ' + os.path.split(self.filename)[1])
            leg = axes.legend(loc=0).draggable(True)

            for line in self['COMMENTS']:
                if 'tilt' in line:
                    printi(line)

        return fig

    @dynaLoad
    def smooth(self, window_x=None, window_len=11, window='hanning', axis=-1):
        """
        This built in function makes use of the OMFIT utils.smooth function
        to smooth over a single dimension of the data.

        If the axis in question is irregular, the data is first linearly interpolated onto
        a regular grid with spacing equal to the minimum step size of the irregular grid.

        :param window_x: Smoothing window size in axis coordinate units.
        :param window_len: Smoothing window size in index units. Ignored if window_x present. Enforced odd integer.
        :param window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.
        :param axis: Dimension over which to smooth. Accepts integer (0), key ('X0'), or name ('TIME').

        :return: OMFITuFile with the requested dimension smoothed

        """
        # generalize the axis specification
        if isinstance(axis, str):
            try:
                axis = int(axis.lstrip('X'))
            except Exception:
                for i in range(self['NDIM']):
                    if axis == self['X{:}'.format(i)]['name']:
                        axis = i
        if not isinstance(axis, int):
            raise ValueError('Unable to recognize axis {:}'.format(axis))
        axis = axis % (self['NDIM'])
        akey = 'X{:}'.format(axis)

        # copy if needed
        newu = copy.deepcopy(self)

        # force regular grid
        x = self[akey]['data']
        dx = np.diff(x)
        if not np.all(dx == dx[0]):
            printd('Interpolating to a regular grid', topic='OMFITuFile')
            newlen = int(np.ceil((x.max() - x.min()) / dx.min()))
            newx = np.linspace(x.min(), x.max(), newlen)
            fun = interp1d(x, self['F']['data'], axis=axis, kind='linear', bounds_error=False)
            newu[akey]['data'] = newx
            newu['F']['data'] = fun(newx)
            newu['COMMENTS'].append('Linearly interpolated to regular {:} grid.'.format(self[akey]['name']))
        else:
            newx = x

        # smooth
        if window_x:
            window_len = int(np.round(window_x / (newx[1] - newx[0]), 0))
        window_x = (newx[1] - newx[0]) * window_len
        newu['F']['data'] = utils.map1d(smooth, newu['F']['data'], axis=axis, window_len=window_len, window=window)

        # mark file as smoothed
        newu['PROCESSING_CODE'] = 2
        newu['COMMENTS'].append(
            'Smoothed over a {:} window with length of {:} in the {:} axis.'.format(window, window_x, newu[akey]['name'])
        )

        return newu

    def crop(self, xmin, xmax, axis=-1, endpoint=True):
        """
        Crop ufile data to only include points within the specified range along a given axis.
        Modifies the ufile object in place.

        :param xmin: Lower bound.
        :param xmax: Upper bound.
        :param axis: Dimension to bound. Accepts integer (0), key ('X0'), or name ('TIME').
        :param endpoint: Keeps an extra point on either end, ensuring the bounds are contained within the range of ufile data.

        """
        # generalize the axis specification
        if isinstance(axis, str):
            try:
                axis = int(axis.lstrip('X'))
            except Exception:
                for i in range(self['NDIM']):
                    if axis == self['X{:}'.format(i)]['name']:
                        axis = i
        if not isinstance(axis, int):
            raise ValueError('Unable to recognize axis {:}'.format(axis))
        axis = axis % (self['NDIM'])
        akey = 'X{:}'.format(axis)
        x = np.array(self[akey]['data'])
        # slice axis
        if endpoint:
            xslice = np.array([False] + list((x >= xmin) & (x <= xmax)) + [False])
            xslice = xslice[2:] | xslice[1:-1] | xslice[0:-2]
        else:
            xslice = (x >= xmin) & (x <= xmax)
        self[akey]['data'] = self[akey]['data'][xslice]
        # slice data
        dslice = [slice(stop) for i, stop in enumerate(np.shape(self['F']['data']))]
        dslice[axis] = xslice
        self['F']['data'] = self['F']['data'][dslice]
        # annotate
        self['COMMENTS'].append('Cropped range ({:},{:}) along {:} axis'.format(xmin, xmax, akey))

    def from_OMFITprofiles(self, OMFITprofiles_fit):
        """
        populate u-file based on OMFITprofiles fit xarray DataArray

        :params OMFITprofiles_fit: input OMFITprofiles fit xarray DataArray
        """
        self['NDIM'] = len(OMFITprofiles_fit.values.shape)
        self['SHOT'] = OMFITprofiles_fit.attrs['shot']
        self['DEVICE'] = OMFITprofiles_fit.attrs['device']

        self['DATE'] = now()
        self['COMMENTS'] = tolist('generated from OMFITprofiles')

        self['X0']['data'] = OMFITprofiles_fit['time'].values / 1000.0
        self['X0']['name'] = 'time'
        self['X0']['units'] = 's'

        self['F']['data'] = nominal_values(OMFITprofiles_fit.values / 1000.0)
        self['F']['name'] = OMFITprofiles_fit.name
        try:
            self['F']['units'] = OMFITprofiles_fit.attrs['units']
        except Exception:
            self['F']['units'] = ''

        if self['NDIM'] == 2:
            self['X1'] = dict()
            self['X1']['data'] = nominal_values(OMFITprofiles_fit[OMFITprofiles_fit.dims[1]].values)
            self['X1']['name'] = OMFITprofiles_fit.dims[1]
            try:
                self['X1']['units'] = OMFITprofiles_fit[OMFITprofiles_fit.dims[1]].attrs['units']
            except Exception:
                self['X1']['units'] = ''

    def reset(self):
        '''Set up basic bare bones structure'''
        self['SHOT'] = 0
        self['DEVICE'] = ''
        self['NDIM'] = 0
        self['COMPRESSION'] = 0
        self['LSHOT'] = 0
        self['DATE'] = ''
        self['SCALARS'] = SortedDict()
        self['X0'] = {'name': '', 'units': '', 'data': np.array([])}
        self['F'] = {'name': '', 'units': '', 'data': np.array([])}
        self['PROCESSING_CODE'] = 0
        self['COMMENTS'] = []
