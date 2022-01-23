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

from omfit_classes.omfit_namelist import OMFITnamelist
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_nc import OMFITnc
from omfit_classes.omfit_mds import OMFITmdsValue, OMFITmds
from omas import ODS, omas_environment
from omfit_classes.omfit_data import Dataset, DataArray
from omfit_classes.sortedDict import OMFITdataset, SortedDict
from omfit_classes.utils_math import atomic_element
from omfit_classes.omfit_ufile import OMFITuFile
from omfit_classes.utils_plot import *

from scipy.interpolate import LinearNDInterpolator, RectBivariateSpline
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk as NavigationToolbar2
import numpy as np
from scipy import integrate

__all__ = [
    'OMFITtranspNamelist',
    'OMFITtranspData',
    'OMFITtranspMultigraph',
    'OMFITplasmastate',
    'OMFITtranspOutput',
    'check_TRANSP_run',
    'wait_TRANSP_run',
    'next_available_TRANSP_runid',
    'OMFITfbm',
]

_OMFITtranspNamelist_class_attributes = {
    'collect_arrays': {'__offset__': 1},  # Collect arrays to access array data consistently within OMFIT
    'explicit_arrays': True,  # TRANSP requires arrays to have style: ARR(1)
    'compress_arrays': False,  # TRANSP does not surpport NAMELIST repetitions
    'max_array_chars': None,  # TRANSP does not support arrays on multiple lines
    'separator_arrays': ', ',
    'outsideOfNamelistIsComment': False,
    'split_arrays': True,  # TRANSP requires each namelist row not to exceed 132 characters
    'end_token': '&END',
}


