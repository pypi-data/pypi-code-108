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


from omfit_classes.omfit_mds import OMFITmdsValue

from matplotlib import pyplot
from matplotlib.widgets import MultiCursor
import numpy as np

__all__ = ['DI_signal', 'DI_DTS_signal', 'DI_file_signal', 'DI_LP_signal', 'DI_GW_signal', 'DI_asdex_signal']


class BadOrMissingDataError(ValueError, doNotReportException):
    """Couldn't find/use data necessary to back one of the signal requests"""


class DI_signal(SortedDict):
    """
    Principal data class used by _Detachment_Indicator.

    Data is fetched as a MDS+ pointname, truncated, ELM filtered, smoothed and remapped to an independent
    variable. See below for inherited objects with specific implementation needs (eg langmuir probes, DTS ...)
    """

    def __init__(self, tag):
        """
        :param tag: string
            a keyword name for this signal. Eg. pointname of MDS+ siganl
        """
        self['tag'] = tag
        self['derived'] = False

    def fetch(self, shotnumber, device):
        """
        Fetch data from MDS+

        :param shotnumber: int
            Shot identifier

        :pram device: string
            Device name, to be used as server name in creation of MDS+ connection
        """

        self['shotnumber'] = shotnumber
        self['device'] = device

        mdsval = OMFITmdsValue(server=device, shot=shotnumber, TDI=self['tag'])
        if not mdsval.check():
            raise BadOrMissingDataError(f"Could not find signal {self['tag']} data for {device}#{shotnumber}")

        self['RAW'] = SortedDict()
        self['RAW']['times'] = mdsval.dim_of(0)  # ms
        self['RAW']['data'] = mdsval.data()
        self['RAW']['units'] = mdsval.units()

    def truncate_times(self, time_range):
        """
        Trim the dataset down by removing values. Helps with speed and to avoid out-of-bounds interpolation errors

        :param time_range: list
            Min and max times for truncation [min, max]
        """

        if time_range is None:
            # Do not truncate
            self['RAW_TRIM'] = SortedDict()
            self['RAW_TRIM']['times'] = self['RAW']['times']
            self['RAW_TRIM']['data'] = self['RAW']['data']
            self['RAW_TRIM']['units'] = self['RAW']['units']
        else:
            tmin_loc = np.argmin(abs(self['RAW']['times'] - time_range[0]))
            tmax_loc = np.argmin(abs(self['RAW']['times'] - time_range[1]))

            self['RAW_TRIM'] = SortedDict()
            self['RAW_TRIM']['times'] = self['RAW']['times'][tmin_loc:tmax_loc]
            self['RAW_TRIM']['data'] = self['RAW']['data'][tmin_loc:tmax_loc]
            self['RAW_TRIM']['units'] = self['RAW']['units']

    def ELM_filter(self, elm_obj, filter_settings):
        """
        Requires that trimmed data already exists.

        :param elm_obj: omfit_elm instance
        A DI_signal doesn't need to know the details of the ELM identification that is identified
        globally for a shot and then shared out to a variety of signals/diagnostics for processing.
        As such, the ELM filtering is done here using a pre-defined omfit_elm object.

        :param filter_settings: Dict
         dict containing the values to be passed to ELM filtering. See OMFITelm for specification
        """

        self['settings_ELM_filter'] = filter_settings  # set a record of what was used
        times_to_filter = self['RAW_TRIM']['times']
        vals = self['RAW_TRIM']['data']
        stimes = np.ones(np.shape(times_to_filter)) * filter_settings['s_time']
        elm_obj.set_filter_params(filter_settings)
        elm_okay = elm_obj(times_to_filter, stimes=stimes)

        self['FILTERED'] = SortedDict()
        self['FILTERED']['times'] = times_to_filter[elm_okay]
        self['FILTERED']['data'] = vals[elm_okay]
        self['FILTERED']['units'] = self['RAW_TRIM']['units']

    def smooth(self, smooth_settings):
        """
        Smooth the filtered data using some kind

        :param smooth_settings" Dict
            A dict of settings as required for the particular kinds of smoothing requested in smooth_settings['smoothtype']
        """
        self['settings_smoothing'] = smooth_settings  # set a record of what was done

        if smooth_settings['smoothtype'] == 'savgol':
            times = self['FILTERED']['times']
            data = scipy.signal.savgol_filter(
                self['FILTERED']['data'], smooth_settings['window_length'], smooth_settings['polyorder'], mode='nearest'
            )

        elif smooth_settings['smoothtype'] == 'median+savgol':
            times = self['FILTERED']['times']
            data_med = scipy.signal.medfilt(self['FILTERED']['data'], smooth_settings['median_length'])
            data = scipy.signal.savgol_filter(data_med, smooth_settings['window_length'], smooth_settings['polyorder'], mode='nearest')

        self['SMOOTHED'] = SortedDict()
        self['SMOOTHED']['times'] = times
        self['SMOOTHED']['data'] = data
        self['SMOOTHED']['units'] = self['FILTERED']['units']

    def remap(self, remap_signal):
        """
        Remap the signal onto an independent variable, which itself is an DI_signal instance
        """
        remap_fun = interp1d(remap_signal['SMOOTHED']['times'], remap_signal['SMOOTHED']['data'], bounds_error=False)
        xdata = remap_fun(self['SMOOTHED']['times'])
        ydata = self['SMOOTHED']['data']

        self['REMAPPED'] = SortedDict()
        self['REMAPPED']['xname'] = remap_signal['tag']
        self['REMAPPED']['xunits'] = remap_signal['SMOOTHED']['units']
        self['REMAPPED']['xdata'] = xdata
        self['REMAPPED']['data'] = ydata
        self['REMAPPED']['units'] = self['SMOOTHED']['units']

    def __call__(self):
        self.plot()

    def plot(self):
        """
        A basic plotting function of the available datatypes.
        """

        pyplot.figure()
        try:
            pyplot.plot(self['RAW']['times'], self['RAW']['data'], color='#87CEFF', label='RAW')
        except Exception:
            print(self['tag'] + ': raw data not available')
        try:
            pyplot.plot(self['RAW_TRIM']['times'], self['RAW_TRIM']['data'], color='#4A708B', label='RAW_TRIM')
        except Exception:
            print(self['tag'] + ': trimmed data not available')
        try:
            pyplot.plot(self['FILTERED']['times'], self['FILTERED']['data'], '+', color='black', label='FILTERED')
        except Exception:
            print(self['tag'] + ': filtered data not available')
        try:
            pyplot.plot(self['SMOOTHED']['times'], self['SMOOTHED']['data'], color='red', label='SMOOTHED')
        except Exception:
            print(self['tag'] + ': smoothed data not available')
        try:
            pyplot.xlim([np.min(self['RAW_TRIM']['times']) * 0.9, np.max(self['RAW_TRIM']['times']) * 1.05])
        except Exception:
            pass
        pyplot.xlabel('Time [ms]')
        pyplot.ylabel(self['RAW']['units'])
        pyplot.title(self['tag'])
        ax = pyplot.gca()
        ax.ticklabel_format(useOffset=False)
        ax.get_xaxis().get_major_formatter().set_scientific(False)
        pyplot.text(1.01, 0.97, self['shotnumber'], rotation=90, transform=ax.transAxes, fontsize=9)
        pyplot.legend(loc='best').draggable(True)
        pyplot.tight_layout()
        pyplot.show(block=False)

    def plot_elm_check(self, xrange=None):

        if xrange is None:
            xrange = [np.min(self['RAW_TRIM']['times']) * 0.9, np.max(self['RAW_TRIM']['times']) * 1.05]

        fig = pyplot.figure()
        ax1 = pyplot.subplot(3, 1, 1)
        ax2 = pyplot.subplot(3, 1, 2, sharex=ax1)

        elm_obj = self['elm_obj']
        elm_obj.elm_detection_plot(
            time_zoom=xrange, crop_data_to_zoom_range=False, show_more_timing=False, show_details=False, fig=fig, axs=[ax1, ax2]
        )
        ax3 = pyplot.subplot(3, 1, 3, sharex=ax1)
        pyplot.plot(self['RAW']['times'], self['RAW']['data'], color='#87CEFF')
        pyplot.plot(self['RAW_TRIM']['times'], self['RAW_TRIM']['data'], color='#4A708B')
        pyplot.plot(self['FILTERED']['times'], self['FILTERED']['data'], '+', color='black')
        pyplot.gcf().multi = MultiCursor(pyplot.gcf().canvas, [ax1, ax2, ax3], color='r', lw=1)
        pyplot.xlabel('Time [ms]')
        pyplot.title(self['tag'])
        pyplot.ylabel(self['RAW']['units'])
        pyplot.tight_layout()