class OMFITtranspNamelist(OMFITnamelist):
    r"""
    Class used to interface with TRANSP input "namelist"
    This is necessary because the TRANSP input namelist is not a default format
    (e.g. with the update_time functionality)

    :param filename: filename passed to OMFITobject class

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        tmp = {}
        tmp.update(_OMFITtranspNamelist_class_attributes)
        tmp.update(kw)
        OMFITnamelist.__init__(
            self, filename, **tmp
        )  # the call to OMFITnamelist.__init__ with **kw takes care of setting up the class attributes
        for k in list(_OMFITtranspNamelist_class_attributes.keys()):
            if k in self.OMFITproperties and self.OMFITproperties[k] == _OMFITtranspNamelist_class_attributes[k]:
                self.OMFITproperties.pop(k, None)

    @dynaLoad
    def load(self):
        """
        Method used to load the content of the file specified in the .filename attribute

        :return: None
        """
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        sections = SortedDict()
        sec = 'main'
        sections[sec] = []
        for line in lines:
            line = line.strip('\n')
            if re.match(r'^\s*~update_time\s*=\s*[\.0-9]', line):
                try:
                    sec = float(line.split('!')[0].split('=')[1].strip())
                    sections[sec] = []
                except Exception:
                    pass
            else:
                sections[sec].append(line)
        for sec in list(sections.keys()):
            sections[sec] = '\n'.join(sections[sec])
            tmp = NamelistFile(
                None, input_string=sections[sec], **{attr: getattr(self, attr) for attr in _OMFITtranspNamelist_class_attributes}
            )
            if sec == 'main':
                self.update(tmp)
            else:
                self[sec] = tmp

    @dynaSave
    def save(self):
        """
        Method used to save the content of the object to the file specified in the .filename attribute

        :return: None
        """
        tmp = SortedDict(sorted=True)
        for k in list(self.keys()):
            if not isinstance(k, str):
                tmp[k] = self[k]
                del self[k]
        super(OMFITnamelist, self).save()
        with open(self.filename, 'a') as f:
            for k in list(tmp.keys()):
                f.write('~update_time = %f\n' % k)
                tmp_file = NamelistFile()
                tmp_file.update(tmp[k])
                tmp_file.save(fp=f)
                self[k] = tmp_file

    @property
    def update_time(self):
        """
        This attribute returns a SortedDictionary with the update times elements in the TRANSP namelist
        """
        tmp = SortedDict(sorted=True)
        for k in sorted(self.keys()):
            if not isinstance(k, str):
                tmp[k] = self[k]
        return tmp

    def _checkSetitem(self, key, val):
        """
        Allow non-string keys
        """
        return key, val


class OMFITtranspData(SortedDict):
    """
    Class for plotting and manipulating TRANSP output MDS and CDF files
    """

    def __init__(self, transp_output, data):
        """
        Initialize data object from a OMFITmdsValue

        :param transp_output: OMFITmds object or OMFITnc object containing transp run

        :param data: Output data label

        :type data: str

        >> OMFIT['NC_d3d']=OMFITnc(filename)
        >> OMFITtranspData(OMFIT['NC_d3d'],'Q0')
        >> OMFITtranspData(OMFIT['NC_d3d'],'NE')
        >>
        >> OMFIT['MDS_d3d']=OMFITmds(server='D3D', treename='transp', shot='1551960501')
        >> OMFITtranspData(OMFIT['MDS_d3d'],'Q0')
        >> OMFITtranspData(OMFIT['MDS_d3d'],'NE')
        >>
        >> OMFIT['MDS_iter']=OMFITmds(server='transpgrid', treename='transp_iter', shot='201001676')
        >> OMFITtranspData(OMFIT['MDS_iter'],'Q0')
        >> OMFITtranspData(OMFIT['MDS_iter'],'NE')
        """

        # NetCDF
        if isinstance(transp_output, OMFITnc):
            self['DATA'] = transp_output[data]['data']
            self['DIM_OF'] = [
                transp_output[transp_output[data]['__dimensions__'][k]]['data'] for k in reversed(list(range(len(self['DATA'].shape))))
            ]
            self['UNITS_DIM_OF'] = [
                transp_output[transp_output[data]['__dimensions__'][k]]['units'].strip()
                for k in reversed(list(range(len(self['DATA'].shape))))
            ]
            self['UNITS_DIM_OF'] = [re.sub('SECONDS', 's', x) for x in self['UNITS_DIM_OF']]
            if len(self['DATA'].shape) == 2:
                self['XAXIS'] = transp_output[data]['__dimensions__'][1]
                if len(self['DIM_OF'][1].shape) == 1:
                    self['DIM_OF'] = [self['DIM_OF'][0], np.array([self['DIM_OF'][1]] * self['DIM_OF'][0].shape[1]).T]
            self['LABEL'] = transp_output[data]['long_name'].strip() + ' (%s)' % transp_output[data]['units'].strip()
            self['RPLABEL'] = transp_output[data]['long_name'].strip()
            self['UNITS'] = transp_output[data]['units'].strip()
            self['CDF'] = transp_output

        # MDS+
        elif isinstance(transp_output, OMFITmds):
            # time needs to be treated special since in MDS+ 'TIME' is stored ad TIME1D and TIME2D
            if data == 'TIME' and 'TIME' not in transp_output['OUTPUTS']['ONE_D']:
                Data = transp_output['OUTPUTS']['ONE_D']['AIMP']
                self['DATA'] = Data.dim_of(0)
                self['DIM_OF'] = [self['DATA']]
                self['UNITS_DIM_OF'] = ['s']
                self['LABEL'] = 'Time'
                self['RLABEL'] = 'Time'
                self['UNITS'] = ['s']

            # get all the data
            else:
                if data in transp_output['OUTPUTS']['ONE_D']:
                    Data = transp_output['OUTPUTS']['ONE_D'][data]
                else:
                    Data = transp_output['OUTPUTS']['TWO_D'][data]

                self['DATA'] = Data.data()

                if data == 'TIME' or data in transp_output['OUTPUTS']['ONE_D']:

                    # this is to handle different ways of storing dim_of information at GA and PPPL
                    if len(transp_output['OUTPUTS']['ONE_D']['TIME1D']):
                        time = transp_output['OUTPUTS']['ONE_D']['TIME1D'].data()
                    else:
                        time = Data.dim_of(0)
                    self['DIM_OF'] = [time]
                    self['UNITS_DIM_OF'] = ['s']

                elif data in transp_output['OUTPUTS']['TWO_D']:

                    self['XAXIS'] = Data['XAXIS'].data()[0].strip()
                    self['DIM_OF'] = [transp_output['OUTPUTS']['TWO_D'][self['XAXIS']].data()]
                    self['UNITS_DIM_OF'] = [transp_output['OUTPUTS']['TWO_D'][self['XAXIS']]['UNITS'].data()[0].strip()]

                    # this is to handle different ways of storing dim_of information at GA and PPPL
                    if len(transp_output['OUTPUTS']['ONE_D']['TIME1D']):
                        time = transp_output['OUTPUTS']['ONE_D']['TIME1D'].data()
                    else:
                        time = Data.dim_of(1)
                    self['DIM_OF'].append(np.tile(time, (Data.data().shape[1], 1)).T)
                    self['UNITS_DIM_OF'].append('s')

                # get all the metadata
                for k in ['LABEL', 'RPLABEL', 'UNITS']:
                    self[k] = Data[k].data()[0].strip()
                    self[k] = re.sub(r' \)', ')', re.sub('  +', ' ', self[k]))

            # save knowledge of the tree
            self['MDS'] = transp_output

        else:
            raise ValueError(
                'transp_output of class %s is not recognized. Must be either %s or %s' % (transp_output.__class__, OMFITmds, OMFITnc)
            )

    def plot(self, axes=None, label='RPLABEL', slice_axis=None, slice_at=[], **kw):
        """
        Plot TRANSP data, using default metadata.

        If Data is one dimensional, it is plot using the matplotlib plot function.
        If 2D, the default is to show the data using View2d. If a slice_axis is defined, the slices
        are shown as line plots.
        Extra key words are passed to the plot or View2d function used.

        :param axes: Axes in which to make the plots.
        :type axes: Axes
        :param label: Labels the data in the plot. If 'LABEL' or 'RPLABEL' these values are taken from the Data.
        :type label: str
        :param slice_axis:  Slices 2D data along the radial (0) or time (1) axis.
        :type slice_axis: int
        :param slice_at: Slices made in slice_axis. An empty list plots all available slices.
        :type slice_at: np.ndarray

        :return: Figure
        """
        # don't modify someone's outside options
        kw = copy.copy(kw)

        # force 1D list of slices
        if slice_at is None:
            slice_at = []
        slice_at = np.array([slice_at]).ravel()

        # use metadaat for default labels
        if label in ['RPLABEL', 'LABEL']:
            if self[label].endswith('(' + self['UNITS'] + ')') or self[label].endswith('(' + self['UNITS'] + ' )'):
                label = self[label].strip()
            else:
                label = self[label] + ' (' + self['UNITS'] + ')'

        # make new plot if needed
        if axes:
            fig = axes.get_figure()
        elif 'figure' in kw:
            fig = kw['figure']
            if fig.axes:
                axes = fig.axes[0]
            else:
                axes = fig.add_subplot(111)
        else:
            fig = pyplot.gcf()
            axes = pyplot.gca()

        im_opt = {}
        if 'cmap' in kw:
            im_opt['cmap'] = kw.pop('cmap')

        # 1D data
        if len(self['DIM_OF']) == 1:
            kw.setdefault('label', label)
            axes.plot(self['DIM_OF'][0], self['DATA'], **kw)
            axes.set_xlabel('Time $[{:}]$'.format(self['UNITS_DIM_OF'][0]))

        # 2D data
        elif len(self['DIM_OF']) == 2:
            x = self['DIM_OF'][0][0]
            t = self['DIM_OF'][1][:, 0]
            y = self['DATA']
            x0label = '{:} [{:}]'.format(self['XAXIS'], self['UNITS_DIM_OF'][0]).replace('[]', '')
            x1label = '{:} [{:}]'.format('Time', self['UNITS_DIM_OF'][1]).replace('[]', '')

            # default is interactive data interface
            if slice_axis == None:
                view = View2d(
                    self['DATA'].T,
                    coords=[x, t],
                    dims=[x0label, x1label],
                    name='$[' + self['UNITS'] + ']$',
                    axes=axes,
                    imag_options=im_opt,
                    **kw,
                )
                view.colorbar.set_label(label)
                fig, axes = view.fig, view.axm
                fig.view = view

            # retain plain 2D contour plot option
            elif slice_axis < 0:
                cs = utils.utils_plot.pcolor2(x, t, self['DATA'], cmap=cmap, **kw)
                cr = utils.utils_plot.contour(x, t, y, 21, colors='k')
                cb = utils.utils_plot.colorbar(cs, label=label)
                axes.set_xlabel(x0label)
                axes.set_ylabel(x1label)

            # plot 1D slices
            else:

                # collect slices
                if len(slice_at) == 0:
                    if slice_axis == 1:
                        yy = y
                        slice_at = t
                    else:
                        yy = y.T
                        slice_at = x
                else:
                    tmp = RectBivariateSpline(x, t, y.T, kx=min(3, len(x)), ky=min(3, len(t)))
                    if slice_axis == 0:
                        yy = [tmp.ev(t * 0 + s, t) for s in slice_at]
                    elif slice_axis == 1:
                        yy = [tmp.ev(x, x * 0 + s) for s in slice_at]
                xx = [t, x][slice_axis]
                xl = [x1label, x0label][slice_axis]
                slice_label = [x1label, x0label][slice_axis - 1]

                # plot lines
                lines = []
                for yi in yy:
                    lines += axes.plot(xx, yi, **kw)
                if len(slice_at) == 1:
                    label += ', {:}={:}'.format(slice_label.split()[0], slice_at[0])
                else:
                    sm = utils_plot.set_linearray(lines, slice_at)
                    cb = fig.colorbar(sm)
                    cb.set_label(slice_label)
                kw.setdefault('label', label)
                axes.lines[-1].set_label(kw['label'])
                axes.set_xlabel(xl)

                if label and label.upper() != 'tk.NONE':
                    leg = axes.legend(loc=0)
                    if leg:
                        leg.draggable(True)

        return fig


class OMFITtranspMultigraph(SortedDict):
    """
    Class for unique manipulation/plotting of TRANSP multigraph mdsValues.
    """

    def __init__(self, MDStree, data):
        """
        Initialize data object from a `OMFITmdsValue`.

        :param MDStree: OMFITmdsTree object
        :type MDStree: :class:`omfit_mds`
        :param data: Name of multigraph
        :type data: str

        """
        # get all the data
        content = list(map(lambda x: str(x).strip(), MDStree['MULTIGRAPHS'][data]['CONTENT'].data()))
        self['CONSIGN'] = np.array(MDStree['MULTIGRAPHS'][data]['CONSIGN'].data())
        self['LABEL'] = MDStree['MULTIGRAPHS'][data]['LABEL'].data()[0].strip()
        self['CONTENT'] = SortedDict()
        for k, s in zip(content, self['CONSIGN']):
            self['CONTENT'][k] = OMFITtranspData(MDStree, k)
            if np.any(self['CONSIGN'] < 0):
                self['CONTENT'][k]['DATA'] *= s
                self['CONTENT'][k]['LABEL'] = '{:}*{:}'.format(s, self['CONTENT'][k]['LABEL'])
                self['CONTENT'][k]['RPLABEL'] = '{:}*{:}'.format(s, self['CONTENT'][k]['RPLABEL'])
        self['DIM_ND'] = len(self['CONTENT'][content[-1]]['DIM_OF'])

    def plot(self, axes=None, label='LABEL', squeeze=None, **kw):
        """
        Plot each data object in the multigraph.

        :param axes: Axes in which to plot.
        :param label: String labeling the data. 'LABEL' or 'RPLABEL' are taken from TRANSP metadata.
        :param squeeze: Bool demanding all plots be made on a single figure. Default is True for 1D data.

        All other key word arguments are passed to the individual OMFITtranspData plot functions.

        """
        # defaults
        kw.setdefault('slice_at', [])
        kw.setdefault('slice_axis', None)
        kw['slice_at'] = np.array([kw['slice_at']]).ravel()  # forces 1D

        # Single lines or not
        if squeeze == None:
            if self['DIM_ND'] == 1:
                squeeze = True
            elif kw['slice_axis'] != None and len(kw['slice_at']) == 1:
                squeeze = True

        # use metadaat for default labels
        if label in ['LABEL']:
            label = self[label]

        # set up figure(s)
        if squeeze:
            if not axes:
                note, axes = pyplot.subplots()
        # make a notebook to organize/collect all the 2D plots
        else:
            master = tk.Toplevel(OMFITaux['rootGUI'])
            if OMFITaux['rootGUI'] is not None and OMFITaux['rootGUI'].globalgetvar('figsOnTop'):
                master.transient(OMFITaux['rootGUI'])
            master.wm_title(label)
            master.geometry("710x710")
            note = ttk.Notebook(master)

        # plot all content
        for k, v in list(self['CONTENT'].items()):
            # overplot the 1D quantities
            if squeeze:
                note = v.plot(axes=axes, label='LABEL', **kw)
            # pack 2D viewers into tabs in a common notebook
            else:
                # add the Tkinter GUI tab
                tab = ttk.Frame(note)
                note.add(tab, text=k)
                note.pack()
                # embed the figure
                fig = matplotlib.figure.Figure()
                canvas = FigureCanvasTkAgg(fig, master=tab)
                canvas.draw()
                fig.set_canvas(canvas)
                canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
                # Add standard toolbar to plot
                toolbar = NavigationToolbar2(canvas, tab)
                toolbar.update()
                canvas._tkcanvas.pack(side='top', fill='both', expand=1)
                tab.fig = v.plot(figure=fig, **kw)

                def update_slices(tab, event=None):
                    """Keep all view slices consistent"""
                    if hasattr(tab.fig, 'view'):
                        xlim = tab.fig.view.get_vslice_args()
                        ylim = tab.fig.view.get_hslice_args()
                        for tid in note.tabs():
                            t = note.children[tid.split('.')[-1]]
                            if t != tab and hasattr(t, 'fig') and hasattr(t.fig, 'view'):
                                view = t.fig.view
                                view.hslice(*ylim)
                                view.vslice(*xlim)

                tab.update_slices = utils.types.MethodType(update_slices, tab)
                tab.bind('<FocusOut>', tab.update_slices)

        # extra features
        if squeeze:
            leg = axes.legend()
            leg.draggable(True)
        else:
            # add summary tab to the Tkinter GUI
            if hasattr(tab.fig, 'view'):
                tab = ttk.Frame(note)
                note.add(tab, text='Summary')
                note.pack()
                # embed the figure
                fig = matplotlib.figure.Figure()
                canvas = FigureCanvasTkAgg(fig, master=tab)
                canvas.draw()
                fig.set_canvas(canvas)
                canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
                # Add standard toolbar to plot
                toolbar = NavigationToolbar2(canvas, tab)
                toolbar.update()
                canvas._tkcanvas.pack(side='top', fill='both', expand=1)
                axx = fig.add_subplot(211)
                axy = fig.add_subplot(212)
                tab.fig = fig

                def update_lines(tab, event=None):
                    axx, axy = tab.fig.axes[:2]
                    for a in [axx, axy]:
                        a.lines = []
                        a.collections = []
                        a.set_prop_cycle('color', pyplot.rcParams['axes.prop_cycle'].by_key()['color'])
                    for tid in note.tabs():
                        k = note.tab(tid, 'text')
                        t = note.children[tid.split('.')[-1]]
                        if not hasattr(t, 'fig') or not hasattr(t.fig, 'view'):
                            continue
                        fig = t.fig
                        v = fig.view
                        # re-produce fills
                        (l,) = axx.plot(v._hslice_xdata, v._hslice_mean, label=k, **v.plot_options)
                        axx.fill_between(
                            v._hslice_xdata, v._hslice_mean - v._hslice_std, v._hslice_mean + v._hslice_std, color=l.get_color(), alpha=0.3
                        )
                        (l,) = axy.plot(v._vslice_xdata, v._vslice_mean, label=k, **v.plot_options)
                        axy.fill_between(
                            v._vslice_xdata, v._vslice_mean - v._vslice_std, v._vslice_mean + v._vslice_std, color=l.get_color(), alpha=0.3
                        )
                    # refresh labels
                    # axx.texts = [axx.text(0.02,0.95,v.axx.texts[0].get_text(),verticalalignment='top',
                    #                      transform=axx.transAxes)]
                    # axy.texts = [axy.text(0.02,0.95,v.axy.texts[0].get_text(),verticalalignment='top',
                    #                      transform=axy.transAxes)]
                    axx.set_xlabel(fig.view.axm.get_xlabel())
                    axx.set_ylabel(fig.view.axx.get_ylabel())
                    axy.set_ylabel(fig.view.axy.get_xlabel())
                    axy.set_xlabel(fig.view.axm.get_ylabel())
                    axx.autoscale()
                    axy.autoscale()
                    lx = axx.legend()
                    ly = axy.legend()
                    tab.fig.canvas.draw()
                    return

                tab.update_lines = utils.types.MethodType(update_lines, tab)
                tab.bind('<FocusIn>', tab.update_lines)

            # resize notebook figures with main window
            def set_fig_size(event=None):
                master.unbind('<Configure>')
                master.update_idletasks()
                note.configure(width=master.winfo_width())
                note.configure(height=master.winfo_height())
                master.bind('<Configure>', set_fig_size)

            set_fig_size()
            master.bind('<Configure>', set_fig_size)

            # allow keys to change tabs
            note.enable_traversal()

        return note

    plot.__doc__ += OMFITtranspData.plot.__doc__


def check_TRANSP_run(runid, project=None, tunnel=None):
    """
    Function that checks the status of a TRANSP run as reported
    by the TRANSP MONITOR GRID website: https://w3.pppl.gov/transp/transpgrid_monitor

    :param runid: runid to be checked

    :param project: project (ie. tokamak) of the runid (optional)

    :param tunnel: use SOCKS via specified tunnel

    :return: * None if no matching runid/project is found
             * tuple with 1) True/None/False if run went ok, run is waiting, run failed
                     and  2) dictionary with parsed HTML information
    """

    socks = {}
    if tunnel is not None:
        tmp = setup_socks(tunnel)
        socks['http'] = 'socks5://localhost:' + tmp[2]
        socks['https'] = 'socks5://localhost:' + tmp[2]
    url = 'https://w3.pppl.gov/cgi-bin/transpgrid_monitor.frames'
    data = {'runid': runid}
    if project is not None:
        data.update({'project': project})

    import requests
    from urllib3.exceptions import InsecureRequestWarning

    with warnings.catch_warnings(record=False) as w:
        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        response = requests.get(url, data, proxies=socks, verify=False)
    response.raise_for_status()
    the_page = response.text

    items = ['project', 'owner', 'details', 'status', 'remarks']

    parsed = OrderedDict()
    for line in the_page.split('\n'):
        if np.all([k in line for k in items]):
            line = re.sub('&nbsp', '', line)
            line = re.sub('''<(?:"[^"]*"['"]*|'[^']*'['"]*|[^'">])+>''', '\n', line)
            line = [_f for _f in line.split('\n') if _f]
            for entry, value in zip(line[::2], line[1::2]):
                parsed.setdefault(entry, '')
                parsed[entry] += value

    wait = ['submitted', 'active', 'HALT_RQST', 'mdswrite']
    ok = ['success', 'Fetched']
    bad = ['stopped', 'canceled', 'HALT_FAILED', 'double', 'nopriv', 'suspended']

    if np.any([k in ok for k in list(parsed.keys())]):
        return True, parsed

    elif np.any([k in wait for k in list(parsed.keys())]):
        return None, parsed

    elif np.any([k in bad for k in list(parsed.keys())]):
        return False, parsed


def wait_TRANSP_run(runid, project=None, t_check=5, verbose=True, tunnel=None):
    """
    Function that waits for a TRANSP run to end as reported
    by the TRANSP MONITOR GRID website: https://w3.pppl.gov/transp/transpgrid_monitor

    :param runid: runid to be checked

    :param project: project (ie. tokamak) of the runid (optional)

    :param t_check: how often to check (seconds)

    :param verbose: print to screen

    :param tunnel: use SOCKS via specified tunnel

    :return: * None if no matching runid/project is found
             * tuple with 1) True/False if run went ok or run failed
                     and  2) dictionary with parsed HTML information
    """

    aborted = tk.BooleanVar()
    aborted.set(False)
    if OMFITaux['rootGUI'] is not None:

        def onAbort():
            aborted.set(True)

        try:
            if OMFITaux['pythonRunWindows'][-1] is None:
                raise RuntimeError('--')
            top = ttk.Frame(OMFITaux['pythonRunWindows'][-1], borderwidth=2, relief=tk.GROOVE)
            top.pack(side=tk.TOP, expand=tk.NO, fill=tk.BOTH, padx=5, pady=5)
        except Exception:
            top = tk.Toplevel(OMFITx._topGUI(OMFITaux['rootGUI']))
            top.transient(OMFITaux['rootGUI'])

        top.update_idletasks()
        ttk.Label(top, text='TRANSP wait ' + str(runid), wraplength=top.winfo_width()).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        p = ttk.Progressbar(top, orient=tk.HORIZONTAL, mode='indeterminate')
        p.start()
        p.pack(padx=5, pady=5, expand=tk.NO, fill=tk.X)
        frm = ttk.Frame(top)
        ttk.Button(frm, text="Abort", command=onAbort).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        frm.pack(side=tk.TOP)
        top.update_idletasks()

    status = None
    old_print = None
    t = -1
    dt = 0.1
    n = 0
    while not aborted.get():
        if t < 0:
            t = t_check
            out = check_TRANSP_run(runid, project, tunnel=tunnel)

            # if the runid does not appear in the list
            # wait 5x the t_check before giving up
            if out is None:
                if n == 5:
                    if OMFITaux['rootGUI'] is not None:
                        top.destroy()
                    return None
                n += 1

            # if the runid is listed print only new updates
            else:
                n = 0
                if old_print != repr(out[1]):
                    if verbose:
                        print('-' * 5 + ' ' + str(runid) + ' ' + '-' * 5 + ' ' + now())
                        for k in out[1]:
                            printi('%s : %s' % (k, out[1][k]))
                elif out[0] is not None:
                    break
                old_print = repr(out[1])

        sleep(dt)

        t = t - dt

    if OMFITaux['rootGUI'] is not None:
        top.destroy()

    if aborted.get():
        raise OMFITexception('-- Aborted by user waiting for TRANSP run %s --' % str(runid))

    return out


def next_available_TRANSP_runid(runid, project, increment=1, skiplist=[], server=None):
    """
    Function which checks what MDS+ tree entries are available

    :param runid: runid to start checking from (included)

    :param project: project [e.g. D3D, ITER, NSTX, ...] used to set the MDS+ TRANSP tree and server to be queried

    :param increment: positive / negative

    :param skiplist: list of runids to skip

    :param server: MDS+ TRANSP server to be queried [e.g. 'atlas.gat.com', or 'transpgrid.pppl.gov']

    :return: tuple with next available runid (as integer with format shotXXYY) and augmented skiplist
    """

    # handle letter in runid
    try:
        int(runid)
    except Exception:
        shot = runid[:-3]
        letter = runid[-3:-2].upper()
        index = runid[-2:]
        runid = str(str(shot) + str(ord(letter) - ord('A') + 1) + index)
    runid = str(runid)
    runid_base = str(runid)[:-2]

    # wrap around counting up/down
    if increment > 0:
        lst = np.mod(int(runid[-2:]) - 1 + np.arange(0, 99), 99) + 1
    else:
        lst = np.mod(int(runid[-2:]) - 1 - np.arange(0, 99), 99) + 1

    # handle MDS+ server/treename
    if server == None:
        if project in ['D3D', 'DIII-D']:
            server = 'atlas.gat.com'
            project = 'D3D'
        else:
            server = 'transpgrid.pppl.gov'
    if server == 'atlas.gat.com':
        tree = 'transp'
    else:
        tree = 'transp_' + project.lower()

    # look in search for first available spot
    list_busy = copy.copy(skiplist)
    import MDSplus

    for k in lst:
        runid = int('%s%02d' % (runid_base, k))
        if k in list_busy:
            printi('skipping %d' % runid)
            continue
        printi('testing  %d' % runid)
        try:
            tmp = OMFITmdsValue(server=server, treename=tree, shot=runid, TDI='\\' + tree.upper() + '::TOP.OUTPUTS.ONE_D.AIMP').data()
            if tmp is None or isinstance(tmp, np.ndarray):
                printw('MDSplus tree exists')
            list_busy.append(k)
        except Exception as _excp:
            printi('Found available MDSplus tree')
            return runid, list_busy

    raise OMFITexception('No available runid for %s' % runid_base)


class OMFITplasmastate(OMFITnc):
    """
    Class for handling TRANSP netcdf statefile (not to be confused with the time-dependent TRANSP output CDF file)
    """

    sources = {
        'pe_trans': 'Total power to electrons',
        'pi_trans': 'Total power to ions',
        'qie': 'Collisional exchange from ions to electrons',
        'pbe': 'Beam power to electrons',
        'pbi': 'Beam power to ions',
        'pbth': 'Thermalization of beam power to ions',
        'peech': 'ECH power to electrons',
        'pohme': 'Ohmic heating power to electrons',
        'pmine': 'Electron heating power by minority ions',
        'pmini': 'Ion heating power by minority ions',
        'pminth': 'Thermalization of ion heating power by minority ions',
        'picth': 'Direct ion heating power by ICRF',
        'pfuse': 'Fusion alpha power transferred to electrons',
        'pfusi': 'Fusion alpha power transferred to thermal ions',
        'pfusth': 'Thermalization of fusion alpha power transferred to thermal ions',
        'prad_cy': 'Radiated power: synchrotron',
        'prad_br': 'Radiated power: bremsstrahlung',
        'prad_li': 'Radiated power: line',
        'tq_trans': 'Angular momentum source torque',
        'sn_trans': 'Particle source',
    }

    def calcQ(self):
        """
        :return: fusion gain
        """
        auxi = 0
        for k in ['pbi', 'picth', 'pmini']:
            auxi += np.sum(self[k]['data'])

        auxe = 0
        for k in ['pbe', 'peech', 'pmine', 'pohme']:
            auxe += np.sum(self[k]['data'])

        aux = auxe + auxi

        fuse = np.sum(self['pfuse']['data'])
        fusi = np.sum(self['pfusi']['data'])
        fus_alpha = fuse + fusi
        fus_neut = (fuse + fusi) * 4

        return (fus_neut + fus_alpha) / aux

    def summary_sources(self):
        """
        Print summary of integrated sources
        """
        for item in sorted(list(self.sources.keys())):
            if item.startswith('p'):
                print('%s:% 4d MW      [%s]' % (item.ljust(10), np.sum(self[item]['data']) / 1e6, self.sources[item]))
            if item.startswith('s'):
                print('%s:% 4d 1E20/s  [%s]' % (item.ljust(10), np.sum(self[item]['data']) / 1e20, self.sources[item]))
            if item.startswith('t'):
                print('%s:% 4d N*m^2   [%s]' % (item.ljust(10), int(np.sum(self[item]['data'])), self.sources[item]))

    def to_omas(self, ods=None, time_index=0, update=['core_profiles', 'equilibrium', 'core_sources']):
        """
        translate TRANSP plasmastate file (output of TRXPL and plasmastate of SWIM) to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :update: list of IDS to update from statefile

        :return: ODS
        """
        from omas import ODS, omas_environment

        cocosio = 2  # need to confirm that indeed TRANSP plasmastate is in COCOS 2

        if ods is None:
            ods = ODS()
            # set the shot number
            ods['dataset_description.data_entry.pulse'] = self['shot_number']['data']

        # ------------------
        # Equilibrium
        # ------------------
        if 'equilibrium' in update:
            # set time array
            ods.set_time_array('equilibrium.time', time_index, self['t1']['data'])  # t0,t1,tfinal,tinit?

            # shortcut
            eq = ods['equilibrium.time_slice'][time_index]

            # define coordinate of input/output quantities
            coordsio = {'equilibrium.time_slice.%d.profiles_1d.psi' % time_index: self['psipol']['data']}

            # assign data
            with omas_environment(ods, cocosio=cocosio, coordsio=coordsio):
                eq['global_quantities.magnetic_axis.b_field_tor'] = self['B_axis_vac']['data']

                ods.set_time_array('equilibrium.vacuum_toroidal_field.b0', time_index, self['B_axis_vac']['data'])
                ods['equilibrium.vacuum_toroidal_field.r0'] = self['R_axis']['data']

                eq['global_quantities.magnetic_axis.r'] = self['R_axis']['data']
                eq['global_quantities.magnetic_axis.z'] = self['Z_axis']['data']
                eq['global_quantities.psi_axis'] = self['psipol']['data'][0]
                eq['global_quantities.psi_boundary'] = self['psipol']['data'][-1]
                eq['global_quantities.ip'] = self['curt']['data'][-1]

                eq['profiles_1d.rho_tor_norm'] = self['rho']['data']

                eq['profiles_1d.f'] = self['g_eq']['data']
                eq['profiles_1d.pressure'] = self['P_eq']['data']
                eq['profiles_1d.f_df_dpsi'] = deriv(self['psipol']['data'], self['g_eq']['data']) * self['g_eq']['data']
                eq['profiles_1d.dpressure_dpsi'] = deriv(self['psipol']['data'], self['P_eq']['data'])
                eq['profiles_1d.q'] = self['q_eq']['data']
                eq['profiles_1d.rho_tor_norm'] = self['rho']['data']

                eq['profiles_2d.0.grid_type.index'] = 1
                eq['profiles_2d.0.grid.dim1'] = self['R_grid']['data']
                eq['profiles_2d.0.grid.dim2'] = self['Z_grid']['data']
                eq['profiles_2d.0.psi'] = self['PsiRZ']['data'].T

                eq['boundary.outline.r'] = self['R_geo']['data'][:, -1]
                eq['boundary.outline.z'] = self['Z_geo']['data'][:, -1]

                eq['profiles_1d.elongation'] = self['elong']['data']
                eq['profiles_1d.triangularity_upper'] = self['triangU']['data']
                eq['profiles_1d.triangularity_lower'] = self['triangL']['data']

            # ============WALL
            ods['wall.description_2d.0.limiter.type.name'] = 'first_wall'
            ods['wall.description_2d.0.limiter.type.index'] = 0
            ods['wall.description_2d.0.limiter.type.description'] = 'first wall'
            ods['wall.description_2d.0.limiter.unit.0.outline.r'] = self['rlim']['data']
            ods['wall.description_2d.0.limiter.unit.0.outline.z'] = self['zlim']['data']

        # ------------------
        # Core profiles
        # ------------------
        if 'core_profiles' in update:
            # set time array
            ods.set_time_array('core_profiles.time', time_index, self['t1']['data'])  # t0,t1,tfinal,tinit?

            # shortcut
            prof1d = ods['core_profiles.profiles_1d.%d' % time_index]

            # define coordinate of input/output quantities
            coordsio = {
                'core_profiles.profiles_1d.%d.grid.rho_tor_norm' % time_index: self['rho']['data'][:-1] + np.diff(self['rho']['data']) / 2.0
            }

            # assign data
            with omas_environment(ods, coordsio=coordsio, cocosio=cocosio):
                ods.set_time_array('core_profiles.vacuum_toroidal_field.b0', time_index, self['B_axis_vac']['data'])
                ii = -1
                fi = -1
                bi = -1
                mi = -1
                for ks, species in enumerate(self['ALL_name']['data']):
                    species = species.strip()
                    if species == 'e':
                        prof1d['electrons.density_thermal'] = self['ns']['data'][ks, :]
                        prof1d['electrons.temperature'] = self['Ts']['data'][ks, :] * 1e3
                    else:
                        ii += 1
                        if '_fusn' in species:
                            fi += 1
                            prof1d['ion'][ii]['label'] = species.replace('_fusn', '')
                            prof1d['ion'][ii]['density_fast'] = self['nfusi']['data'][fi, :]
                            prof1d['ion'][ii]['pressure_fast_perpendicular'] = self['eperp_fusi']['data'][fi, :]
                            prof1d['ion'][ii]['pressure_fast_parallel'] = self['epll_fusi']['data'][fi, :]
                        elif '_beam' in species:
                            bi += 1
                            prof1d['ion'][ii]['label'] = species.replace('_beam', '')
                            prof1d['ion'][ii]['density_fast'] = self['nbeami']['data'][bi, :]
                            prof1d['ion'][ii]['pressure_fast_perpendicular'] = self['eperp_beami']['data'][bi, :]
                            prof1d['ion'][ii]['pressure_fast_parallel'] = self['epll_beami']['data'][bi, :]
                        elif '_mini' in species:
                            mi += 1
                            prof1d['ion'][ii]['label'] = species.replace('_mini', '')
                            prof1d['ion'][ii]['density_fast'] = self['nmini']['data'][bi, :]
                            prof1d['ion'][ii]['pressure_fast_perpendicular'] = self['eperp_mini']['data'][bi, :]
                            prof1d['ion'][ii]['pressure_fast_parallel'] = self['epll_mini']['data'][bi, :]
                        else:
                            prof1d['ion'][ii]['label'] = species
                            prof1d['ion'][ii]['density_thermal'] = self['ns']['data'][ks, :]
                            prof1d['ion'][ii]['temperature'] = self['Ts']['data'][ks, :]
                        prof1d['ion'][ii]['element'][0]['z_n'] = list(atomic_element(symbol=prof1d['ion'][ii]['label']).values())[0]['Z']
                        prof1d['ion'][ii]['element'][0]['a'] = list(atomic_element(symbol=prof1d['ion'][ii]['label']).values())[0]['A']
                        prof1d['ion'][ii]['multiple_states_flag'] = 0

            # calculate derived quantites
            ods.physics_core_profiles_pressures()
            ods.physics_core_profiles_zeff()

        # ------------------
        # Core sources
        # ------------------
        if 'core_sources' in update:

            # set time array
            ods.set_time_array('core_sources.time', time_index, self['t1']['data'])  # t0,t1,tfinal,tinit?

            def set_source(si, source_name, id_index, source_value, destination):
                # define coordinates for all sources
                coordsio = {}
                coordsio['core_profiles.profiles_1d.%d.grid.rho_tor_norm' % (time_index)] = (
                    self['rho']['data'][:-1] + np.diff(self['rho']['data']) / 2.0
                )
                coordsio['core_sources.source.%d.profiles_1d.%d.grid.rho_tor_norm' % (si, time_index)] = (
                    self['rho']['data'][:-1] + np.diff(self['rho']['data']) / 2.0
                )
                with omas_environment(ods, coordsio=coordsio, cocosio=cocosio):
                    ods['core_sources.source.%d.identifier.name' % si] = source_name
                    ods['core_sources.source.%d.identifier.index' % si] = id_index
                    source1d = ods['core_sources.source.%d.profiles_1d.%d' % (si, time_index)]
                    source1d['grid.volume'] = vol
                    source1d[destination] = source_value

            # fluxes are defined between nodes in the grid
            # volume is stored at the nodes of the grid
            # place volume info on same grid as fluxes
            vol = interp1d(self['rho']['data'], self['vol']['data'])(self['rho']['data'][:-1] + np.diff(self['rho']['data']) / 2.0)

            # assign data

            prof1d['grid.volume'] = vol

            volumetric_electron_heating_terms = {'pohme': 7, 'pbe': 2, 'peech': 3, 'pmine': 5, 'pfuse': 6}
            volumetric_ion_heating_terms = {'pbi': 2, 'picth': 5, 'pmini': 5, 'pfusi': 6}
            volumetric_electron_particles_terms = {'sbsce': 2}
            volumetric_momentum_terms = {'tq_trans': 1}

            si = -1
            # electron energy
            for source, id_index in volumetric_electron_heating_terms.items():
                if source in self:
                    si += 1
                    set_source(si, source, id_index, self[source]['data'], 'electrons.energy')

            # ion energy
            for source, id_index in volumetric_ion_heating_terms.items():
                if source in self:
                    si += 1
                    set_source(si, source, id_index, self[source]['data'], 'total_ion_energy')

            # particle ???
            for source, id_index in volumetric_electron_particles_terms.items():
                if source in self:
                    si += 1
                    set_source(si, source, id_index, self[source]['data'][0, :], 'electrons.particles')

            # momentum ???
            for source, id_index in volumetric_momentum_terms.items():
                if source in self:
                    si += 1
                    set_source(si, source, id_index, self[source]['data'], 'momentum_tor')

        return ods


class transp_out_dynamic_quantity(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __call__(self):
        return self.parent[self.name]

    def __tree_repr__(self):
        return self.name, []


class OMFITtranspOutput(OMFITdataset):
    """
    Class for dynamic serving of TRANSP output data from MDS or CDF
    """

    def __init__(self, transp_out):
        """
        :param transp_out: OMFITnc file, OMFITmds TRANSP tree, or string path to NetCDF file
        """
        if isinstance(transp_out, str):
            transp_out = OMFITnc(transp_out)
        if isinstance(transp_out, OMFITmds):
            self.type = 'MDS'
        else:
            self.type = 'CDF'
        self.transp_out = transp_out
        self.dynaLoad = True
        self._dynamic_keys = []
        OMFITdataset.__init__(self)

    @dynaLoad
    def load(self):
        if self.type == 'MDS':
            items = self.transp_out['TRANSP_OUT'].keys()
        else:
            items = self.transp_out.keys()
        items = [item for item in items if not item.startswith('_')]
        for item in items:
            self._dynamic_keys.append(item)
        if 'TIME' not in self._dynamic_keys:
            self._dynamic_keys.insert(0, 'TIME')

    def __tree_repr__(self):
        return self.type, []

    @dynaLoad
    def __tree_keys__(self):
        return np.unique(list(self.variables.keys()) + self._dynamic_keys).tolist()

    @dynaLoad
    def __getitem__(self, key):
        # return items that exist
        if key in self:
            return OMFITdataset.__getitem__(self, key)

        # return virtual items if requested so
        elif OMFITaux['virtualKeys'] and key in self._dynamic_keys:
            return transp_out_dynamic_quantity(self, key)

        # dynamically evaluate quantity
        elif key in self._dynamic_keys:
            transp_data = OMFITtranspData(self.transp_out, key)
            # 0D data
            if not len(transp_data['DIM_OF']):
                tmp = DataArray(transp_data['DATA'], coords={}, dims=())
            # 1D data
            elif len(transp_data['DIM_OF']) == 1:
                tmp = DataArray(transp_data['DATA'], coords={'TIME': transp_data['DIM_OF'][0]}, dims=('TIME',))
            # 2D data
            elif len(transp_data['DIM_OF']) == 2:
                x = transp_data['DIM_OF'][0][0]
                t = transp_data['DIM_OF'][1][:, 0]
                y = transp_data['DATA']
                tmp = DataArray(transp_data['DATA'], coords={'TIME': t, 'X': x}, dims=('TIME', 'X'))

            self[key] = tmp
        return OMFITdataset.__getitem__(self, key)

    def to_omas(self):
        # this may be of use: https://github.com/transp/transp-imas-translator/blob/master/transp2imas/transp2imas.f90
        ods = ODS()

        with omas_environment(ods, cocosio=2):  # what COCOS is TRANSP using?
            ion_species = ['D']  # what is a good way to figure out ion species?
            times = self['TIME']

            for time_index, time in enumerate(times):
                # ion-profiles
                for ion_index, ion_species in enumerate(ion_species):
                    ods['core_profiles.profiles_1d.{time_index}.ion.{ion_index}.temperature'.format(**locals())] = self['TI'][time_index, :]

                # electron-profiles
                ods['core_profiles.profiles_1d.{time_index}.electrons.density_thermal'.format(**locals())] = self['NE'][time_index, :] * 1e6
                ods['core_profiles.profiles_1d.{time_index}.electrons.temperature'.format(**locals())] = self['TE'][time_index, :]

                # equilibrium
                ods['equilibrium.time_slice.{time_index}.global_quantities.ip'.format(**locals())] = self['PCURC'][time_index]

                # wall: for the the time being, we only save limiter info at first time-slice
                #       hopefully other codes can agree this is reasonable for static walls
                if time_index == 0:
                    ods['wall.description_2d.{time_index}.limiter.type.name'.format(**locals())] = 'first_wall'
                    ods['wall.description_2d.{time_index}.limiter.type.index'.format(**locals())] = 0
                    ods['wall.description_2d.{time_index}.limiter.type.description'.format(**locals())] = 'first wall'
                    ods['wall.description_2d.{time_index}.limiter.unit.0.outline.r'.format(**locals())] = self['RLIM'][time_index, :]
                    ods['wall.description_2d.{time_index}.limiter.unit.0.outline.z'.format(**locals())] = self['YLIM'][time_index, :]

            # set the time
            ods['core_profiles.time'] = times
            ods['equilibrium.time'] = times
            ods['wall.time'] = times[:1]

            # set homogeneous time and other things
            ods.satisfy_imas_requirements()
        return ods


class OMFITfbm(OMFITnc):
    """
    Class for handling NUBEAM FBM distribution function files
    """

    def plot(self, rf=None, zf=None, cartesian=True, fig=None):
        """
        Plot distribution function

        :param rf: radial location where to show data in velocity space

        :param zf: vertical location where to show data in velocity space

        :return: figure handle
        """
        f = self['F_D_NBI']['data']
        energy = self['E_D_NBI']['data']
        pitch = self['A_D_NBI']['data']
        r2d = self['R2D']['data']
        z2d = self['Z2D']['data']
        rho = self['X2D']['data']
        theta = self['TH2D']['data']

        # Find index of our desired (R,Z)
        if rf is None or zf is None:
            idx = 0
        else:
            idx = np.argmin(np.sqrt((r2d - rf) ** 2 + np.abs(z2d - zf) ** 2))

        # Get beam ion density (#/cm^3)
        de = energy[1] - energy[0]
        dp = pitch[1] - pitch[0]
        bdens = np.sum(f, axis=(1, 2)) * 0.5 * de * dp

        # Form regular grid
        rr = np.linspace(np.min(r2d), np.max(r2d), 51)
        zr = np.linspace(np.min(z2d), np.max(z2d), 51)
        bdensr = scipy.interpolate.griddata((r2d, z2d), bdens, (rr[None, :], zr[:, None]), method='cubic')

        if fig is None:
            fig = pyplot.gcf()
        fig.suptitle(
            '{}'.format(self['TOKAMAK']['data'])
            + ' {}'.format(self['TRANSP_RUNID']['data'])
            + ' t={0:0.2f}s'.format(float(self['TIME']['data']))
        )

        ax = pyplot.subplot(1, 2, 1)
        con = ax.contourf(rr, zr, bdensr, 11)
        ax.contour(rr, zr, bdensr, 11, colors='black')
        ax.plot(r2d[idx], z2d[idx], marker='x', color='red')
        ax.set_aspect('equal')
        ax.set_title(label='Density $(cm^{-3})$')
        ax.set_xlabel('R (cm)')
        ax.set_ylabel('Z (cm)')
        fig.subplots_adjust(left=0.2)
        cax = fig.add_axes([0.05, 0.1, 0.03, 0.8])
        fig.colorbar(con, cax=cax)

        ax = pyplot.subplot(2, 2, 2)

        if not cartesian:
            t = np.arccos(np.linspace(-1, 1, len(pitch)))
            e = energy * 1e-3
            E, T = np.meshgrid(e, t)
            x = np.cos(T) * E
            y = np.sin(T) * E
            ax.contourf(x, y, f[idx, :, :], 11)
            ax.set_aspect('equal')
            ax.set_xlabel('Energy$_\\parallel$ (keV)')
            ax.set_ylabel('Energy$_\\perp$ (keV)')
        else:
            ax.contourf(energy * 1e-3, pitch, f[idx, :, :], 11)
            ax.set_ylim(-1, 1)
            ax.set_xlabel('Energy (keV)')
            ax.set_ylabel('Pitch $V_{||}/V$')
        ax.set_title('$f_b(E,\\xi)$' + ' R={0:0.1f}, Z={1:0.1f}'.format(r2d[idx], z2d[idx]))

        ax = pyplot.subplot(2, 2, 4)
        ax.scatter(rho, bdens * 1e-13, c=theta, alpha=0.25, label='$n_b(\\theta) [10^{19}m^{-3}]$')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, np.max(bdens) * 1e-13])
        ax.set_xlabel('$\\rho$')
        ax.legend()

        return fig

    def plot_energy_space(self, rmin, rmax, zmin, zmax, emin=0 * 1e3, emax=1000 * 1e3, cartesian=True, ax=None):
        """
        Average distribution function over a specified R,Z and plot energy versus pitch

        :param rmin: minimum R to average over

        :param rmax: maximum R to average over

        :param zmin: minimum Z to average over

        :param zmax: maximum Z to average over

        :param emin: minimum energy to average over

        :param emax: maximum energy to average over

        :param cartesian: plot in energy/pitch space or E_\\parallel and E_\\perp

        :param ax: axes
        """

        f = self['F_D_NBI']['data']
        R = self['R2D']['data']
        Z = self['Z2D']['data']
        energy = self['E_D_NBI']['data']
        pitch = self['A_D_NBI']['data']

        emini = np.argmin(abs(energy - emin))
        emaxi = np.argmin(abs(energy - emax))

        total_f = np.zeros((f.shape[1], f.shape[2]))

        k = 0
        for i, r in enumerate(R):
            if r <= rmax and r >= rmin:
                if Z[i] <= zmax and Z[i] >= zmin:
                    total_f[:, :] += f[i, :, :]
                    k += 1

        levels = [
            np.amin(total_f[:, emini:emaxi] / k),
            np.amax(total_f[:, emini:emaxi] / k) / 40,
            np.amax(total_f[:, emini:emaxi] / k) / 20,
            np.amax(total_f[:, emini:emaxi] / k) / 10,
            np.amax(total_f[:, emini:emaxi] / k) / 4,
            np.amax(total_f[:, emini:emaxi] / k) / 3,
            np.amax(total_f[:, emini:emaxi] / k) / 2,
            np.amax(total_f[:, emini:emaxi] / k) / 1.5,
            np.amax(total_f[:, emini:emaxi] / k) / 1.25,
            np.amax(total_f[:, emini:emaxi] / k) / 1.2,
            np.amax(total_f[:, emini:emaxi] / k) / 1.1,
            np.amax(total_f[:, emini:emaxi] / k) / 1.05,
            np.amax(total_f[:, emini:emaxi] / k),
        ]

        if ax is None:
            ax = pyplot.gca()

        if not cartesian:
            t = np.arccos(np.linspace(-1, 1, len(pitch)))
            e = energy[emini:emaxi] * 1e-3
            E, T = np.meshgrid(e, t)
            x = np.cos(T) * E
            y = np.sin(T) * E
            ax.contourf(x, y, total_f[:, emini:emaxi] / k, levels=levels)
            ax.contour(x, y, total_f[:, emini:emaxi] / k, levels=levels)
            ax.set_aspect('equal')
            ax.set_xlabel('Energy$_\\parallel$ (keV)')
            ax.set_ylabel('Energy$_\\perp$ (keV)')
        else:
            ax.contourf(energy[emini:emaxi] * 1e-3, pitch, total_f[:, emini:emaxi] / k, levels=levels)
            ax.set_ylim(-1, 1)
            ax.set_xlim(10, 100)
            ax.set_xlabel('Energy (keV)')
            ax.set_ylabel('Pitch $V_\\parallel/V$')
        ax.set_title(
            'D3D $f_b(E,\\xi)$ '
            + ' {0} Rmin={1:0.1f}, Rmax={2:0.1f}, \nZmin={3:0.1f}, Zmax={4:0.1f}, average over {5} points'.format(
                self['TRANSP_RUNID']['data'], rmin, rmax, zmin, zmax, k
            )
        )
        return ax

    def to_omas(self, ods=None, time_index=0):
        """
        Save NUBEAM distribution function to OMAS

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :return: updated ODS
        """
        if ods is None:
            ods = ODS()

        # shortcut
        ggd = ods[f'distributions.distribution[{time_index}].ggd[0]']

        # assign grid spaces for different spatial coordinates
        for s, (item, name, coordinates_type, norm) in enumerate(
            [
                ('R2D', 'r', 1, 0.01),  # r [cm-->m]
                ('Z2D', 'z', 2, 0.01),  # z [cm-->m]
                ('X2D', 'rho', 12, 1.0),  # rho [-]
                ('TH2D', 'theta', 22, 1.0),  # theta [rad]
            ]
        ):
            # standard or fourier data
            ggd[f'grid.space[{s}].geometry_type.index'] = 0  # 0: standard, 1:Fourier
            ggd[f'grid.space[{s}].geometry_type.name'] = name + '_pitch_energy'
            ggd[f'grid.space[{s}].coordinates_type'] = [coordinates_type, 403, 301]
            ggd[f'grid.space[{s}].objects_per_dimension[0].object[0].geometry'] = self[item]['data'] * norm
            ggd[f'grid.space[{s}].objects_per_dimension[0].object[1].geometry'] = self['A_D_NBI']['data']  # pitch v_parallel/v [-]
            ggd[f'grid.space[{s}].objects_per_dimension[0].object[2].geometry'] = self['E_D_NBI']['data'] * 1e3  # energy [kev --> ev]

        # assign the distribution function data itself
        ggd[f'expansion[0].grid_subset[0].values'] = self['F_D_NBI']['data'].flatten()

        return ods


################################################# Basic Data Manipulation in TRANSP


def vint(d, dvol=None):
    """
    Volume integrate a TRANSP OMFITmdsValue object.
    Currently only available for objects from the TRANSP tree.

    :param d: OMFITtranspData object from the mds+ TRANSP OUTPUTS.TWO_D tree.
    :type d: OMFITtranspData

    :param dvol: OMFITtranspData object 'dvol' from the mds TRANSP tree.
        If None, will be taken from Data's MDStree.
    :type dvol: OMFITtranspData or None

    **Example:**
    Assuming the root is an OMFIT TRANSP module with a loaded run.
    >> mvisc = OMFITtranspData(root['OUTPUTS']['TRANSP_OUTPUT'],'MVISC')
    >> tvisc = vint(mvisc)
    >> tvisc['DATA'][0,-1] # total viscous torque at first time step in Nm
    2.0986965
    >> mvisc2 = vder(tvisc)
    >> np.all(np.isclose(mvisc2['DATA'][0,:],mvisc['DATA'][0,:]))
    True

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = vint(v, dvol)
        return dnew

    if dvol == None:
        if 'DVOL' in d:
            dvol = d['DVOL']
        elif 'MDS' in d:
            dvol = d['MDS']['OUTPUTS']['TWO_D']['DVOL']
        else:
            dvol = OMFITmdsValue(d.server, d.treename, d.shot, TDI='DVOL')
    elif isinstance(dvol, OMFITmdsValue):
        dvol = OMFITtranspData(dvol)
    # if type(d)==OMFITmdsValue:
    #    d = OMFITtranspData(d)
    dvol = set_grid(dvol, 'X')  # just in case it was changed and given
    dint = set_grid(d, 'XB')
    ddv = set_grid(d, 'X')['DATA'] * dvol['DATA']
    dint['DATA'] = np.cumsum(ddv, axis=1)

    # clean up metadata
    dint['LABEL'] = 'int({:},dV)'.format(dint['LABEL'])
    dint['RPLABEL'] = dint['RPLABEL'].replace('DENSITY', '')
    dint['UNITS'] = dint['UNITS'] + '*CM**3'
    dint['UNITS'] = dint['UNITS'].replace('/CM3*CM**3', '')  # TRANSP conventions
    dint['UNITS'] = dint['UNITS'].replace('/Cm3*CM**3', '')  # TRANSP conventions
    dint['UNITS'] = dint['UNITS'].replace('/CM3/SEC*CM**3', '/SEC')  # TRANSP conventions

    return dint