class BadThomsonDataError(BadOrMissingDataError):
    """(Divertor) Thomson Scattering (TS or DTS) data for this shot or channel are unavailable."""


class DI_DTS_signal(DI_signal):
    """
    DTS specific methods. Nothing fancy here, just a parsing of the DTS arrays stored in MDS+. It can't be done
    with DI_signal as the MDS+ arrays are 2D.
    """

    def __init__(self, tag):
        """
        Initialization.

        :param tag: string
        Reference name for quantity. This will be in the form DTS_x_y where x is the quantity (eg DENS, TEMP)
        and y is the channel (eg 0 for the channel closest to the plate). Eg 'DTS_TEMP_0'. Case independent.
        """
        DI_signal.__init__(self, tag)

        _, param, channel = tag.split('_')
        self['tag'] = tag

        if param.lower() == 'dens':
            self['parameter'] = 'ne'
        elif param.lower() == 'temp':
            self['parameter'] = 'te'
        self['chordnumber'] = int(channel)
        self['derived'] = False

    def fetch(self, shotnumber, device):
        """
        Fetch data from MDS+ and split up to find requested quantity on requested channel.

        :param shotnumber: integer
        Shotnumber for data fetch

        :param device:
        Server name for MDS+ data fetch. eg 'DIII-D'
        """
        self['shotnumber'] = shotnumber
        self['device'] = device

        self['RAW'] = SortedDict()

        mdsval = OMFITmdsValue(server=device, shot=shotnumber, TDI="ts" + self['parameter'] + '_div')
        if not mdsval.check():
            raise BadThomsonDataError(f"Could not find any DTS {self['parameter']} data for {device}#{shotnumber}")
        n_dts_ch = len(mdsval.data()[:, 0])
        if self['chordnumber'] >= n_dts_ch:
            raise BadDivThomsonData(
                f"DTS channel index {self['chordnumber']} was requested, "
                f"but the DTS data for {device}#{shotnumber} only cover channels 0-{n_dts_ch}"
            )

        self['RAW']['times'] = mdsval.dim_of(0)  # ms
        self['RAW']['data'] = mdsval.data()[self['chordnumber'], :]

        if self['parameter'] == 'te':
            self['RAW']['data'][self['RAW']['data'] == 0] = np.nan  # indicates bad fit
            self['RAW']['data'][self['RAW']['data'] > 1e3] = np.nan  # not physical and very unhelpful

        if self['parameter'] == 'te':
            self['RAW']['units'] = 'eV'
        elif self['parameter'] == 'ne':
            self['RAW']['units'] = 'm**3'