OMFITtranspData.vint = vint
OMFITtranspMultigraph.vint = vint


def vder(d, dvol=None):
    """
    Derivative with respect to volume for TRANSP variables consistent with
    TRANSP finite differencing methods.

    See Solomon's unvolint.pro

    :param d: OMFITtranspData object from the mds+ TRANSP tree.
    :type d: OMFITtranspData
    :param dvol: OMFITtranspData object 'dvol' from the mds TRANSP tree.
        If None, will be taken from the Data's MDStree.
    :type dvol: OMFITtranspData or None

    :return: dy/dV OMFITtransData object on zone-centered grid.

    **Example:**
    Assuming the root is an OMFIT TRANSP module with a loaded run.
    >> mvisc = OMFITtranspData(root['OUTPUTS']['TRANSP_OUTPUT'],'MVISC')
    >> tvisc = vint(mvisc)
    >> tvisc['DATA'][0,-1] # total viscous torque at first time step in Nm
    2.0986965
    >> mvisc2 = vder(tvisc)
    >> np.all(np.isclose(mvisc2['DATA'][0,:],mvisc['DATA'][0,:]))
    True

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = vder(v, dvol)
        return dnew

    if dvol == None:
        dvol = d['DVOL']
    elif isinstance(dvol, OMFITmdsValue):
        dvol = OMFITtranspData(dvol)
    if isinstance(d, OMFITmdsValue):
        d = OMFITtranspData(d)
    dvol = set_grid(dvol, 'X')  # just in case it was changed and given
    dder = set_grid(d, 'X')
    y = set_grid(d, 'XB')['DATA']
    y = np.hstack([np.zeros([len(dder['DIM_OF'][1]), 1]), y])
    dder['DATA'] = np.diff(y, axis=1) / dvol['DATA']

    # clean up metadata
    dder['LABEL'] = 'd{:}/dV)'.format(dder['LABEL'])
    dder['UNITS'] = dder['UNITS'] + '/CM**3'
    dder['UNITS'] = dder['UNITS'].replace('CM3/CM**3', '')  # TRANSP conventions
    dder['UNITS'] = dder['UNITS'].replace('Cm3/CM**3', '')  # TRANSP conventions

    return dder


OMFITtranspData.vder = vder
OMFITtranspMultigraph.vder = vder


def sint(d, darea=None):
    """
    Surface integrate a TRANSP OMFITmdsValue object.
    Currently only available for objects from the TRANSP tree.

    :param d: OMFITtranspData object from the mds+ TRANSP OUTPUTS.TWO_D tree.
    :type d: OMFITtranspData

    :param darea: OMFITtranspData object 'darea' from the mds TRANSP tree.
        If None, will be taken from Data's MDStree.
    :type darea: OMFITtranspData or None

    **Example:**

    mds = OMFITmds('DIII-D','transp',1633030101)
    cur = OMFITtranspData(mds,'CUR')
    da = OMFITtranspData(mds,'DAREA')
    curi = cur.sint(darea=da)
    print(curi['DATA'][0,-1])
    pcur = OMFITtranspData(mds,'PCUR')
    print(pcur['DATA'][0])
    -> 1.16626e+06
    -> 1.16626e+06

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = sint(v, darea)
        return dnew

    if darea == None:
        if 'DAREA' in d:
            darea = d['DAREA']
        elif 'MDS' in d:
            darea = d['MDS']['OUTPUTS']['TWO_D']['DAREA']
        else:
            darea = OMFITmdsValue(d.server, d.treename, d.shot, TDI='DAREA')
    elif isinstance(darea, OMFITmdsValue):
        darea = OMFITtranspData(darea)
    # if type(d)==OMFITmdsValue:
    #    d = OMFITtranspData(d)
    darea = set_grid(darea, 'X')  # just in case it was changed and given
    dint = set_grid(d, 'XB')
    dda = set_grid(d, 'X')['DATA'] * darea['DATA']
    dint['DATA'] = np.cumsum(dda, axis=1)

    # clean up metadata
    dint['LABEL'] = 'int({:},dA)'.format(dint['LABEL'])
    dint['RPLABEL'] = dint['RPLABEL'].replace('DENSITY', '')
    dint['UNITS'] = dint['UNITS'] + '*CM**2'
    dint['UNITS'] = dint['UNITS'].replace('/CM2*CM**2', '')  # TRANSP conventions
    dint['UNITS'] = dint['UNITS'].replace('/Cm2*CM**2', '')  # TRANSP conventions

    return dint


OMFITtranspData.sint = sint
OMFITtranspMultigraph.sint = sint


def set_grid(d, zone='X', dvol=None):
    """
    Interpolate 2D TRANSP data to rho grid zone-boundary or zone-centered values.

    :param d: OMFITtranspData object from the mds+ TRANSP tree.

    :param zone: ``'XB'`` for zone-boundary rho, ``'X'`` for zone-centered. ``'V'`` or ``'VB'`` for volume.
    :type zone: str
    :param dvol: OMFITtranspData object 'dvol' from the mds+ TRANSP tree.
            If None, will be taken from Data's MDStree.

    return: OMFITtranspData object on the specified rho grid

    **Example:**
    Assuming the root is an OMFIT TRANSP module with a loaded run.
    >> mvisc = OMFITtranspData(root['OUTPUTS']['TRANSP_OUTPUT'],'MVISC')
    >> mvisc['XAXIS']
    'X'
    >> print(mvisc['DIM_OF'][0][:3])
    [ 0.01  0.03  0.05]
    >> mviscb = set_grid(mvisc,'XB')
    >> mviscb['XAXIS']
    'XB'
    >> print(mviscb['DIM_OF'][0][:3])
    [ 0.02  0.04  0.06]

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = set_grid(v, zone, dvol)
        return dnew

    if dvol == None and 'V' in zone:
        dvol = d['DVOL']
    elif isinstance(dvol, OMFITmdsValue):
        dvol = OMFITtranspData(dvol)
    if isinstance(d, OMFITmdsValue):
        d = OMFITtranspData(d)
    zone = zone.upper()
    db = copy.copy(d)

    # return a copy if no change
    if d['XAXIS'] == zone:
        return db

    # native transp rho grid center or boundary
    if zone in ['X', 'XB']:
        if 'MDS' in d:
            xnew = d['MDS']['TRANSP_OUT'][zone].data()
        else:
            xnew = d['CDF'][zone]['data']
        y = d['DATA']  # .ravel()
        x = d['DIM_OF'][0][0, :]  # .ravel()
        t = d['DIM_OF'][1][:, 0]  # .ravel()
        # f = LinearNDInterpolator(zip(x,t),y)
        # db['DATA'] = f(zip(xnew.ravel(),t.ravel())).reshape(t.shape)
        f = RectBivariateSpline(x, t, y.T)  # assume regular grid
        db['DATA'] = f(xnew[0, :], t).T
        db['DIM_OF'][0] = xnew
    # volume grid center or boundary for easy integration of densities
    elif zone in ['V', 'VB']:
        db = set_grid(d, zone.replace('V', 'X'))
        v = set_grid(xint(dvol), zone.replace('V', 'X'))
        db['DIM_OF'][0] = v['DATA']
    else:
        raise ValueError('Valid zones are "X", "XB", "V", or "VB".')
    db['XAXIS'] = zone
    return db


OMFITtranspData.set_grid = set_grid
OMFITtranspMultigraph.set_grid = set_grid


def xdiff(d):
    """
    TRANSP convention of simple finite difference along rho (axis=0), including
    switching of centered/boundary grids.

    :param d: OMFITtranspData object from the mds+ TRANSP tree.

    :return: OMFITtranspData differenced on the other rho grid (``'X'`` vs ``'XB'``)

    **Example:**

    >> x = Data(['x','TRANSP'],1470670204)
    >> dx = xdiff(x)
    >> print(dx['XAXIS'])
    XB
    >> print(dx.y[0,:3])
    [ 0.02  0.02  0.02]

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = xdiff(v)
        return dnew

    ddiff = copy.copy(d)
    # extend axis by 1 (back of forward)
    tn = list(d['DIM_OF'][1].T)
    tn.insert(0, d['DIM_OF'][1][:, 0])
    xn = list(d['DIM_OF'][0].T)
    if d['XAXIS'] == 'X':
        xn.insert(len(xn), xn[-1] + (xn[-1] - xn[-2]))
        ddiff = set_grid(ddiff, 'XB')
    elif d['XAXIS'] == 'XB':
        xn.insert(0, xn[0] - (xn[1] - xn[0]))
        ddiff = set_grid(ddiff, 'X')
    else:
        raise ValueError('Data object must have xaxis attribute "X" or "XB"')
    # data on extended axis
    y = d['DATA'].ravel()
    x = d['DIM_OF'][0].ravel()
    t = d['DIM_OF'][1].ravel()
    fl = LinearNDInterpolator(list(zip(x, t)), y)
    fn = NearestNDInterpolator(list(zip(x, t)), y)
    dn = fl(list(zip(np.array(xn).ravel(), np.array(tn).ravel()))).reshape(np.shape(xn))
    dn[np.isnan(dn)] = fn(list(zip(np.array(xn)[np.isnan(dn)].ravel(), np.array(tn)[np.isnan(dn)].ravel())))
    # simple finite differences
    dy = np.diff(dn, axis=0).T
    # new data
    ddiff['DATA'] = dy
    # clean up metadata
    ddiff['LABEL'] = 'd({:})'.format(d['LABEL'])
    ddiff['RPLABEL'] = 'Delta {:})'.format(d['RPLABEL'])

    return ddiff