class DI_file_signal(DI_signal):
    """
    A convenient way to make a DI_signal object when the times and values are coming from file. For example
    a custom-read of some data from an IDL save file. In these cases, it is sometimes easier just to
    pass the raw data straight to the object and then it will be able to handle the filtering, remapping etc. in
    a way that is equivalent to the other diagnostics.
    """

    def __init__(self, tag):
        """
        Initialize DI object with tag as specified.
        :param tag: string
        Tag name for signal, used for identification purposes
        """
        DI_signal.__init__(self, tag)
        self['tag'] = tag

    def fetch(self, shotnumber, times, data, units=''):
        """
        No fetching actually occurs for this subclass. In this case, the otherwise-sourced data is
        simply placed into the attributes that are required by the processing methods in DI_signal.

        :param shotnumber: int
        Shotnumber for reference purposes

        :param times: array-like
        List of times corresponding to data [ms].

        :param data: array-like
        The actual data, 1D array.

        :param units: string
        Description of the units of data.
        """
        self['shotnumber'] = shotnumber
        self['RAW'] = SortedDict()
        self['RAW']['times'] = times  # ms
        self['RAW']['data'] = data
        self['RAW']['units'] = units


class DI_LP_signal(DI_signal):
    """
    Langmuir probe specific methods. Interacts with the Langmuir_Probes module.
    """

    def __init__(self, tag):
        """
        :param tag: string
        reference name for the signal
        """
        DI_signal.__init__(self, tag)

        self['tag'] = tag
        self['derived'] = False

    def fetch(self, shotnumber, probe_tree, param_name, units, processing_settings=None):
        """
        This subclass can't know anything about where the LP data is being saved in the tree. It can however operate
        on one of the probe sub trees. That means the Langmuir_Probe module tree needs to be populated first,
        and then one of the sub trees from its ['OUTPUT'] can be passed into here, alongside the physical quantity
        to be extracted from the tree.

        :param probe_tree: OMFITTree
        a subtree of the Langmuir_Probe module corresponding

        :param param_name: string
        The name of the physical parameter to be extracted from probe tree (eg. JSAT, DENS, or TEMP).

        :param units: OMFITTree
        Descriptors of the units for each of the param_name options. This often lives
        in Langmuir_Toolbox['OUTPUTS']['LP_MDS']['units']

        :param processing_settings: Dict
        settings dict containing filter_settings, smoothing_settings, DOD_tmin, DOD_tmax. See process_data.py
        for full details.
        """

        self['shotnumber'] = shotnumber

        self['RAW'] = SortedDict()
        self['RAW']['times'] = probe_tree['time']
        self['RAW']['data'] = probe_tree[param_name]
        self['RAW']['units'] = units[param_name]