OMFITtranspData.xdiff = xdiff
OMFITtranspMultigraph.xdiff = xdiff


def xder(d):
    """
    TRANSP style differentiation in rho.

    :param d: OMFITtranspData object from the TRANSP tree.

    :return: dy/drho OMFITtranspData object on the other rho grid.

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = xder(v)
        return dnew

    dx = xdiff(OMFITtranspData(d['MDS'], d['XAXIS']))
    dder = xdiff(d)
    dder['DATA'] /= dx['DATA']

    # clean up metadata
    dder['LABEL'] = '{:}/drho'.format(dder['LABEL'])

    return dder


OMFITtranspData.xder = xder
OMFITtranspMultigraph.xder = xder


def xint(d):
    """
    TRANSP style integration in rho. UNVALIDATED.

    :param d: OMFITtranspData object from the TRANSP tree.

    :return: dy/drho OMFITtranspData object on the other rho grid.

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = xint(v)
        return dnew

    dint = copy.copy(d)
    dint['DATA'] = integrate.cumtrapz(dint['DATA'], x=dint['DIM_OF'][0], axis=1, initial=0)

    # clean up metadata
    dint['LABEL'] = 'int({:},drho)'.format(dint['LABEL'])

    return dint


OMFITtranspData.xint = xint
OMFITtranspMultigraph.xint = xint


def aol(d, rmnmp=None):
    """
    Normalized inverse scale length a/Lx with derivative with respect to
    midplane minor radius "r".  The equation is aol = -(a/X)dX/dr

    :param d: OMFITtranspData object from the TRANSP tree.
    :param rmnmp: OMFITtranspData "RMNMP"

    :return:

    """
    if isinstance(d, OMFITtranspMultigraph):
        dnew = copy.copy(d)
        for k, v in list(dnew['CONTENT'].items()):
            dnew['CONTENT'][k] = aol(v, rmnmp)
        return dnew

    if rmnmp == None:
        if 'RMNMP' in d:
            rmnmp = d['RMNMP']
        elif 'MDS' in d:
            rmnmp = d['MDS']['OUTPUTS']['TWO_D']['RMNMP']
        else:
            rmnmp = OMFITmdsValue(d.server, d.treename, d.shot, TDI='RMNMP')
    elif isinstance(rmnmp, OMFITmdsValue):
        rmnmp = OMFITtranspData(rmnmp)

    a = rmnmp['DATA'][:, -1]
    dr = np.zeros(d['DATA'].shape)
    for i in range(d['DATA'].shape[0]):
        dr[i, :] = deriv(rmnmp['DATA'][i, :], d['DATA'][i, :])
    dder = copy.copy(d)
    dder['DATA'] = -1.0 * (a[:, np.newaxis] / d['DATA']) * dr

    # clean up metadata
    dder['LABEL'] = 'a/L_{:})'.format(dder['LABEL'])
    dder['UNITS'] = '-'
    return dder