class DI_DOD_signal(DI_signal):
    """
    Derived quantity: Calculate degree of detachment (DOD).
    The process is that jsat for a single probe is calculated as a function of the line averaged density.
    A n**2 fit is then calculated in a time range that should be just the well attached portion of the discharge.
    After the JSAT rollover, JSAT will deviate from the n**2 scaling and the ratio of this scaling to JSAT is
    the degree of detachment. NB: this formulation is just DOD for a single probe. Other methods may be possible
    for some shots. For example, using the integral from a JSAT profile, or a Eich fit to the JSAT profiles.
    """

    def __init__(self, tag):
        """
        Initialization
        :param tag: string
        reference name for signal
        """
        DI_signal.__init__(self, tag)

        self['tag'] = tag
        self['derived'] = True

    def fetch(self, shotnumber, device, probe_tree, units, LP_processing_settings, density_processing_settings):
        """
        This subclass will operate on the probe tree to calculate DOD as per in DI_LP_signal

        :param shotnumber: int
        number of shot of interest

        :param device: string
        server for MDS+ calls
        .
        :param units: OMFITTree
        Descriptors of the units for each of the param_name options. Often empty for DOD

        :param LP_processing_settings: Dict
        settings dict containing filter_settings, smoothing_settings, DOD_tmin, DOD_tmax. See process_data.py
        for full details.

        :param density_processing_settings: Dict
        settings dict containing filter_settings, smoothing_settings for the density processing
        """

        print('Calculating DOD')

        self['shotnumber'] = shotnumber
        self['device'] = device

        DOD_min = LP_processing_settings['DOD_tmin']
        DOD_max = LP_processing_settings['DOD_tmax']
        dod_zeroth_order_term = LP_processing_settings.get('dod_zeroth_order_term', True)
        truncate_range = [LP_processing_settings['truncate_range'][0] - 300, LP_processing_settings['truncate_range'][1] + 300]

        jsat = DI_LP_signal(self['tag'])
        jsat.fetch(shotnumber, probe_tree, 'JSAT', units)
        jsat.truncate_times(truncate_range)
        jsat.ELM_filter(LP_processing_settings['elm_obj'], LP_processing_settings['filter_settings'])
        jsat.smooth(LP_processing_settings['smooth_settings'])

        # The processing for density is handled incrementally to ensure settings align with it being the
        # independent variable for this jsat DI_signal instance
        density_pointname = density_processing_settings.get('pointname', 'density')
        # The den** pointnames include both passes of the laser through the plasma so need 0.5
        # fmt: off
        density_factor = (
            density_processing_settings.get('factor', None)
            or {
                'density': 1e-13,
                'prmtan_neped': 1e-19,
                'denv3': 0.5e-13,
                'denv2': 0.5e-13,
                'denv1': 0.5e-13,
                'denr0': 0.5e-13,
            }.get(density_pointname, 1)
        )
        # fmt: on
        density = DI_signal(density_pointname)
        density.fetch(self['shotnumber'], self['device'])
        density.truncate_times([np.min(jsat['RAW']['times']) - 200, np.max(jsat['RAW']['times']) + 200])
        density.ELM_filter(density_processing_settings['elm_obj'], density_processing_settings['filter_settings'])
        density.smooth(density_processing_settings['smooth_settings'])

        jsat.remap(density)
        xdata = copy.copy(jsat['REMAPPED']['xdata'])
        ydata = copy.copy(jsat['REMAPPED']['data'])
        times = copy.copy(jsat['SMOOTHED']['times'])
        xmin_loc = np.argmin(abs(jsat['SMOOTHED']['times'] - DOD_min))
        xmax_loc = np.argmin(abs(jsat['SMOOTHED']['times'] - DOD_max))

        # This is the real fitting part of JSAT as a function of density. It may seem overkill for a polynomial fit
        # but polyfit was giving me trouble and this will be extensible for more sophisticated fits.
        def DOD_fun(p, xdata):
            """
            Definition of Degree of Detachment. See Loarte NF 38(3): 1998 for details
            :param xdata: arraylike
            Densities
            :return: arraylike
            Degree of Detachment at all densities specified in xdata
            """
            ydata = p[0] * xdata ** 2
            if dod_zeroth_order_term:
                ydata += p[1]
            return ydata

        def fit_fun(p, exp_data=None):
            """
            A function used for optimizing the DOD fit. Compares fit to data and returns least squares difference
            that can be used for minimization purposes

            :param p: arraylike
            Coefficients for fit that are passed to DOD_fun

            :param exp_data: arraylike
            The experimental data to be compared against (eg a single probe's JSAT)

            :return: float
            Least squares difference for this set of p values
            """
            xdata, ydata = exp_data
            fit = DOD_fun(p, xdata)
            lsq_output = np.sum((ydata - fit) ** 2)
            return lsq_output

        fit_fun_partial = functools.partial(fit_fun, exp_data=[xdata[xmin_loc:xmax_loc] * density_factor, ydata[xmin_loc:xmax_loc]])
        p_guess = [1, 0]

        f = scipy.optimize.minimize(fit_fun_partial, p_guess, method='Powell')
        n_scaling = DOD_fun(f.x, xdata * density_factor)
        DOD = n_scaling / ydata
        self['RAW'] = SortedDict()
        self['RAW']['times'] = times
        self['RAW']['data'] = DOD
        self['RAW']['units'] = ''
        self['RAW']['DOD_jsat'] = ydata
        self['RAW']['DOD_density'] = xdata * density_factor
        self['RAW']['DOD_fit'] = n_scaling
        self['RAW']['DOD_time_range'] = [DOD_min, DOD_max]
        if dod_zeroth_order_term:
            self['RAW']['DOD_coefficients'] = f.x
        else:
            self['RAW']['DOD_coefficients'] = [f.x[0], 0]
        self['RAW']['density_pointname'] = density_pointname