OMFITtranspData.aol = aol
OMFITtranspMultigraph.aol = aol


def tavg(d, time=None, avgtime=None):
    """
    Time average data

    :param d: OMFITtranspData object from the TRANSP tree.
    :param time: Center time in seconds
    :param avgtime: Averaging window (+/-) in seconds

    :return: For 1D input uncertainty uarray of the data time avarge and standard deviation.
             For 2D input uncertainty uarray of the profile with time avarge and standard deviation.

    **Example:**
    Assuming data in root['OUTPUTS']['TRANSP_OUTPUT']

    time = 2.0
    avgtime = 0.1
    # 1D
    tr_neutt = OMFITtranspData(root['OUTPUTS']['TRANSP_OUTPUT'], 'NEUTT')
    tr_neutt_tavg = tr_neutt.tavg(time=time, avgtime=avgtime)
    tr_neutt.plot()
    ax = gca()
    uband([time-avgtime, time+avgtime],np.repeat(tr_neutt_tavg,2),ax=ax)
    ax.text(time,nominal_values(tr_neutt_tavg)+std_devs(tr_neutt_tavg),
            '{0:0.3g}+/-{1:0.3g}'.format(nominal_values(tr_neutt_tavg),std_devs(tr_neutt_tavg)))

    # 2D
    tr_ne = OMFITtranspData(root['OUTPUTS']['TRANSP_OUTPUT'],'NE')
    tr_ne_tavg = tr_ne.tavg(time=time, avgtime=avgtime)
    figure()
    tr_ne.plot(slice_axis=1,slice_at=time)
    ax = gca()
    uband(tr_ne['DIM_OF'][0][0,:],tr_ne_tavg,ax=ax)

    """

    if time is None or avgtime is None:
        raise (OMFITexception("Must set time and average time"))

    # Determine if 1D or 2D data
    if len(d['DIM_OF']) == 1 and d['UNITS_DIM_OF'][0] == 's':
        # 1D
        idx = np.where((d['DIM_OF'][0] >= time - avgtime) * (d['DIM_OF'][0] <= time + avgtime))[0]
        if len(idx):
            ud = uarray(np.mean(d['DATA'][idx]), np.std(d['DATA'][idx]))
        else:
            raise (OMFITexception("Averaging window empty."))
    elif len(d['DIM_OF']) == 2 and d['UNITS_DIM_OF'][1] == 's':
        # 2D
        idx = np.where((d['DIM_OF'][1][:, 0] >= time - avgtime) * (d['DIM_OF'][1][:, 0] <= time + avgtime))[0]
        if len(idx):
            ud = uarray(np.mean(d['DATA'][idx, :], axis=0), np.std(d['DATA'][idx, :], axis=0))
        else:
            raise (OMFITexception("Averaging window empty."))
    else:
        raise (OMFITexception("Unrecognized dimensions of quantity to average."))

    return ud


OMFITtranspData.tavg = tavg


############################################
if '__main__' == __name__:
    test_classes_main_header()

    # This is not a real TRANSP output file, but the class should be able to finish __init__() with any .nc sample.
    # This is just a limited initialization test, not a detailed test of all class features.
    test_nc_file = os.sep.join([OMFITsrc, '..', 'samples', 'bmn.nc'])
    class_instance = OMFITtranspOutput(test_nc_file)
    class_instance.load()