class DI_GW_signal(DI_signal):
    """
    A convenience function for calculating the greenwald fraction
    """

    def __init__(self, tag):
        """
        Initialization of greenwald DI_signal
        :param tag: string
        reference name for signal
        """
        DI_signal.__init__(self, tag)

        self['tag'] = tag
        self['derived'] = True

    def fetch(self, shotnumber, device, processing_settings):
        """
        Fetch the mdsplus values for density,aminor, and ip to calculate the Greenwald fraction

        :param shotnumber: integer
        The number of the shot of interest

        :param device: string
        Name of the server to be used for MDS+ calls

        :param processing_settings: dict
        A nested dictionary of settings to be used for smoothing and ELM filtereing. See process_data.py for more
        information
        """

        print('Calculting greenwald fraction')

        self['shotnumber'] = shotnumber
        self['device'] = device

        dataset = {}

        for signal_name in ['aminor', 'ip', 'density']:
            data = DI_signal(signal_name)
            data.fetch(shotnumber, device)
            data.truncate_times(None)
            data.ELM_filter(processing_settings[signal_name]['elm_obj'], processing_settings[signal_name]['filter_settings'])
            data.smooth(processing_settings[signal_name]['smooth_settings'])
            data.smoothed_interp_fun = interp1d(data['SMOOTHED']['times'], data['SMOOTHED']['data'])
            dataset[signal_name] = data

        # Determine the minimum range of density times for which all signals are valid to provide a time-base that can
        # be reliably interpolated onto.
        t_mins = []
        t_maxes = []
        for signal_name in dataset:
            t_mins.append(np.min(dataset[signal_name]['SMOOTHED']['times']))
            t_maxes.append(np.max(dataset[signal_name]['SMOOTHED']['times']))
        dens_tmin_loc = np.argmin(abs(dataset['density']['SMOOTHED']['times'] - np.max(t_mins))) + 1
        dens_tmax_loc = np.argmin(abs(dataset['density']['SMOOTHED']['times'] - np.min(t_maxes))) - 1

        times = dataset['density']['SMOOTHED']['times'][dens_tmin_loc:dens_tmax_loc]
        aminor = dataset['aminor'].smoothed_interp_fun(times)
        ip = dataset['ip'].smoothed_interp_fun(times)
        density = dataset['density'].smoothed_interp_fun(times)

        greenwald_fraction = density * 3.14e-8 * aminor * aminor / ip

        self['RAW'] = SortedDict()
        self['RAW']['times'] = times
        self['RAW']['data'] = greenwald_fraction
        self['RAW']['units'] = ''


class DI_asdex_signal(DI_signal):
    """
    A convenience function for calculating the various kinds of neutral compression from the gauges
    """

    def __init__(self, tag):
        """
        Initialization of greenwald DI_signal
        :param tag: string
        reference name for signal
        """
        DI_signal.__init__(self, tag)

        self['tag'] = tag
        self['derived'] = True

    def fetch(self, shotnumber, device, processing_settings):
        """
        Fetch the mdsplus values for calculation of the neutral compression in the SAS.

        :param shotnumber: integer
        The number of the shot of interest

        :param device: string
        Name of the server to be used for MDS+ calls

        :param processing_settings: dict
        A nested dictionary of settings to be used for smoothing and ELM filtereing. See process_data.py for more
        information
        """

        print('Calculting ASDEX gauge SAS compression')

        self['shotnumber'] = shotnumber
        self['device'] = device
        dataset = {}

        for signal_name in ['asdex_sas1a', 'asdex_sas1b']:
            data = DI_signal(signal_name)
            data.fetch(shotnumber, device)
            data.truncate_times([-500, np.max(data['RAW']['times'])])  # Remove extreme values before shot begins
            dataset[signal_name] = data

        # ASDEX gagues are on the same time base, so they can just be divided

        self['RAW'] = SortedDict()
        self['RAW']['times'] = dataset['asdex_sas1a']['RAW_TRIM']['times']
        self['RAW']['data'] = dataset['asdex_sas1a']['RAW_TRIM']['data'] / dataset['asdex_sas1b']['RAW_TRIM']['data']
        self['RAW']['units'] = ''
