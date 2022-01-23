# Created by eldond at 2019-12-02 11:50

"""
Provides tools used for analyzing tokamak control systems
"""

import math
import numpy as np
from scipy.interpolate import interp1d

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

from omfit_classes.omfit_mds import OMFITmdsValue, interpret_signal
from omfit_classes.omfit_base import OMFITtmp
from omfit_classes.omfit_rdb import OMFITrdb
from omfit_classes.utils_fusion import is_device

__all__ = ['auto_scale', 'mean_trapz', 'ControlAnalysis', 'SystemIdentification', 'ControlQuality', 'sanitize_key', 'remove_periodic_noise']


def sanitize_key(key):
    """
    Replaces illegal characters in a string so it can be used as a key in the OMFIT tree

    :param key: string

    :return: string
    """
    sk = '{}'.format(key)
    translations = {'/': '_|_'}
    for old, new in translations.items():
        sk.replace(old, new)
    return sk


def auto_scale(x, y):
    """
    Given some data, pick a scale that would probably work nicely for most smoothing functions.

    If the user doesn't like it, they can provide a scale explicitly.

    :param x: float array
        Independent variable.

    :param y: float array
        Dependent variable. We assume you want to smooth this and have it look nice.

    :return: float
        Scale for smoothing y(x) in same units as x.
    """
    nx = len(x)
    if not len(x):
        return np.NaN
    # Increase nfft to get better resolution around low frequency features
    nfft = int(2 ** (np.floor(math.log(nx, 2)) + 1))
    dx = np.nanmean(np.diff(x))

    f = pylab.rfft(y - np.nanmean(y), nfft)
    freq = pylab.rfftfreq(nfft, dx)

    # Pick a smoothing frequency based on when big low frequency components drop out of FFT
    rf = np.real(f) ** 2
    rf = smooth(rf, min([11, int(np.floor(nx / 2.0))]))
    rf /= np.max(rf)
    fs = (freq[rf <= 1e-1])[0]
    fsa = fs

    scale = 1.0 / fsa

    return scale


def mean_trapz(y, x=None, nan_policy='ignore'):
    """
    Average y using trapezoid rule and step spacing from x, if provided.

    Can be used to effectively weight y by dx and cope with uneven x spacing.

    :param y: float array
        Dependent variable to average

    :param x: float array [optional]
        Independent variable corresponding to y. If not provided, will assume even spacing.

    :param nan_policy: string
        'ignore' or 'propagate'

    :return: float
        Average value of y using trapezoid integration and accounting for potential uneven x spacing
    """
    if x is None:
        x = np.arange(len(y))
    if nan_policy == 'ignore':
        w = ~np.isnan(x) & ~np.isnan(y)
        x2 = x[w]
        y2 = y[w]
    else:
        x2 = x
        y2 = y
    return np.trapz(y2, x2) / np.trapz(np.ones(len(y2)), x2)


def remove_periodic_noise(x, y, baseline_interval, amp_threshold=0.1, min_freq='auto', max_freq=None, debug=False):
    """
    Tries to remove periodic noise from a signal by characterizing a baseline interval and extrapolating

    1. FFT signal during baseline interval, when there should be no real signal (all noise)
    2. Cut off low amplitude parts of the FFT and those outside of min/max freq
    3. Find frequencies where the baseline has high amplitude
    4. Suppress frequency components that appear prominently in the baseline

    :param x: 1D float array

    :param y: 1D float array

    :param baseline_interval: two element numeric iterable
        Should give start and end of time range / x range to be used for noise
        characterization. Both ends must be within the range of X.

    :param amp_threshold: float
        Fraction of peak FFT magnitude (not counting 0 frequency) to use as a threshold.
        FFT components with magnitudes below this will be discarded.

    :param min_freq: float [optional]
        Also remove low frequencies while cleaning low amplitude components out of the FFT

    :param max_freq: float [optional]
        Also remove high frequencies while cleaning low amplitude components out of the FFT

    :param debug: bool
        Returns intermediate quantities along with the primary result

    :return: 1D float array or dictionary
        If debug is False: 1D array
            y, but with best estimate for periodic noise removed
        If debug is True: dict
    """
    # Get FFT of baseline interval
    sel = (x >= baseline_interval[0]) & (x <= baseline_interval[1])
    x1 = x[sel]
    y1 = y[sel]
    dx = np.nanmedian(np.diff(x1))
    fr = np.fft.fftfreq(len(y1), d=dx)
    f = np.fft.fft(y1)

    # Discard small components; these are more likely to be random noise and not the periodic signal we're after
    fclean = copy.copy(f)
    if min_freq is not None:
        if min_freq == 'auto':
            min_freq = (fr[1] - fr[0]) * 2
        fclean[abs(fr) < min_freq] = 0
    if max_freq is not None:
        fclean[abs(fr) > max_freq] = 0
    fnorm = np.max(abs(fclean * fr)[fr != 0])
    fclean[abs(fclean * fr) < (fnorm * amp_threshold)] = 0

    # Find where the baseline has components with large amplitude
    fmagc = abs(fclean)
    fall = np.fft.fft(y)
    frall = np.fft.fftfreq(len(y), d=dx)
    fmagci = np.fft.ifftshift(
        interp1d(np.fft.fftshift(fr), np.fft.fftshift(fmagc), bounds_error=False, fill_value=0)(np.fft.fftshift(frall))
    )

    # Suppress frequency components that appear prominently in the baseline
    fall[fmagci > 0] = 0
    yf = np.real(np.fft.ifft(fall))

    if debug:
        ynoise = y - yf
        return dict(yf=yf, ynoise=ynoise)
    return yf


class ControlAnalysisBadInputValue(ValueError, doNotReportException):
    """Some value was outside of reasonable ranges or was otherwise problematic"""


class ControlAnalysis(OrderedDict):
    """
    Contains helper functions for analyzing control problems.
    """

    # Setup methods
    def __init__(self, **kw):
        """
        :param topic: string [optional]
            Topic of the control analysis, like "Detachment control"

        :param device: string [optional]
            Which tokamak or device is being analyzed? Like 'DIII-D'

        :param shot: int [optional]
            Which shot is being analyzed?
        """
        super().__init__()

        self['__scratch__'] = self._pop_kw('scratch', OMFITtmp(), kw)
        self['__fit_controls__'] = SortedDict()
        self['__fit_controls__']['uniform_dx'] = False
        self['__fit_controls__']['fit_out_name_format'] = 'order_{order:}_generic_control_response'
        self['__details__'] = SortedDict()
        self['__details__']['time_range'] = self._pop_kw('time_range', None, kw)
        self['__details__']['time_units'] = self._pop_kw('time_units', None, kw)
        self['__plot__'] = SortedDict()
        self['summary'] = SortedDict()
        self['summary']['uniform_dx'] = False
        # Track problems in a dictionary where the keys are descriptions of problems and values are severity.
        # Severity will be scaled as:
        self['__details__']['problem_severity_scale'] = {
            1: 'minor warning',
            2: 'warning',
            3: 'stern warning',
            4: 'serious warning',
            5: 'error in secondary method',
            6: 'error in important method due to inputs',
            7: 'error in important method',
            8: 'partial failure in setup/init',
            9: 'serious failure in setup; even minor methods of a dummy instance will not work',
            10: 'catastrophic failure',
        }
        self['__details__']['problem_severity_qualitative_scale'] = {
            1: 'minor',
            2: 'minor',
            3: 'minor',
            4: 'moderate',
            5: 'moderate',
            6: 'moderate',
            7: 'serious',
            8: 'serious',
            9: 'serious',
            10: 'serious',
        }
        self['__details__']['problems'] = {}
        self['__details__']['debug_topic'] = self.__class__.__name__
        self['__details__']['median_filter_max_steps'] = 3503
        self['__details__']['dt_var_thresh'] = self._pop_kw('dt_var_thresh', 1e-3, kw)
        self._setup_plot(**kw)
        for thing in ['device', 'shot', 'topic']:
            self['__details__'][thing] = self._pop_kw(thing, None, kw)
        self.describe_case()
        return

    def _fetch_data(self, reference, smooth_first=False):
        """
        Fetches data from MDSplus as an alternative to supplying data. Data will be loaded into self['history'].

        Requires device, shot, and other info related to the reference to be stored in the class
        (supply these when initializing). Will not overwrite existing data for the reference.

        :param reference: string
            Quantity to look up within self.
            For example, 'response' will direct this function to look up
            'response_pointname', 'response_treename', etc.

        :param smooth_first: bool
            Perform smoothing before cutting or interpolating data.
            Useful when smoothing method introduces edge effects; these can be
            mitigated by including data from outside of the desired range.
        """
        self.printq('_fetch_data({})...'.format(repr(reference)))
        cx = self['history'].get('x', None)
        if cx is not None and self['history'].get(reference, None) is not None:
            # This reference already exists. Don't do anything.
            self.printq('  already have {}; aborting _fetch_data({})...'.format(reference, repr(reference)))
            return
        if (self['__details__']['device'] is None) or (not self['__details__'].get('{}_pointname'.format(reference), None)):
            # This must be a dummy instance or unused optional signal or something. We can't work with this.
            self['history'][reference] = None
            self.printq('  No pointname for {}. Aborting _fetch_data({})'.format(reference, repr(reference)))
            return
        shots = self['__details__']['shot']
        x_factor = self['__details__']['{}_x_factor'.format(reference)] * self['__details__']['overall_x_factor']
        y_factor = self['__details__']['{}_y_factor'.format(reference)] * self['__details__']['overall_y_factor']

        # Prepare objects to catch data
        x = []
        y = []
        # Accumulate data for all shots
        for i, shot in enumerate(np.atleast_1d(shots)):
            # Pull data from MDSplus
            x1, y1, u1, xu1 = interpret_signal(
                server=self['__details__']['device'],
                treename=self['__details__']['{}_treename'.format(reference)],
                shot=shot,
                tdi=self['__details__']['{}_pointname'.format(reference)],
                scratch=self['__scratch__'].setdefault(reference, dict()),
            )
            if x1 is None or y1 is None:
                printw('Aborted data fetching for {}'.format(reference))
                self['history'][reference] = None
                self['__details__']['problems'][
                    'Failed to gather data for {} with pointname {}'.format(
                        reference, self['__details__']['{}_pointname'.format(reference)]
                    )
                ] = 8
                return

            x1 *= x_factor
            y1 *= y_factor
            if not self['__details__'].get('{}_units'.format(reference), None):
                self.printq('  Updating {} units to ({}) using data output by interpret_signal()'.format(reference, u1))
                self['__details__']['{}_units'.format(reference)] = u1
            else:
                self.printq('  Already have units for {}; ignoring units ({}) output by interpret_signal()'.format(reference, u1))
            if smooth_first:
                self.printq(
                    f"Smoothing incoming data during _fetch_data(): {reference}, "
                    f"{self['__details__']['smoother']}, {self['__details__']['scale']}"
                )
                # Do some cutting first to speed up the smooth
                xmin = self['__details__']['time_range'][0] - self['__details__']['scale'] * 2
                xmax = self['__details__']['time_range'][1] + self['__details__']['scale'] * 2
                sel = (x1 >= xmin) & (x1 <= xmax)
                x1 = x1[sel]
                y1 = y1[sel]
                y1 = self._smooth(x1, y1)
            if cx is None:
                # Wow, this is the first pointname! It gets to define x (and x units)!
                self.printq(
                    '  No x defined yet; this must be the first pointname! ref: {}, ptname: {}'.format(
                        reference, self['__details__']['{}_pointname'.format(reference)]
                    )
                )
                w = (x1 >= self['__details__']['time_range'][0]) & (x1 <= self['__details__']['time_range'][1])
                self.printq(
                    '  x data range: {} to {} s; analysis range: {} to {} s'.format(
                        np.nanmin(x1), np.nanmax(x1), self['__details__']['time_range'][0], self['__details__']['time_range'][1]
                    )
                )
                if not len(np.atleast_1d(w)):
                    self['__details__']['problems']['No x data found within time range'] = 8
                    raise OMFITexception(
                        'No x data found within time range. Did you match the units correctly? '
                        'time_range = {}, x.min = {}, x.max = {}'.format(self['__details__']['time_range'], x1.min(), x1.max())
                    )
                x1 = x1[w]
                y1 = y1[w]
                if not self['__details__'].get('time_units', None):
                    if x_factor == 1e-3 and xu1 == 'ms':
                        xu1 = 's'
                    elif x_factor != 1:
                        xu1 = '{} {}'.format(x_factor, xu1)
                    self['__details__']['time_units'] = xu1
            else:
                # x is already defined, so interpolate to make sure all data are sampled consistently.
                if len(np.shape(cx)) > 1:
                    cxi = cx[~np.isnan(cx[:, i]), i]
                else:
                    cxi = cx
                    self.printq('  Interpolating y for {} with original length {}'.format(reference, len(y1)))
                y1 = interp1d(x1, y1, bounds_error=False, fill_value=np.NaN)(cxi)
                x1 = cxi
            x += [x1]
            y += [y1]
            self.printq('  Length of new y entry under {}: {}'.format(reference, len(y1)))
        # Add NaNs to the ends of arrays as needed to make consistent length
        nx = np.max([len(x1) for x1 in x])
        ns = len(np.atleast_1d(shots))
        for i in range(ns):
            n = len(x[i])
            extra = nx - n
            if extra > 0:
                xtr = np.empty(extra)
                xtr[:] = np.NaN
                x[i] = np.append(x[i], xtr)
                y[i] = np.append(y[i], xtr)

        # Finalize
        x, y = np.squeeze(np.array(x).T), np.squeeze(np.array(y).T)
        if cx is None:
            self['history']['x'] = x
        self['history'][reference] = y
        return

    def _setup_calcs(self, **kw):
        """
        :param uniform_dx: bool
            Are x (independent variable) evenly spaced?

        :param fit_npts: int
            Maximum number of points to use for fitting.
        """
        dx = np.diff(self['history']['x'], axis=0)
        udx = np.all((np.nanmean(dx, axis=0) == 0)) or np.all(((np.nanstd(dx, axis=0) / np.nanmean(dx, axis=0)) < 1e-3))
        self['summary']['uniform_dx'] = self['__fit_controls__']['uniform_dx'] = self._pop_kw('uniform_dx', udx, kw)
        self['__fit_controls__']['npts'] = self._pop_kw('fit_npts', 250, kw)
        self['__fit_controls__']['method'] = self._pop_kw('method', 'nelder', kw)
        self['__fit_controls__']['nan_policy'] = self._pop_kw('nan_policy', ['raise', 'propagate', 'omit'][0], kw)
        return

    def _setup_smooth(self, x, y, **kw):
        """
        :param scale: float with units matching x
            Scale for smoothing some quantities. For example, you could get RMS error where the M is actually not
            a mean over all time, but a smooth (which is effectively a weighted mean of nearby data).
            This is probably a timescale in ms for DIII-D or in s for most other devices.

        :param smoother: string
            Sets which smoothing function to use

        :param window_function: string
            Which window function to use

        :param causal_smoothing: bool
            Use a causal (doesn't see the future / isn't symmetric in x) smoothing function or kernel
        """
        self['__details__']['scale'] = kw.pop('scale', None)
        if (self['__details__']['scale'] is None) and (len(np.shape(x)) > 1):
            nx2 = len(x[0, :])
            asc = [np.NaN] * nx2
            for i in range(nx2):
                asc[i] = auto_scale(x[:, i], y[:, i])
            self['__details__']['scale'] = np.nanmean(asc)
        elif (self['__details__']['scale'] is None) and (y is not None):
            self['__details__']['scale'] = auto_scale(x, y)
        self['__details__']['smoother'] = kw.pop('smoother', 'butter_smooth')
        self['__details__']['window_function'] = kw.pop('window_function', 'hanning')
        self['__details__']['causal_smoothing'] = kw.pop('causal_smoothing', False)
        return

    smoother_options = ['smooth_by_convolution', 'smooth', 'butter_smooth', 'median_filter', 'trismooth']

    def _smooth(self, x, y, override_scale=None):
        """
        Shortcut to smoothing data with the class's settings

        :param x: 1d float array

        :param y: 1d float array

        :param override_scale: float [optional]

        :return: 1d float array
        """
        scale = self['__details__']['scale'] if override_scale is None else override_scale
        if self['__details__']['smoother'] == 'smooth_by_convolution':
            return smooth_by_convolution(
                y,
                x,
                window_size=scale,
                window_function=self['__details__']['window_function'],
                causal=self['__details__']['causal_smoothing'],
            )
        elif self['__details__']['smoother'] == 'smooth':
            window_len = int(np.ceil(scale / np.mean(np.diff(x))))
            if self['__details__']['causal_smoothing']:
                window = scipy.signal.get_window(self['__details__']['window_function'], window_len, fftbins=False)
                window[(window_len + 1) // 2 :] = 0
            else:
                return smooth(y, window_len, window=self['__details__']['window_function'])
        elif self['__details__']['smoother'] == 'butter_smooth':
            return butter_smooth(x, y, scale, laggy=self['__details__']['causal_smoothing'])
        elif self['__details__']['smoother'] == 'median_filter':
            median_filter_steps = int(np.ceil(scale / np.nanmedian(np.diff(x)) / 2.0) * 2 + 1)
            # Median filtering is SLOOOOW if a lot of steps are included
            if median_filter_steps > self['__details__']['median_filter_max_steps']:
                max_scale = (self['__details__']['median_filter_max_steps'] - 1) * np.nanmedian(np.diff(x))
                raise ControlAnalysisBadInputValue(
                    f'Too many steps ({median_filter_steps}) for median filter with\n'
                    f'timescale {scale} and data sampled every {np.nanmedian(np.diff(x))}.\n'
                    f'Mitigate this problem by manually setting scale to somethings smaller (<= {max_scale}).'
                )
            # Median filtering can introduce weird effects at the edges; mitigate by padding with a specific value
            padlen = median_filter_steps // 2
            self.printq(f'median_filter_steps = {median_filter_steps}')
            front_pad = np.nanmedian(y[:padlen])
            back_pad = np.nanmedian(y[-padlen:])
            ymod = np.append(np.append([front_pad] * padlen, y), [back_pad] * padlen)
            ysmo = scipy.signal.medfilt(ymod, median_filter_steps)
            return ysmo[padlen:-padlen]
        else:  # if self['__details__']['smoother'] == 'trismooth':
            return trismooth(y, x, scale)

    def _cleanup_units(self, default_units=''):
        """
        Makes sure unspecified or missing units are '', not None, to avoid awkward display issues
        Or, alternatively, supply default units to assign where units are missing (instead of '')

        :param default_units: string
        """
        uk = [k for k in self['__details__'] if k.endswith('units')]
        for k in uk:
            if self['__details__'][k] is None:
                self['__details__'][k] = default_units
        return

    def _rdb_setup(self, **kw):
        """
        Sets up Relational DataBase (RDB) interfacing instructions
        :param kw: keywords passed through __init__
        """
        div_ctrls = ['Detach', 'Prad']
        device_db_info = {'DIII-D': ['huez', 'd3d'], 'EAST': ['huez', 'd3d']}

        default_controller = self['__details__'].get('topic', None)
        if default_controller not in div_ctrls:
            default_controller = 'Detach'
        device = self['__details__'].get('device', None)

        self['__rdb__'] = SortedDict()
        self['__rdb__']['server'], self['__rdb__']['database'] = device_db_info.get(tokamak(device), [None, None])
        self['__rdb__']['shot'] = self['__details__'].get('shot', None)
        controller = self._pop_kw('controller', default_controller, kw)
        if controller in div_ctrls:
            self['__rdb__']['table'] = 'divertor_control_settings'
        else:
            self['__rdb__']['table'] = None
        self['__rdb__']['controller'] = controller
        self['__rdb__']['checks'] = ['ctrl_tmin', 'ctrl_tmax']
        notes = [self['__details__'].get('topic', None), self['__fit_controls__'].get('method', None)]
        self['__rdb__']['notes'] = '; '.join([a for a in notes if a is not None])
        self['__rdb__']['tag'] = self._pop_kw('rdb_tag', None, kw)
        return

    @staticmethod
    def _pop_kw(key, default, kw):
        """
        Shortcut for popping keywords out of **kw while also providing default values

        :param key: string
            The name of the keyword

        :param default: object
            The default value it should have if it doesn't exist or is None

        :param kw: dict
            Keywords and values, in which key will be sought.
        """
        value = kw.pop(key, None)
        return default if value is None else value

    def describe_case(self, topic=None, device=None, shot=None):
        """Form a string describing the case being analyzed using user-supplied data"""
        topic = self['__details__'].get('topic', None) if topic is None else topic
        device = self['__details__'].get('device', None) if device is None else device
        shot = np.squeeze(self['__details__'].get('shot', None) if shot is None else shot)
        if (device is None) and (shot is None):
            dv = ''
        elif device is None:
            dv = '#{:}'.format(shot)
        elif shot is None:
            dv = tokamak(device)
        else:
            dv = '{}#{:}'.format(tokamak(device), shot)

        if topic is None:
            self['__details__']['case'] = dv
        else:
            self['__details__']['case'] = '{}: {}'.format(sanitize_key(topic), dv)
        return copy.copy(self['__details__']['case'])

    def _setup_plot(self, **kw):
        """
        :param error_color: Matplotlib color specification
            Color to use for errors

        :param target_color: Matplotlib color specification
            Color to use for targets

        :param command_color: Matplotlib color specification
            Color to use for commands.
            Probably won't be used at the same time as target_color, so they can be the same.

        :param dtdx_color: Matplotlib color specification
            Color to use for d(target)/dx

        :param measurement_color: Matplotlib color specification
            Color to use for measurements

        :param model_color: Matplotlib color specification
            Color to use for models output from fitting

        :param guess_color: Matplotlib color specification
            Color to use for guesses input to fitting

        :param other_error_color: list of Matplotlib color specifications
            Colors to use for other quality metrics and errors

        :param shot_color_cycle: list of Matplotlib color specifications
            In multi-shot mode, this list is used to color objects for a given shot instead of the
            target/measurement/etc. colors. This will only turn out well for plots that use different
            linestyles for different quantities.
        """
        self['__plot__']['error_color'] = kw.pop('error_color', 'r')
        self['__plot__']['target_color'] = kw.pop('target_color', 'b')
        self['__plot__']['command_color'] = kw.pop('command_color', 'b')
        self['__plot__']['dtdx_color'] = kw.pop('dtdx_color', 'g')
        self['__plot__']['measurement_color'] = kw.pop('measurement_color', 'r')
        self['__plot__']['model_color'] = kw.pop('model_color', 'c')
        self['__plot__']['guess_color'] = kw.pop('guess_color', 'g')
        self['__plot__']['other_error_colors'] = kw.pop('other_error_colors', ['m', 'orange', 'firebrick'])
        self['__plot__']['shot_color_cycle'] = kw.pop('shot_color_cycle', ['b', 'r', 'm', 'c', 'g', 'gray', 'orange'])
        return

    def update_parent_module_settings(self, module_root=None):
        """
        Uses the settings in this class instance to update settings in the parent module to force consistency

        This is like the reverse of ['SCRIPTS']['general']['control_analysis_setup'] in the PCS module.

        :param module_root: OMFITmodule instance [optional]
            You can manually provide this in case there's trouble identifying it automatically, which is unlikely.

        :return: bool
            Was an update done?
        """
        from omfit_classes.omfit_base import OMFITmodule
        from omfit_classes.omfit_json import SettingsName

        # Find the parent module
        location = treeLocation(self)
        for loc in location[1:]:
            if loc == 'OMFIT':
                continue
            thing = eval(loc)
            if isinstance(thing, OMFITmodule):
                module_root = thing
            elif module_root is not None:
                break
        if module_root is None:
            print(
                'Aborting update of parent module settings because the parent module could not be identified. '
                'You can supply a reference to it manually with the module_root keyword.'
            )
            return False

        # Find which settings to update
        tags = dict(SystemIdentification='sys_id', ControlQuality='ctrl_qual', ControlAnalysis='ctrl_analysis')
        tag = tags.get(self.__class__.__name__, None)
        if tag is None:
            print(f'This class ({self.__class__.__name__}) is not supported.')
            return False
        print(f"Updating {tag} settings for module with ID: {module_root['SETTINGS']['MODULE']['ID']}")
        settings = module_root['SETTINGS']['PHYSICS'].setdefault(tag, SettingsName())

        # Handle experiment settings
        expt_set = dict(device=self['__details__']['device'])
        if isinstance(self, SystemIdentification):
            expt_set['shots'] = np.atleast_1d(self['__details__']['shot'])
        else:
            expt_set['shot'] = self['__details__']['shot']
        module_root.experiment(**{k: v for k, v in expt_set.items() if v is not None})

        # Handle some easy to process settings in details
        details = ['topic', 'time_range', 'overall_x_factor', 'smooth_response', 'smoother', 'scale', 'enable_value']
        if tag == 'sys_id':
            details += ['target_pointname', 'enable_pointname', 'response_pointname', 'command_pointname', 'response_uncertainty_pointname']
        else:
            details += ['target_pointname', 'enable_pointname', 'measurement_pointname']
        for detail_key in details:
            settings[detail_key] = self['__details__'].get(detail_key, None)

        # Handle treenames: don't overwrite SETTINGS if they're not set to be used, anyway
        excl = ['response_uncertainty_pointname']
        trees = [a.replace('_pointname', '_treename') for a in details if ('_pointname' in a) and (a not in excl)]
        settings['data_from_mds'] = any(self['__details__'].get(tree, None) is not None for tree in trees)
        if settings.get('data_from_mds', False):
            for tree in trees:
                settings[tree] = self['__details__'][tree]

        # Handle fit controls
        if self['__fit_controls__'].get('npts', None) is not None:
            settings['fit_npts'] = self['__fit_controls__']['npts']

        return True

    # General utilities
    def _pick_name(self, order, new_name=False):
        """Picks a unique name for fit output"""
        name0 = self['__fit_controls__']['fit_out_name_format'].format(**locals())
        if not new_name:
            return name0
        name = name0
        i = 0
        while name in self:
            name = '{}_{}'.format(name0, i)
            i += 1
        return name

    def load_results_to_rdb(self, orders=None, tag=None, overwrite=0, test_data=None):
        """
        Loads results to the RDB

        :param orders: list of ints
            Fit orders to consider

        :param tag: string
            'sys' or 'cq' for base system identification or control quality evaluation

        :param overwrite: int or bool
            Passed to OMFITrdb.update(), where it has the following effects:
             - 0/False: abort loading any results if anything would be overwritten
             - 1/True: ignore pre-existing results and try to load regardless of what would be overwritten
             - 2: avoid overwriting by popping keys out of new data if they are found with non-None in existing data

        :param test_data: dict [optional]
            Used for testing: if a dictionary is supplied, its keys should match columns in the RDB.

        :return: OMFITrdb instance
        """
        from lmfit import Parameter

        def clean_data(dat):
            """Evaluates .value of Parameter instances and removes "None" entries"""
            for k in list(dat.keys()):
                if isinstance(dat[k], Parameter):
                    dat[k] = dat[k].value
                if dat[k] is None:
                    del dat[k]
            return dat

        def get_w_factor(source, key, factor):
            """
            Gets data and applies a factor if that's possible

            :param source: dict-like

            :param key: string

            :param factor: float

            :return: depends
            """
            value = source.get(key, None)
            # noinspection PyBroadException
            try:
                return value * factor
            except Exception:
                return value

        # Form data
        time_unit_convert = 1000.0  # s to ms
        shots = tolist(self['__rdb__'].get('shot', None))
        tag = self['__rdb__'].get('tag', tag) if tag is None else tag
        assert tag is not None, 'Must specify whether system ID (sys) or control quality (cq) results are being loaded.'
        tr = [xx * time_unit_convert for xx in self['__details__']['time_range']]
        data = {}
        if tag == 'sys':
            if orders is None:
                orders = [1, 2]

            for order in orders:
                fit_out = self.get(self['__fit_controls__']['fit_out_name_format'].format(order=order), {})
                p = fit_out.get('params', {})
                data_o = {
                    'o{}_sys_y0'.format(order): p.get('y0', None),
                    'o{}_sys_gain'.format(order): p.get('gain', None),
                    'o{}_sys_lag'.format(order): get_w_factor(p, 'lag', time_unit_convert),
                    'o{}_sys_scale'.format(order): get_w_factor(p, 'scale', time_unit_convert),
                }
                if order > 1:
                    data_o['o{}_sys_damping'.format(order)] = p.get('damping', None)
                data_o = clean_data(data_o)
                # Only load shot, time, etc. (things that will surely be defined)
                # if there are some fit parameters to load
                if not len(data_o):
                    printw('No data to load for order {}. ' 'Only specific outputs are used; run fits to generate these.'.format(order))
                    self['__details__']['problems']['Unable to load missing order {} fit data to RDB'.format(order)] = 2
                    continue
                xfit = fit_out.get('inputs', {}).get('x', np.array([np.NaN]))
                ftr = np.array([xfit.min(), xfit.max()]) * time_unit_convert
                data_o.update(
                    {
                        'o{}_sys_shots'.format(order): shots,
                        'o{}_sys_time_range'.format(order): ftr,
                        'o{}_sys_notes'.format(order): self['__rdb__']['notes'],
                        'o{}_sys_date'.format(order): "now()",
                        'o{}_sys_redchisq'.format(order): fit_out['fit_out'].redchi,
                    }
                )
                data.update(clean_data(data_o))
                # Clear warnings that might be left over from past failed loading attempts
                self['__details__']['problems'].pop('Unable to load missing order {} fit data to RDB'.format(order), None)
        elif tag == 'cq':
            order = 2
            fit_out = self.get(self['__fit_controls__']['fit_out_name_format'].format(order=order), {})
            data_o = {
                'o2_cq_overshoot': fit_out.get('time_domain_specs', {}).get('overshoot', None),
                'o2_cq_settle_time': get_w_factor(fit_out.get('time_domain_specs', {}), 'settle_time', time_unit_convert),
            }
            data_o = clean_data(data_o)
            # Only load shot, time, etc. (things that will surely be defined)
            # if there are some fit parameters to load
            if not len(data_o):
                printe('No data to load for order 2 CQ. Only specific outputs are used; run fits to generate these.')
                self['__details__']['problems']['Unable to load missing order {} fit data to RDB'.format(order)] = 2

            else:
                xfit = fit_out.get('inputs', {}).get('x', np.array([np.NaN]))
                ftr = np.array([xfit.min(), xfit.max()]) * time_unit_convert
                data_o.update(
                    {
                        'cq_time_range': ftr,
                        'cq_date'.format(order): "now()",
                        'o{}_cq_redchisq'.format(order): fit_out['fit_out'].redchi,
                        'cq_rms_error': self.get('raw', {}).get('RMS_error', None),
                        'cq_data_units': self.get('raw', {}).get('RMS_error_units', None),
                        'o2_cq_gain_error': self.get('normalized', {}).get('gain_error_order_2', None),
                    }
                )
                # Clear warnings that might be left over from past failed loading attempts
                self['__details__']['problems'].pop('Unable to load missing order {} fit data to RDB'.format(order), None)
            data.update(clean_data(data_o))
        else:
            printe('Unrecogized tag: {}'.format(tag))
            self['__details__']['problems']['Failed to load to unrecognized category/tag {} to RDB'.format(tag)] = 2

        if isinstance(test_data, dict):
            data.update(test_data)

        assert len(data), 'No data to load! Only specific outputs are used; run more fits to generate them.'
        self['__rdb__']['last_data_tried'] = data

        # Set up DB connection
        table = self['__rdb__'].get('table', None)
        controller = self['__rdb__'].get('controller', None)
        columns = ', '.join(['controller', 'shot'] + list(data.keys()) + self['__rdb__'].get('checks', []))
        results = {}
        for shot in shots:
            where_str = "controller='{controller:}' and shot='{shot:}'".format(**locals())
            query = "SELECT {columns:} FROM {table:} WHERE {where_str:}".format(**locals())
            self['__rdb__']['last_query_tried'] = query
            # See if this case exists in the database
            result = OMFITrdb(query, db=self['__rdb__']['database'], server=self['__rdb__']['server'], by_column=False)
            if len(result) == 0:
                printe('No entry found in {table:} for shot {shot:}, controller = {controller:}'.format(**locals()))
                self['__details__']['problems']['This case does not exist in the database; unable to load'] = 5
            for res in result.values():
                tr_db = [res['ctrl_tmin'], res['ctrl_tmax']]
                if not np.array_equal(tr_db, tr):
                    printe("Time range in DB for {} ({}) doesn't match fit range ({})!".format(res['shot'], tr_db, tr))
                    self['__details__']['problems']['RDB time range does not match fit range'] = 4
            result.update(table, data, where_str, overwrite=overwrite)
            results[shot] = result
        return results

    def estimate_uncertainty(self, reference, min_frac_err=0.05, max_frac_err=0.35):
        """
        Estimates uncertainty in some quantity indicated by reference.
        The primary method relies on assuming that high frequency variation is noise that can be described as
        random measurement error or uncertainty. This requires a definition of "high" frequency, which is based on
        the system smoothing timescale.

        :param reference: string
            The data to be analyzed are x, y = self['history']['x'], self['history'][reference]

        :param min_frac_err: float
            Minimum error in y as a fraction of y

        :param max_frac_err: float
            Maximum error in y as a fraction of y

        :return: float array
            Uncertainty in self['history'][reference], with matching shape and units.
        """
        tag = '{}_uncertainty'.format(reference)
        if self['history'].get(tag, None) is None:
            x = self['history']['x']
            y = self['history'][reference]
            if y is None:
                self['history'][tag] = None
                self['__details__']['{}_units'.format(tag)] = self['__details__'].get('{}_units'.format(reference), None)
                self['__details__']['problems']['Failed to estimate uncertainty in {}'.format(reference)] = 6
                return None
            cutoff_tau = self['__details__']['scale'] / 10.0
            shx = np.shape(x)
            if len(shx) > 1:
                y_err = np.empty(shx)
                y_err[:] = np.NaN
                for i in range(np.shape(y_err)[1]):
                    y_err[:, i] = std_devs(
                        noise_estimator(
                            x[~np.isnan(x[:, i]), i],
                            y[~np.isnan(y[:, i]), i],
                            cutoff_timescale=cutoff_tau,
                            dt_var_thresh=self['__details__']['dt_var_thresh'],
                        )
                    )
            else:
                y_err = std_devs(
                    noise_estimator(x, y, cutoff_timescale=cutoff_tau, dt_var_thresh=self['__details__']['dt_var_thresh'])
                ).astype(float)
            # Impose limits
            yemin = abs(y) * min_frac_err
            yemax = abs(y) * max_frac_err
            y_err[y_err > yemax] = yemax[y_err > yemax]
            y_err[y_err < yemin] = yemin[y_err < yemin]
            self['history'][tag] = y_err
            self['__details__']['{}_units'.format(tag)] = self['__details__'].get('{}_units'.format(reference), None)
        return self['history'][tag]

    def __call__(self):
        """
        Preferred behavior: load the settings from this instance into module SETTINGS

        Alternative behavior: if not loaded into an appropriate module, try to plot results
        """
        from omfit_classes.OMFITx import UpdateGUI

        updated = self.update_parent_module_settings()
        if updated:
            UpdateGUI()
        elif hasattr(self, 'plot'):
            self.plot()

    # Fit models
    def p_first_order(self, par, x, u, uniform_dx=None):
        """
        Calculates expected response to a given target waveform using a first order plus dead time (FOPDT) model

        :param par: Parameters instance
            Fit parameters

        :param x: float array
            independent variable

        :param u: float array
            command or actuator history as a function of x

        :param uniform_dx: bool
            Evenly spaced x?

        :return: float array
            Expected response vs. time
        """
        uniform_dx = self['__fit_controls__']['uniform_dx'] if uniform_dx is None else uniform_dx
        y = np.zeros(len(x)) + par['y0'].value
        if uniform_dx:
            ui = None
        else:
            ui = interp1d(x, u, bounds_error=False, fill_value=(u[0], u[-1]))
        u0 = par.get('u0', None)
        u0 = u[0] if u0 is None else u0.value

        for i in range(1, len(x)):
            if x[i] <= x[i - 1]:
                # Maybe we're past the end of the real time range and we're into zero-padding at the end
                y[i:] = 0
                break
            if uniform_dx:
                idu = i - 1 - int(np.round(par['lag'].value / (x[i] - x[i - 1])))
                du = u[np.min([np.max([0, idu]), len(x) - 1])] - u0
            else:
                du = ui(x[i - 1] - par['lag'].value) - u0
            geff = par['gain'].value + par['d_gain_du'].value * du
            dydt = -((y[i - 1] - par['y0'].value) - geff * du) / par['scale'].value
            y[i] = y[i - 1] + dydt * (x[i] - x[i - 1])
        y = y ** (1.0 / (1 + par['ex'].value)) * par['y0'].value ** (par['ex'].value / (1 + par['ex'].value))
        return y

    def first_order(self, x, u, y0, gain, lag, scale, d_gain_du=0, ex=0, u0=None):
        """
        Calculates expected response to a given target waveform using a first order plus dead time (FOPDT) model

        :param x: float array
            independent variable

        :param u: float array
            command or actuator history as a function of x

        :param y0: float
            Initial y value (y units)

        :param gain: float
            Gain = delta_y / delta_u: how much will response variable change given a change in command?
            Units  = y units / u units

        :param lag: float
            How long before a change in command begins to cause a change in response? (x units)

        :param scale: float
            Timescale for response (x units)

        :param d_gain_du: float
            Change in gain per change in u away from u0. This is normally exactly 0. Should you really change it?

        :param ex: float
            Exponent ex in transformation Y = y * (y/y0)**ex. Transforms output y after running model.
            It is a modification of the standard model.
            This seemed like it was worth a shot, but it didn't do me any good.

        :param u0: float
            Reference u value (defaults to u[0])

        :return: float array
            Expected response vs. time
        """
        par = Parameters()
        par.add('y0', value=y0)
        par.add('gain', value=gain)
        par.add('lag', value=lag)
        par.add('scale', value=scale)
        par.add('d_gain_du', value=d_gain_du)
        if u0 is not None:
            par.add('u0', value=u0)
        par.add('ex', value=ex)
        return self.p_first_order(par, x, u)

    def p_second_order(self, par, x, u):
        """Version of second_order() using Parameters"""
        return self.second_order(
            x,
            u,
            par['y0'].value,
            par['gain'].value,
            par['lag'].value,
            par['scale'].value,
            par['damping'].value,
            d_gain_du=par['d_gain_du'].value,
            ex=par['ex'].value,
        )

    def second_order(self, x, u, y0, gain, lag, scale, damping, d_gain_du=0, ex=0, u0=None, uniform_dx=None):
        """
        Calculates expected response to a given target waveform using a second order plus dead time (SOPDT) model

        :param x: float array
            independent variable

        :param u: float array
            command or actuator history as a function of x

        :param y0: float
            Initial y value (y units)

        :param gain: float
            Gain = delta_y / delta_u: how much will response variable change given a change in command?
            Units  = y units / u units

        :param lag: float
            How long before a change in command begins to cause a change in response? (x units)

        :param scale: float
            Timescale for response (x units)

        :param damping: float
            unitless

        :param d_gain_du: float
            Change in gain per change in u away from u0. This is normally exactly 0. Should you really change it?

        :param ex: float
            Exponent X for transforming to Y in in Y = y (y/y0)^X

        :param u0: float
            Reference value of u. Defaults to u[0].

        :param uniform_dx: bool
            x is evenly spaced

        :return: float array
            Expected response vs. time
        """
        uniform_dx = self['__fit_controls__']['uniform_dx'] if uniform_dx is None else uniform_dx

        y = np.zeros(len(x)) + y0
        dydt = np.zeros(len(x))
        d2ydt2 = np.zeros(len(x))
        if uniform_dx:
            ui = None
        else:
            ui = interp1d(x, u, bounds_error=False, fill_value=(u[0], u[-1]))
        u0 = u[0] if u0 is None else u0
        for i in range(2, len(x)):
            if x[i] <= x[i - 1]:
                # Maybe we're past the end of the real time range and we're into zero-padding at the end
                y[i:] = 0
                break
            if uniform_dx:
                idu = i - 2 - int(np.round(lag / (x[i - 1] - x[i - 2])))
                du = u[np.min([np.max([0, idu]), len(x) - 1])] - u0
            else:
                du = ui(x[i - 2] - lag) - u0
            geff = gain + du * d_gain_du
            d2ydt2[i - 2] = (geff * du - (y[i - 2] - y0)) / scale ** 2 - 2 * damping / scale * dydt[i - 2]
            dydt[i - 1] = dydt[i - 2] + d2ydt2[i - 2] * (x[i - 1] - x[i - 2])
            y[i] = y[i - 1] + dydt[i - 1] * (x[i] - x[i - 1])
        y = y ** (1.0 / 1 + ex) * y0 ** (ex / (1 + ex))
        return y

    def third_order(self, x, u, y0, gain, lag, scale, damping, a3, d_gain_du=0, ex=0, u0=None, uniform_dx=None):
        """
        Calculates expected response to a given target waveform using a third order plus dead time (TOPDT) model

        Where I made up the third order expression and the exact implementation may not be standard.
        Because this isn't confirmed as a standard sys id model, it is not recommended for use.

        :param x: float array
            independent variable

        :param u: float array
            command or actuator history as a function of x

        :param y0: float
            Initial y value (y units)

        :param gain: float
            Gain = delta_y / delta_u: how much will response variable change given a change in command?
            Units  = y units / u units

        :param lag: float
            How long before a change in command begins to cause a change in response? (x units)

        :param scale: float
            Timescale for response (x units)

        :param damping: float
            unitless

        :param a3: float
            unitless factor associated with third order term

        :param d_gain_du: float
            Change in gain per change in u away from u0. This is normally exactly 0. Should you really change it?

        :param ex: float
            Exponent X for transforming to Y in in Y = y (y/y0)^X

        :param u0: float
            Reference value of u. Defaults to u[0].

        :param uniform_dx: bool
            x is evenly spaced

        :return: float array
            Expected response vs. time
        """
        uniform_dx = self['__fit_controls__']['uniform_dx'] if uniform_dx is None else uniform_dx
        warnings.warn(
            "This implementation of a third order model is not standard. "
            "Please use caution or maybe just another model. This is not a good idea. You shouldn't be doing this."
        )

        y = np.zeros(len(x)) + y0
        dydt = np.zeros(len(x))
        d2ydt2 = np.zeros(len(x))
        d3ydt3 = np.zeros(len(x))
        if uniform_dx:
            ui = None
        else:
            ui = interp1d(x, u, bounds_error=False, fill_value=(u[0], u[-1]))
        u0 = u[0] if u0 is None else u0
        for i in range(3, len(x)):
            if uniform_dx:
                idu = i - 2 - int(np.round(lag / (x[i - 1] - x[i - 2])))
                du = u[np.min([np.max([0, idu]), len(x) - 1])] - u0
            else:
                du = ui(x[i - 2] - lag) - u0
            geff = gain + du * d_gain_du
            term1 = (geff * du - (y[i - 3] - y0)) / scale ** 3
            term2 = -2 * damping / scale ** 2 * dydt[i - 3]
            term3 = d2ydt2[i - 3] / scale
            d3ydt3[i - 3] = a3 * (term1 + term2 + term3)
            d2ydt2[i - 2] = d2ydt2[i - 3] + d3ydt3[i - 3] * (x[i - 2] - x[i - 3])
            dydt[i - 1] = dydt[i - 2] + d2ydt2[i - 2] * (x[i - 1] - x[i - 2])
            y[i] = y[i - 1] + dydt[i - 1] * (x[i] - x[i - 1])
        y = y ** (1.0 / 1 + ex) * y0 ** (ex / (1 + ex))
        return y

    def p_third_order(self, par, x, u):
        """Version of third_order() using Parameters"""
        return self.third_order(
            x,
            u,
            par['y0'].value,
            par['gain'].value,
            par['lag'].value,
            par['scale'].value,
            par['damping'].value,
            par['a3'].value,
            d_gain_du=par['d_gain_du'].value,
            ex=par['ex'].value,
        )

    # Fitting tools
    def make_first_order_guess(self, x, u, y):
        """
        Guesses parameters to use in the first order model

        :param x: 1d float array
            independent variable

        :param u: 1d float array
            command or target as a function of x

        :param y: 1d float array
            response as a function of x

        :return: list of 4 floats
            Guesses for y0, gain, lag, and scale
        """
        from scipy.signal import correlate

        # Guess gain
        du = u.max() - u.min()
        dy = y.max() - y.min()
        gain = dy / du
        if (np.nanmean(y) > y[0]) != (np.nanmean(u) > u[0]):
            gain *= -1

        # Guess lag
        y2 = np.append(np.append(np.zeros(len(x)) + y[0], y), np.zeros(len(x)) + y[-1])
        u2 = np.append(np.append(np.zeros(len(x)) + u[0], u), np.zeros(len(x)) + u[-1])
        dx = np.mean(np.diff(x))
        x2 = np.append(x[0] - np.arange(0, len(x))[::-1] * dx, x)
        x2 = np.append(x2, x[-1] + np.arange(0, len(x)) * dx)
        lags2 = -np.append(-x2[::-1] + x2[0], x2[1:] - x2[0])
        nn2 = np.arange(len(x2), 0, -1)
        nn2 = np.append(nn2[::-1], nn2[1:]) / 2.0
        c2 = correlate(u2, y2) / nn2
        lag = lags2[int(c2.argmax())]
        lag = max([lag, dx, (x.max() - x.min()) * 0.025])

        # Guess scale
        scale = self['__details__']['scale'] * 0.25

        # Guess y0
        if y[-1] > y[0]:
            y0 = y.min()
        else:
            y0 = y.max()

        return [y0, gain, lag, scale]

    def make_guess(self, x, y, u, order, guess=None, variable_gain=False, modified_y=False):
        """
        Guesses fit parameters

        :param x: float array

        :param y: float array

        :param u:  float array

        :param order: int

        :param guess: list of at least (2 + order) numbers

        :param variable_gain: bool
            This is NOT a standard option. Should you really touch it?

        :param modified_y: bool
            Transforms Y = y * (y/y_0)**ex, where ex is a new parameter

        :return: Parameters instance
        """
        from lmfit import Parameters

        guess = tolist(guess)
        if None in guess:
            if len(np.shape(x)) > 1:
                # X is 2d: we have several cases combined together. Guess them separately, then average.
                nx2 = np.shape(x)[1]
                guesses = np.zeros((4, nx2))
                for i in range(nx2):
                    guesses[:, i] = self.make_first_order_guess(x[:, i], u[:, i], y[:, i])
                new_guess = np.nanmean(guesses, axis=1)
                # For gain, average the magnitude first and then take the sign from the signed average.
                # The sign of the gain is a separate guess from its magnitude and we could've gotten it wrong.
                new_guess[1] = np.nanmean(abs(guesses[1, :])) * np.sign(new_guess[1])
            else:
                new_guess = self.make_first_order_guess(x, u, y)
            new_guess = tolist(new_guess)
            if order > 1:
                damping_guess = 0.6
                new_guess += [damping_guess]
            new_guess += [0]  # Default guess for variable gain for order 1 and 2 systems
            while len(new_guess) > len(guess):
                guess += [None]
            for i in range(len(guess)):
                if guess[i] is None:
                    guess[i] = new_guess[i]
        g = Parameters()
        dy = y.max() - y.min()
        dx = x.max() - x.min()
        du = u.max() - y.min()
        min_scale = np.nanmin(np.diff(x)) * 1e-1
        if order > 0:
            g.add('y0', value=guess[0], min=y.min() - dy, max=y.max() + dy)
            g.add('gain', value=guess[1], min=-dy / du * 10.0, max=dy / du * 10.0)
            g.add('lag', value=guess[2], min=0, max=dx * 0.9)
            g.add('scale', value=guess[3], min=min_scale, max=dx * 0.9)
            if order > 1:
                g.add('damping', value=guess[4], min=0, max=100)
            if order > 2:
                g.add('a3', value=1.0)
            if (len(guess) > 3 + order) and variable_gain:
                g.add('d_gain_du', value=guess[-1], vary=variable_gain)
            else:
                g.add('d_gain_du', value=0, vary=variable_gain)
            g.add('ex', value=0, vary=modified_y)
        else:
            raise ValueError('Order {} is unsupported. Unable to make guess.'.format(order))
        return guess, g

    def model_residual(self, par, x, u, y, y_err=None, order=None):
        """Prepares residual between data and model given some parameters, for use in minimization/fitting"""
        if order is None:
            order = self['__fit_controls__']['default_order']

        nx2 = np.shape(x)[1] if len(np.shape(x)) > 1 else 0
        residual = np.atleast_2d(np.zeros(np.shape(x)))
        if nx2 == 0:
            residual = residual.T
        for i in range(max([1, nx2])):
            if nx2 == 0:
                xi = x
                yi = y
                ui = u
            else:
                sel = ~np.isnan(x[:, i]) & ~np.isnan(y[:, i]) & ~np.isnan(u[:, i])
                xi = x[sel, i]
                yi = y[sel, i]
                ui = u[sel, i]
            if order == 1:
                model = self.p_first_order(par, xi, ui)
            elif order == 2:
                model = self.p_second_order(par, xi, ui)
            elif order == 3:
                model = self.p_third_order(par, xi, ui)
            else:
                raise OMFITexception('order must be 1, 2, or 3')
            # Track the actual end of the model, in case it clips NaNs off the end or something.
            # Short rows in y may be NaN padded, so "real" lengths could vary.
            nmi = len(model)
            self['__scratch__'][f'yi_{i}'] = yi
            self['__scratch__'][f'model_{i}'] = model
            self['__scratch__'][f'nmi_{i}'] = nmi
            self['__scratch__']['i'] = i
            self['__scratch__']['residual'] = residual
            residual[:nmi, i] += yi - model
        if nx2 == 0:  # Collapse unused extra dimension if x, y, u were purely 1d
            residual = residual[:, 0]

        if y_err is not None:
            y_err_nz = copy.copy(y_err)
            bad = (y_err == 0) | np.isnan(y_err)
            y_err_nz[bad] = 1
            residual /= y_err_nz
            residual[bad] = 0
            self['__scratch__']['y_err'] = y_err
            self['__scratch__']['y_err_nz'] = y_err_nz

        if np.any(np.isnan(residual)):
            print('isnan resid')

        return residual

    def fit_response_model(self, x, y, u, y_err=None, order=2, guess=None, name=None, npts=None, method=None, **kw):
        """
        Fits response /output data to actuator / command / input data

        :param x: float array
            Independent variable

        :param y: float array
            Output or response data

        :param u: float array
            Input data

        :param y_err: float array [optional]
            Uncertainty in y, matching units and dimensions of y. If omitted, it's assumed to be 1.

        :param order: int
            Order of the model, such as 1 or 2

        :param guess: list of floats [optional]
            Initial guesses for y0, gain, lag, timescale, and damping (2nd order only)

        :param name: string
            Tag name where detailed results are placed

        :param npts: int
            Downsample data if necessary to avoid fitting more than this many points

        :param method: string
            Minimization method, like 'nelder'

        :param kw: Additional keywords
            nan_policy: string
                Instructions for handling NaNs in model function output, like 'raise', 'propagate', or 'omit'
            xunits: string
            yunits: string
            uunits: string
            cmd: bool
                u is a command with potentially different units and scale than y,
                as opposed to a target, which should be similar to y.
            variable_gain: bool
                Gain is a linear function of command-command_0 instead of a constant. This is NOT standard.
            modified_y: bool
                Transforms Y = y*(y/y_0)^(ex), where ex is an additional parameter

        :return: lmfit minimzer result
        """
        from lmfit import minimize

        # Interpret keywords
        nan_policy = kw.pop('nan_policy', None)
        xunits = kw.pop('xunits', None)
        yunits = kw.pop('yunits', None)
        uunits = kw.pop('uunits', None)
        cmd = kw.pop('cmd', None)
        variable_gain = kw.pop('variable_gain', None)
        modified_y = kw.pop('modified_y', None)

        # Setup
        if name is None:
            name = self._pick_name(order, new_name=False)
        out = self[name] = SortedDict()
        if npts is None:
            npts = self['__fit_controls__']['npts']
        if method is None:
            method = out['method'] = self['__fit_controls__']['method']
        if nan_policy is None:
            nan_policy = out['nan_policy'] = self['__fit_controls__']['nan_policy']
        if variable_gain is None:
            variable_gain = out['variable_gain'] = self['__fit_controls__'].setdefault('variable_gain', False)
        if modified_y is None:
            modified_y = out['modified_y'] = self['__fit_controls__'].setdefault('modified_y', False)

        # Deal with resampling
        npts2 = min([len(x), npts])
        out['npts'] = npts
        xnew = np.linspace(x.min(), x.max(), npts2)
        if len(np.shape(x)) > 1:
            nx2 = np.shape(x)[1]
            ui = np.empty((npts2, nx2))
            ui[:] = np.NaN
            yi = copy.copy(ui)
            yei = copy.copy(ui) if y_err is not None else None
            for i in range(nx2):
                sel = ~np.isnan(y[:, i])
                yi[:, i] = interp1d(x[sel, i], y[sel, i], bounds_error=False, fill_value=np.NaN)(xnew)
                ui[:, i] = interp1d(x[sel, i], u[sel, i], bounds_error=False, fill_value=np.NaN)(xnew)
                if yei is not None:
                    yei[:, i] = interp1d(x[sel, i], y_err[sel, i], bounds_error=False, fill_value=np.NaN)(xnew)
            y = yi
            u = ui
            x = xnew[:, np.newaxis] + np.zeros((npts2, nx2))
            y_err = yei
        else:
            y = interp1d(x, y)(xnew)
            u = interp1d(x, u)(xnew)
            if y_err is not None:
                y_err = interp1d(x, y_err)(xnew)
            x = xnew
        self['__fit_controls__']['uniform_dx'] = True

        # Handle NaN/zero padding
        nanny = np.isnan(y) | np.isnan(u) | np.isnan(x)
        xc = copy.copy(x)
        yc = copy.copy(y)
        uc = copy.copy(u)
        y_errc = copy.copy(y_err)
        xc[nanny] = 0
        yc[nanny] = 0
        uc[nanny] = 0
        y_errc[nanny] = 0

        # Fill in basics and fit setup
        inp = out['inputs'] = SortedDict()
        inp.update(dict(x=x, y=y, u=u, y_err=y_err, xc=xc, yc=yc, uc=uc, y_errc=y_errc, xunits=xunits, yunits=yunits, uunits=uunits))
        out['u_is_command'] = cmd
        od = out['__details__'] = SortedDict()
        od['y0_units'] = yunits
        od['gain_units'] = '{} ({})^-1'.format(yunits, uunits) if yunits != uunits else ''
        od['lag_units'] = xunits
        od['scale_units'] = xunits
        if order >= 2:
            od['damping_units'] = ''

        # Make an initial guess at parameter values
        self.printq('    CA FIT: Input guess: {}'.format(guess))
        guess, g = out['guess'], out['g'] = self.make_guess(
            xc, yc, uc, order, guess=guess, variable_gain=variable_gain, modified_y=modified_y
        )
        out['guess_y'] = -self.model_residual(g, x, u, x * 0, y_err=None, order=order)
        self.printq('    CA FIT: Processed guess: {}'.format(guess))

        # Do the fit
        with warnings.catch_warnings():
            # Fit warnings are not really great to have, to the point that ignoring them isn't ideal.
            # On the other hand, there are enough of them for minor things that having them pop exceptions isn't a
            # good idea either. So, the policy should be 'always' or 'once'. Set to 'always' for now to reflect
            # that this warning is considered slightly more important than what I'm used to as the average warning
            # from OMFIt.
            warnings.filterwarnings('always', category=RuntimeWarning)
            fit_out = out['fit_out'] = minimize(
                self.model_residual, g, args=(xc, uc, yc, y_err, order), method=method, nan_policy=nan_policy
            )
        out['params'] = fit_out.params
        out['model_y'] = -self.model_residual(fit_out.params, x, u, x * 0, y_err=None, order=order)
        out['model_y'][nanny] = np.NaN

        # Secondary derived quantities
        if order == 2:
            self.calculate_time_domain_specs_order_2()

        return fit_out

    # Derived quantities and other post-processing of fit results
    def calculate_time_domain_specs_order_2(self):
        """Calculates control performance specifications in the time domain; valid for order 2 fits"""
        order = 2
        name = self['__fit_controls__']['fit_out_name_format'].format(order=order)
        p = self[name]['params']
        out = self[name]['time_domain_specs'] = SortedDict()

        d = p['damping'].value
        omega_n = 1.0 / p['scale'].value
        omega_d = omega_n * np.sqrt(1 - d ** 2) if d < 1 else 0

        out['rise_time'] = 1.8 / omega_n
        out['peak_time'] = np.pi / omega_d if d < 1 else np.NaN
        out['overshoot'] = np.exp(-np.pi * d / np.sqrt(1 - d ** 2)) * 100.0 if 0 <= d < 1 else 0.0
        out['settle_time'] = 4.6 / (d * omega_n)
        for a in ['rise', 'peak', 'settle']:
            self[name]['__details__']['{}_time_units'.format(a)] = self[name]['__details__']['scale_units']
        self[name]['__details__']['overshoot_units'] = '%'
        return

    # Plotting and plotting utilities
    def get_plot_data(self, order=None, x=None, y=None, u=None, y_err=None, **kw):
        """
        Sets up data for fit plot

        :return: tuple containing
            x, y, u (float arrays)
            y_err (float array or None)
            xunits, yunits, uunits (strings)
            name (string)
            cmd, annotate (bools)
            my, gy (float arrays)
            order, ishot (int)
        """
        name = kw.get('name', None)
        cmd = kw.get('cmd', None)
        annotate = kw.get('annotate', True)
        ishot = kw.get('ishot', None)
        xunits = kw.get('xunits', None)
        yunits = kw.get('yunits', None)
        uunits = kw.get('uunits', None)

        if name is None:
            if order is None:
                for potential_order in [1, 2]:
                    if self._pick_name(potential_order, new_name=False) in self:
                        order = potential_order
            name = self._pick_name(order, new_name=False)
        else:
            if order is None:
                tmp = self['__fit_controls__']['fit_out_name_format'].split('{order:}')
                order = name.split(tmp[0])[1].split(tmp[1])[0]

        fit_out = self[name]
        cmd = fit_out['u_is_command'] if cmd is None else cmd
        gy = fit_out['guess_y']
        my = fit_out.get('model_y', np.array([np.NaN] * len(gy)))
        if ('inputs' in fit_out) and (None in [x, y, u]):
            x = fit_out['inputs']['x']
            y = fit_out['inputs']['y']
            u = fit_out['inputs']['u']
            y_err = fit_out['inputs']['y_err']
        if ('inputs' in fit_out) and (None in [xunits, yunits, uunits]):
            xunits = fit_out['inputs']['xunits']
            yunits = fit_out['inputs']['yunits']
            uunits = fit_out['inputs']['uunits']
        if x is None:
            x = np.arange(len(my))
            xunits = ''
        if yunits is None:
            yunits = fit_out['__details__']['y0_units']
        if ishot is not None and len(np.shape(x)) > 1:
            x = x[:, ishot]
            y = y[:, ishot]
            u = u[:, ishot]
            my = my[:, ishot]
            gy = gy[:, ishot]
            if y_err is not None:
                y_err = y_err[:, ishot]
        return x, y, u, y_err, xunits, yunits, uunits, name, cmd, annotate, my, gy, order, ishot

    def plot_fit_response(self, order=None, x=None, y=None, u=None, y_err=None, extra_data=None, split=None, **kw):
        """
        Plots fit to response model

        :param order: int
            Order of the model to use. Must be already complete.

        :param x: float array
            Independent variable
            1D: single shot
            2D: multi-shot

        :param y: float array
            Response data as a function of x

        :param u: float array
            Target or command data as a function of x

        :param y_err: float array [optional]
            Uncertainty in y, matching shape and units of y

        :param extra_data: list of dicts [optional]
            Each item contains:
                value: float array (required). Must match dimensions of x or supply its own xx
                xx: dependent variable associated with value. Required if value isn't the same shape as x
                axes: 'y' or 'u', denoting whether quantity should be grouped w response or cmd/target (optional)
                label: string (optional)
                color: matplotlib color spec (optional)
                linestyle: matplotlib line style spec (optional)
                plotkw: dict: addtional plot keywords (optional)

        :param split: bool
            When plotting multiple shots, don't overlay them; make more subplots so each can be separate.
            Set to none to split when twod, and leave alone when only one shot is considered.

        :param kw: Additional keywords
            show_guess: bool [optional]
                Switches display of guesses on/off.
                Defaults to on for single shot mode and off for multi-shot mode.
            show_model: bool
                Switches display of fit model on/off. Defaults to on. One might want to turn it off if one needs to
                customize just this trace with a separate plot command later.
            xunits: string
            yunits: string
            uunits: string
            cmd: bool
                Treat u as a command with different units and scale than y, as opposed to a target,
                which should be comparable to y. Defaults to reading from the fit output.
            name: string
                Tag name of fit output
            annotate: bool
                Mark annotations on the plot. Ignored if X is 2D unless ishot is used to select a single shot.
            ishot: int or None
                If int, selects which column in multi-shot/2D input to plot. If None, plots all shots/column.
                Ignored if x is 1D.
                This is an index from 0, not an actual literal shot number.

        :return: (Figure instance, 2d array of Axes instances)
        """

        # Data gathering and setup
        x, y, u, y_err, xunits, yunits, uunits, name, cmd, annotate, my, gy, order, ishot = self.get_plot_data(order, x, y, u, y_err, **kw)
        show_guess = kw.pop('show_guess', None)
        show_model = kw.pop('show_model', True)
        fit_out = self[name]
        if 'fit_out' in fit_out:
            rcs = fit_out['fit_out'].redchi
        else:
            rcs = np.NaN

        twod = (ishot is None) and (len(np.shape(x)) > 1)
        show_guess = not twod if show_guess is None else show_guess
        mlw = rcParams['lines.linewidth'] * 1.25 + 1.25

        fig = kw.get('fig', None)
        if fig is None:
            fig = pyplot.gcf()
        if split is None:
            split = twod
        if split:
            columns = 1 + cmd
            if len(np.shape(x)) > 1:
                rows = np.shape(x)[1]
            else:
                rows = 1
        else:
            columns = 1
            rows = 1 + cmd
        axs = np.zeros((rows, columns)).astype(object)
        axs[0, 0] = fig.add_subplot(rows, columns, 1)
        for i in range(1, columns * rows):
            axs[i // columns, i % columns] = fig.add_subplot(rows, columns, i + 1, sharex=axs[0, 0])
        if split:
            axu = axs[:, 0]
            axy = axs[:, int(cmd)]
        else:
            axu = axs[0, 0]
            axy = axs[int(cmd), 0]
        for ax in axs[:-1, :].flatten():
            pyplot.setp(ax.get_xticklabels(), visible=False)

        if twod:
            # Plot 2D data, color by shot and rely on linestyle to distinguish

            # Handle color cycle
            n2 = np.shape(x)[1]
            colors = self['__plot__']['shot_color_cycle']
            while len(colors) < n2:
                colors += colors
            if len(np.atleast_1d(self['__details__']['shot'])) == n2:
                shots = np.atleast_1d(self['__details__']['shot'])
            else:
                shots = range(n2)

            for i, shot in enumerate(shots):
                if split:
                    axui = axu[i]
                    axyi = axy[i]
                else:
                    axui = axu
                    axyi = axy
                c = colors[i]
                # Command or input data
                if u is not None:
                    ct_label = 'Command #{}'.format(shot) if cmd else ('Target' if i == 0 else '')
                    axui.plot(x[:, i], u[:, i], color=c, label=ct_label, linestyle='-' if cmd else '-.')
                # Response or output data
                if y is not None:
                    m_label = 'Measurement #{}'.format(shot) if not cmd else 'Measurement' if i == 0 else ''
                    if y_err is None:
                        yi = y[:, i]
                    else:
                        yi = uarray(y[:, i], y_err[:, i])
                    uband(x[:, i], yi, ax=axyi, color=c, label=m_label)
                # Model data
                if show_model:
                    axyi.plot(
                        x[:, i],
                        my[:, i],
                        color=c,
                        label=r'Order {} model; red.$\chi^2$ = {:0.2f}'.format(order, rcs) if i == 0 else '',
                        ls='--',
                        lw=mlw,
                    )
                if show_guess:
                    axyi.plot(x[:, i], gy[:, i], color=c, label='Guess' if i == 0 else '', linestyle=':')
                # Extra data (for example, could be used to plot a target when u is a command & y is a measurement)
                if extra_data is not None:
                    for xd in extra_data:
                        axx = axui if xd.get('axes', None) == 'u' else axyi
                        v = xd.get('value', None)
                        xx = xd.get('xx', x)
                        ls = xd.get('linestyle', None)
                        lab = xd.get('label', '') if i == 0 else ''
                        plotkw = xd.get('plotkw', {})
                        if v is not None:
                            axx.plot(xx[:, i], v[:, i], color=c, linestyle=ls, label=lab, **plotkw)
        else:
            # Plot 1D data, color by plot settings
            if split:
                # With only one shot, there's no basis for splitting by shot, so collapse the shot axis
                axu = axu[0]
                axy = axy[0]
            # Input / command
            if u is not None:
                if cmd:
                    axu.plot(x, u, color=self['__plot__']['command_color'], label='Command')
                else:
                    axu.plot(x, u, color=self['__plot__']['target_color'], label='Target')
            # Output / response / measurement
            if y is not None:
                if y_err is None:
                    axy.plot(x, y, color=self['__plot__']['measurement_color'], label='Measurement')
                else:
                    uband(x, uarray(y, y_err), color=self['__plot__']['measurement_color'], label='Measurement')
            # Model
            if show_model:
                axy.plot(
                    x,
                    my,
                    color=self['__plot__']['model_color'],
                    label=r'Order {} model; red.$\chi^2$ = {:0.2f}'.format(order, rcs),
                    ls='--',
                    lw=mlw,
                )
            if show_guess:
                axy.plot(x, gy, color=self['__plot__']['guess_color'], label='Guess', linestyle=':')
            # Extra
            if extra_data is not None:
                for xd in extra_data:
                    axx = axu if xd.get('axes', None) == 'u' else axy
                    xx = xd.get('xx', x)
                    v = xd.get('value', None)
                    if len(np.shape(xx)) > 1:
                        xx = xx[:, ishot]
                        v = v[:, ishot]
                    ls = xd.get('linestyle', None)
                    lab = xd.get('label', '')
                    c = xd.get('color', None)
                    plotkw = xd.get('plotkw', {})
                    if v is not None:
                        axx.plot(xx, v, color=c, linestyle=ls, label=lab, **plotkw)

        # Label axes and annotate
        if xunits:
            axs[-1, 0].set_xlabel('({})'.format(xunits))
        if yunits:
            for axyi in np.atleast_1d(axy):
                axyi.set_ylabel('({})'.format(yunits))
        if uunits:
            for axui in np.atleast_1d(axu):
                axui.set_ylabel('({})'.format(uunits))
        if annotate and not twod and order > 0:
            # These annotations won't work well on multi-shot (2D) input data
            # Annotations are for typical 1st and 2nd order models, not weird custom models
            self._annotate_fit_plot(axu, axy, x, y, u, xunits, yunits, uunits, name)

        for ax in axs.flatten():
            ax.legend(loc=0)
        self.auto_cornernote(ax=axs.flatten()[0], no_multishot=True, ishot=ishot)
        return fig, axs

    def auto_cornernote(self, ax=None, no_multishot=False, ishot=None):
        """
        Applies labels to a plot using user-supplied information about the case being analyzed

        If information is missing, labels may be skipped.

        :param ax: Axes instance
            These axes will be given a title reflecting the topic under investigation, if it is known

        :param no_multishot: bool
            Suppress shot if it's an iterable

        :param ishot: int or None
            Select just one shot when the instance is using multiple
        """
        topic = self['__details__'].get('topic', None)
        if topic is not None and ax is not None:
            ax.set_title(topic)
        dv = self['__details__'].get('device', None)
        shs = self['__details__'].get('shot', None)
        if ishot is not None and (len(np.atleast_1d(shs)) > ishot):
            sh = shs[ishot]
        else:
            sh = shs
        if no_multishot and (len(np.atleast_1d(sh)) > 1):
            sh = None
        cornernote(ax=ax, device='' if dv is None else dv, shot='' if (sh is None) else sh, time='')
        return

    def _annotate_fit_plot(self, axu, axy, x, y, u, xunits, yunits, uunits, name, time_response=True):
        """
        Applies annotations to the pyplot.plot(s) generated by plot_fit_response()

        :param axu: Axes instance
            The axes to use for command or target plots

        :param axy:
            The axes to use for response plots (may be the same as axu)

        (the remaining keywords are the same as those input to plot_fit_response)

        :param x: float array
            Independent variable

        :param y: float array
            Response data as a function of x

        :param u: float array
            Target or command data as a function of x

        :param xunits: string

        :param yunits: string

        :param uunits: string

        :param name: string
            Tag name of fit output

        :param time_response: bool
            Show time response data
        """

        fit_out = self[name]

        if 'params' in fit_out:
            y0 = fit_out['params']['y0'].value
            gain = fit_out['params']['gain'].value
            lag = fit_out['params']['lag'].value
            scale = fit_out['params']['scale'].value
            damping = fit_out['params'].get('damping', None)
            if damping is not None:
                damping = damping.value
        else:
            y0 = gain = lag = scale = damping = np.NaN

        u0 = u[0]
        uf = np.median(u[-int(np.ceil(len(u) / 10.0)) :])
        yf = y0 + (uf - u0) * gain
        if yunits == uunits:
            gunits = ''
        else:
            gunits = '{} ({})$^{{-1}}$'.format(yunits, uunits)

        us = self._smooth(x, u)
        ysg = self._smooth(x, y) / gain
        du_sign = np.sign(np.nanmean(u) - u0)
        duss = '+' if du_sign > 0 else '-'
        dy_sign = du_sign * np.sign(gain)
        i0 = (deriv(x, us) * du_sign + dy_sign * deriv(x, ysg) * 0.01).argmax()
        x0 = x[i0]

        time_response = time_response and 'time_domain_specs' in fit_out
        if time_response:
            x_rise = fit_out['time_domain_specs']['rise_time']
            x_peak = fit_out['time_domain_specs']['peak_time']
            x_settle = fit_out['time_domain_specs']['settle_time']
            ovs = fit_out['time_domain_specs']['overshoot']
        else:
            x_rise = x_peak = x_settle = ovs = None

        axy.axhline(y0, color=self['__plot__']['model_color'], linestyle='--', label='$y_0$ = {:0.3f} {}'.format(y0, yunits))
        axy.axhline(
            yf,
            color=self['__plot__']['model_color'],
            linestyle='-.',
            label=r'$\approx\Delta u \times K_s$;  $K_s$ = {:0.3f} {}'.format(gain, gunits),
        )
        for i, ax in enumerate({axu, axy}):
            ax.axvline(
                x0,
                color=self['__plot__']['command_color'],
                linestyle='--',
                label=r'$x_0$ = {:0.3f} {} (fastest {}change)'.format(x0, xunits, duss) if i == 0 else '',
            )
        axy.axvline(
            x0 + lag, color=self['__plot__']['model_color'], linestyle='--', label=r'$x_0 + L$;  L = {:0.3f} {}'.format(lag, xunits)
        )
        axy.axvline(
            x0 + lag + scale,
            color=self['__plot__']['model_color'],
            linestyle=':',
            label=r'$x_0 + L + \tau$;  $\tau$ = {:0.3f} {}'.format(scale, xunits),
        )
        if damping is not None:
            axy.plot(x[0], y[0], ls=' ', alpha=0, color='w', label=r'Damping $\xi$ = {:0.3f}'.format(damping))

        if time_response:
            dxr = abs((x_settle - x_rise) / 2.0 if np.isnan(x_peak) else (x_peak - x_rise) / 2.0)
            xr = x0 + dxr + x_rise
            axy.axvline(xr, color='k', ls='--', ymax=0.35, label='Rise time = {:0.3f} {}'.format(x_rise, xunits))
            axy.axvline(x0 + dxr, color='k', ls='--', ymax=0.35)
            if not np.isnan(x_peak):
                axy.axvline(x0 + x_peak, color='k', ls='-.', ymax=0.3, label='Peak time = {:0.3f} {}'.format(x_peak, xunits))
            axy.axvline(x0 + x_settle, color='k', ls=':', ymax=0.25, label='Settle time = {:0.3f} {}'.format(x_settle, xunits))
            if ovs > 0:
                ovsl = yf + yf * np.sign(yf - y0) * ovs / 100.0
                axy.axhline(ovsl, xmin=0.75, label='Overshoot = {:0.1f}%'.format(ovs), color='k')
        return

    # Other reporting tools
    def printq(self, *args):
        """Shortcut for printd with a centrally controlled and consistent topic"""
        return printd(*args, topic=self['__details__']['debug_topic'])

    def _print_report_formatted(self, label, x, units, guess=None):
        """
        Helper function for printing individual lines in a report

        :param label: string

        :param x: object

        :param units: string

        :param guess: float [optional]
        """
        if x is None or isinstance(x, str):
            the_form = '{:>40s} = {:12s} {:10s}'
        elif isinstance(x, int) and (abs(x) <= 999):
            the_form = '{:>40s} = {:+4d}        {:10s}'
        elif x == 0:
            the_form = '{:>40s} = {:4.0f}         {:10s}'
        elif (abs(x) >= 999) or (abs(x) < 1e-2) and (not np.isnan(x)):
            the_form = '{:>40s} = {:+12.3e} {:10s}'
        else:
            the_form = '{:>40s} = {:+8.3f}     {:10s}'
        self.printq(
            '    print_report_formatted: the_form = {}, x = {}, type(x) = {}, label = {}, units = {}'.format(
                the_form, x, type(x), label, units
            )
        )
        line = the_form.format(label, x, '' if units is None else units)
        line = line.replace(' +nan', '  N/A')
        if guess is not None:
            line += '  (guess = {:+0.3f})'.format(guess)
        print(line)
        return

    def fit_report(self, orders=None, notes=None):
        """Prints a report with key scalar metrics"""
        orders = [1, 2] if orders is None else orders
        for i, order in enumerate(orders):
            name = self['__fit_controls__']['fit_out_name_format'].format(**locals())
            if name in self:
                # Announce the category we're reporting
                out = self[name]
                par = out['params']
                pretty_name = name.replace('_', ' ').strip()
                pretty_name = pretty_name[0].upper() + pretty_name[1:]
                print(pretty_name)
                if notes is not None and len(tolist(notes)) > i:
                    print(tolist(notes)[i])

                # Display primary fit variables
                tags = ['y0', 'gain', 'lag', 'scale']
                if order >= 2:
                    tags += ['damping']
                for tag in tags:
                    g = out['g'][tag].value
                    self._print_report_formatted(tag, par[tag].value, out['__details__'].get('{}_units'.format(tag), ''), g)
                print()

                # Secondary quantities derived from the fit
                if 'time_domain_specs' in out:
                    for tag in out['time_domain_specs']:
                        pretty_tag = tag.replace('_', ' ').strip()
                        pretty_tag = pretty_tag[0].upper() + pretty_tag[1:]
                        self._print_report_formatted(
                            pretty_tag, out['time_domain_specs'][tag], out['__details__'].get('{}_units'.format(tag), '')
                        )
                    print()

                # Other fit quality metrics (number of iterations, etc.)
                pretty_names = SortedDict(
                    [
                        ['message', 'Status message'],
                        ['success', 'Success'],
                        ['nit', 'Number of iterations'],
                        ['chisqr', 'chi^2'],
                        ['redchi', 'reduced chi^2'],
                    ]
                )
                self._print_report_formatted('fit method', out.get('method', None), '')
                for tag in pretty_names:
                    label = '{} ({})'.format(pretty_names[tag], tag)
                    x = getattr(out['fit_out'], tag, None)
                    self._print_report_formatted(label, x, '')
            print()
        return

    def complain(self, quiet=False, no_good_news=True):
        """
        Prints or returns problems from self['__details__']['problems'], sorted by severity
        :param quiet: bool
            Don't actually print, just return the formatted report as a string
        :param no_good_news: bool
            No print unless there's a problem to complain about
        :return: string
            The formatted report, which is printed by default
        """
        problems = self['__details__']['problems']
        if len(problems):
            trouble = ['Problems encountered in {}:'.format(self.__class__.__name__)]
            trouble += ['-' * len(trouble[0])]
            sev = np.max(list(problems.values()))
            form = '{{:{}s}}: {{}} ({{}})'.format(np.max([len(k) for k in problems]))
            for desc in sorted(problems, key=lambda x: problems[x])[::-1]:
                line = form.format(desc, problems[desc], self['__details__']['problem_severity_scale'][problems[desc]])
                trouble += [line]
        else:
            trouble = ['No problems in {} so far'.format(self.__class__.__name__)]
            sev = 0

        trouble = '\n'.join(trouble)
        if not quiet:
            if sev < 2:
                if no_good_news and sev == 0:
                    return trouble
                printi(trouble)
            elif sev < 4:
                print(trouble)
            elif sev < 7:
                printw(trouble)
            else:
                printe(trouble)
        return trouble

    def __tree_repr__(self):
        problems = self['__details__']['problems']
        if len(problems):
            severity = self['__details__']['problem_severity_scale']
            qual = self['__details__']['problem_severity_qualitative_scale']
            worst_problem = max(problems.values())
            problem_description = (
                f"{len(problems)} problem(s)! Severity = {worst_problem}/{max(severity.keys())} "
                f"({qual[worst_problem]}): {severity[worst_problem]}"
            )
            # tags = ['BG_gold']  # This would work, but is it a good idea? ... maybe not. Think about it.
            tags = []
        else:
            problem_description = 'Okay'
            tags = []

        return problem_description, tags

    # End of class ControlAnalysis


class SystemIdentification(ControlAnalysis):
    """
    Manages fits to control responses to commands to identify system parameters
    """

    def __init__(self, x=None, response=None, command=None, response_uncertainty=None, target=None, order=2, **kw):
        """
        :param x: float array
            Independent variable; can be used for weighting steps in case of uneven spacing of data
            Single shot mode: x should be 1D
            Multi-shot mode: x should be 2D, with x[:, i] being the entry for shot i.
                If some shots have shorter x than others, pad the end with NaNs to get consistent length.
                Variables like gain, lag, and scale will be fit across all shots together
                assuming that the same system is being studied in each.
        :param response: float array matching shape of x
            Dependent variable as a function of x.
            These are actual measurements of the quantity that the system tried to control.
        :param command: float array matching shape of x
            Dependent variable as a function of x
            This is the command that was used to try to produce a response in y
        :param response_uncertainty: float array [optional]
            Uncertainty in response, matching dimensions and units of response. Defaults to 1.
        :param order: int
        :param time_range: two element numeric iterable in x units
            Used to control gathering of data if x, response, command, and target aren't supplied directly.
            If x units are converted using ???_x_factor, specify time_range in final units after conversion.
        :param [response, command, target, enable]_pointname: string
            Alternative to supplying x, y data for response, command, or target.
            Requires the following to be defined:
                device
                shot
                time_range
            Also considers the following, if supplied:
                ???_treename
                ???_x_factor
                ???_y_factor
            Where ??? is one of [response, command, target]
        :param [response, command, target, enable]_treename: string or None
            string: MDSplus tree to use as data source for [response, command, or target]
            None: Use PTDATA
        :param [response, command, target, enable]_x_factor: float
            Multiply x data by this * overall_x_factor.
            All factors are applied immediately after gathering from MDSplus and before performing any operations
            or comparisons. All effective factors are the product of an individual factor and an overall factor.
            So, response x data are mds.dim_of(0) * response_x_factor * overall_x_factor
        :param enable_value: float
            If supplied, data gathered using enable_pointname and enable_treename must be equal to this value in
            order for the command to be non-zero.
        :param [response, command, target, enable]_y_factor: float
        :param smooth_response: bool
            Smooth response data before further processing.
            Helpful if signal is polluted with irrelevant high frequency noise.
        :param overall_x_factor: float
        :param overall_y_factor: float
        :param response_units: string
        :param command_units: string
        :param time_units: string
            Default order of the control model to use. 1 or 2 for now. Can override later when calling fit.
        :param kw: Keywords passed to secondary setup methods
        """
        # Setup structure
        super().__init__(**kw)
        self['history'] = SortedDict()
        self['__fit_controls__']['fit_out_name_format'] = 'order_{order:}_system_identification_fit'

        # Process pointname, treename, and rescale factor instructions for gathering data from MDSplus, as would be
        # needed in case float arrays for the key quantities are not directly supplied.
        quantities = ['response', 'command', 'target', 'enable']
        for q in quantities:
            for pt, ptd in zip(['pointname', 'treename', 'x_factor', 'y_factor'], ['', None, 1, 1]):
                self['__details__']['{}_{}'.format(q, pt)] = self._pop_kw('{}_{}'.format(q, pt), ptd, kw)

        # Process keywords
        self['__details__']['overall_x_factor'] = self._pop_kw(
            'overall_x_factor', 1e-3 if is_device(self['__details__'].get('device', None), 'DIII-D') else 1, kw
        )
        self['__details__']['overall_y_factor'] = self._pop_kw('overall_y_factor', 1, kw)
        self['__details__']['response_units'] = self._pop_kw('response_units', None, kw)
        self['__details__']['command_units'] = self._pop_kw('command_units', None, kw)
        self['__details__']['response_uncertainty_pointname'] = self._pop_kw('response_uncertainty_pointname', None, kw)
        self['__details__']['enable_value'] = self._pop_kw('enable_value', None, kw)
        self['__details__']['smooth_response'] = kw.pop('smooth_response', False)
        self['__fit_controls__']['default_order'] = order
        quiet_dummy = kw.pop('quiet_dummy', True)

        # Handle key quantities
        self['history']['x'] = x
        if x is not None:  # Only load other data if x exists. If we don't have x, just gather everything
            self['history']['response'] = response
            self['history']['command'] = command
            self['history']['target'] = target
            self['history']['response_uncertainty'] = response_uncertainty
            self['history']['enable'] = self._pop_kw('enable', None, kw)
        # Gather data as needed
        for q in quantities + ['response_uncertainty', 'enable']:
            self._fetch_data(q)  # Fetching skips itself if data are already present or the pointname is missing
        self._cleanup_units()

        # Process enable flag
        if self['history']['enable'] is not None and self['__details__']['enable_value'] is not None:
            # Suppress command when enable flag does not match designated value
            self['history']['raw_command'] = copy.copy(self['history']['command'])
            self['history']['command'][self['history']['enable'] != self['__details__']['enable_value']] = 0

        # Run calculations
        if self['history']['x'] is not None and len(self['history']['x']):
            self._setup_calcs(**kw)
            self._setup_smooth(self['history']['x'], self['history']['response'], **kw)
            if self['__details__']['smooth_response']:
                self['history']['raw_response'] = copy.copy(self['history']['response'])
                if self['__details__']['smoother'] == 'median_filter' and 'response_pointname' in self['__details__']:
                    del self['history']['response']
                    self._fetch_data('response', smooth_first=True)
                else:
                    self['history']['response'] = self._smooth(self['history']['x'], self['history']['raw_response'])

            if self['history']['response_uncertainty'] is None:
                self.estimate_uncertainty('response')
        else:
            if not quiet_dummy:
                cn = self.__class__.__name__
                printw(f'Warning: no x data were supplied. This {cn} instance will not be very useful.')
            self['__details__']['problems']['Missing basic data'] = 8

        # Finalize setup
        self._rdb_setup(rdb_tag='sys', **kw)
        self.complain(quiet=quiet_dummy, no_good_news=True)
        return

    def fit(self, order=None, guess=None, **kw):
        """
        Fit measured response data to modeled response to a given command
        :param order: int
            Order of the model: 1 or 2
        :param guess: list of numbers
            Guesses for y0, gain, lag, scale, and (2nd order only) damping
        :param kw: additional keywords passed to fit_response_model:
            variable_gain: bool
                False: STANDARD! USE THIS UNLESS YOU'RE OUT OF OPTIONS! Gain is a constant
                True: gain is a linear function of command - command_0
        :return: Minimizer result
        """
        if order is None:
            order = self['__fit_controls__']['default_order']
        x = self['history']['x']
        y = self['history']['response']
        u = self['history']['command']
        y_err = self['history'].get('response_uncertainty', None)
        xu = self['__details__']['time_units']
        yu = self['__details__']['response_units']
        uu = self['__details__']['command_units']
        fit_out = self.fit_response_model(x, y, u, y_err=y_err, order=order, guess=guess, yunits=yu, xunits=xu, uunits=uu, cmd=True, **kw)
        return fit_out

    def plot_input_data(self, show_target=True, fig=None):
        """
        Plots data from history, such as command and response
        """
        x = self['history']['x']
        blank = x * np.NaN
        raw_response = self['history'].get('raw_response', blank)
        response = self['history'].get('response', blank)
        response_uncertainty = self['history'].get('response_uncertainty', np.zeros(len(x)))
        command = self['history'].get('command', blank)
        enable = self['history'].get('enable', None)
        target = self['history'].get('target', None)

        if fig is None:
            fig, axs = pyplot.subplots(2, sharex=True)
        else:
            ax0 = fig.add_subplot(211)
            ax1 = fig.add_subplot(212, sharex=ax0)
            axs = [ax0, ax1]
            ax0.xaxis.set_ticklabels([])
        axs[-1].set_xlabel(f"t / {self['__details__'].get('time_units', '?')}")
        axs[0].set_ylabel(f"Command / {self['__details__'].get('command_units', '?')}")
        axs[0].plot(x, command, label='command')
        if enable is not None:
            axb = axs[0].twinx()
            axb.plot(x, enable, linestyle='--')
        axs[1].set_ylabel(f"Response / {self['__details__'].get('response_units', '?')}")
        axs[1].plot(x, raw_response, color='r', alpha=0.3, label='raw')
        uband(x, uarray(response, response_uncertainty), color='b', label='response', ax=axs[1])

        if show_target and target is not None:
            axs[1].plot(x, target, label='target')

        for ax in axs:
            ax.legend(loc=0)
        self.auto_cornernote(axs[0])

        return fig, axs

    def plot(self, show_target=True, **kw):
        """
        Wrapper for ControlAnalysis.plot_fit_response() that can add extra data to include the target

        :param show_target: bool
            Add target as extra data

        :param kw: Additional keywords passed to plot_fit_response()

        :return: (Figure instance, array of Axes instances)
        """
        fig = kw.setdefault('fig', pyplot.gcf())

        if kw.get('order', None) is None:
            for i in range(1, 4):
                if f'order_{i}_system_identification_fit' in self:
                    kw['order'] = i
                    break

        if (kw.get('order', None) == 0) or (kw.get('order', None) is None):
            return self.plot_input_data(show_target=show_target, fig=fig)

        extra_data = kw.pop('extra_data', [])
        if show_target:
            extra_data += [
                {
                    'xx': self['history']['x'],
                    'value': self['history']['target'],
                    'label': 'Target',
                    'linestyle': '-.',
                    'color': self['__plot__']['target_color'],
                    'axes': 'y',
                    'plotkw': {'alpha': 0.5},
                }
            ]

        fig, axs = self.plot_fit_response(extra_data=extra_data, **kw)
        return fig, axs

    def report(self, orders=None):
        """
        Prints results of fits.

        :param orders: list [optional]
            Sets which fit results are selected. [1, 2] prints order 1 and order 2 fit results.
        """
        if orders is None:
            orders = [1, 2]
        case = self['__details__']['case']
        if case is not None:
            print(case)
            print('-' * len(case))
        self.fit_report(
            orders=orders,
            notes=[
                '    The command may be generated by a feedback control system.\n'
                '    The system identification does not include the system which generated the command.'
            ]
            * len(orders),
        )
        return

    # End of class SystemIdentification


class ControlQuality(ControlAnalysis):
    """
    Calculates metrics for control quality
    """

    def __init__(self, x=None, measurement=None, target=None, measurement_uncertainty=None, xwin=None, **kw):
        """
        :param x: float array
            Independent variable; can be used for weighting steps in case of uneven spacing of data
        :param measurement: float array
            Dependent variable as a function of x.
            These are actual measurements of the quantity that the system tried to control.
        :param target: float or float array
            Dependent variable as a function of x, or a scalar value.
            This is the target for measurement. Perfect control would be measurement = target at every point.
        :param measurement_uncertainty: float array [optional]
            Uncertainty in measurement in matching dimensions and units. If not supplied, it will be estimated.
        :param enable: float array [optional]
            Enable switch. Don't count activity when control is disabled.
            Disabled means when the enable switch doesn't match enable_value.
        :param command: float array [optional]
            Command to the actuator.
            Some plots will be skipped if this is not provided, but most analysis can continue.
        :param xwin: list of two-element numeric iterables in units of x
            Windows for computing some control metrics, like integral_square_error.
            You can use this to highlight some step changes in the target and get responses to different steps.
        :param units: string
            Units of measurement and target
        :param command_units: string [optional]
            Units of command, if supplied. Used for display.
        :param time_units: string
            Units of x
            Used for display, so quote units after applying overall_x_factor or measurement_x_factor, etc.
        :param time_range: two element numeric iterable in x units
            Used to control gathering of data if x, response, command, and target aren't supplied directly.
            If x units are converted using ???_x_factor, specify time_range in final units after conversion.
        :param [measurement, target, measurement_uncertainty, enable, command]_pointname: string
            Alternative to supplying x, y data for measurement, target, measurement_uncertainty, enable, or command.
            Requires the following to be defined:
                device
                shot
                time_range
            Also considers the following, if supplied:
                ???_treename
                ???_x_factor
                ???_y_factor
            Where ??? is one of [measurement, target, measurement_uncertainty]
        :param [measurement, target, enable, command]_treename: string or None
            string: MDSplus tree to use as data source for measurement or target
            None: Use PTDATA
        :param [measurement, target, enable, command]_x_factor: float
            Multiply x data by this * overall_x_factor.
            All factors are applied immediately after gathering from MDSplus and before performing any operations
            or comparisons. All effective factors are the product of an individual factor and an overall factor.
            So, target x data are mds.dim_of(0) * target_x_factor * overall_x_factor
        :param [measurement target, enable, command]_y_factor: float
        :param enable_value: float
            enable must match this value for data to count toward metrics
        :param overall_x_factor: float
        :param overall_y_factor: float
        :param kw: Keywords passed to secondary setup methods
        """
        # Set up structure
        super().__init__(**kw)
        self['raw'] = SortedDict()
        self['normalized'] = SortedDict()
        self['history'] = SortedDict()
        self['__fit_controls__']['fit_out_name_format'] = 'order_{order:}_response_to_target'

        # Process pointnames, treenames, and re-scale factors for the various quantities;
        # to be used if float arrays are not supplied directly.
        quantities = ['measurement', 'target', 'enable', 'command']
        for q in quantities:
            for pt, ptd in zip(['pointname', 'treename', 'x_factor', 'y_factor'], ['', None, 1, 1]):
                self['__details__']['{}_{}'.format(q, pt)] = self._pop_kw('{}_{}'.format(q, pt), ptd, kw)

        # Process more keywords
        self['__details__']['allowed_to_make_effective_target'] = kw.pop('allowed_to_make_effective_target', True)
        self['__details__']['overall_x_factor'] = self._pop_kw(
            'overall_x_factor', 1e-3 if is_device(self['__details__'].get('device', None), 'DIII-D') else 1, kw
        )
        self['__details__']['overall_y_factor'] = self._pop_kw('overall_y_factor', 1, kw)
        self['__details__']['units'] = self._pop_kw('units', None, kw)
        self['__details__']['command_units'] = self._pop_kw('command_units', None, kw)
        self['__details__']['measurement_uncertainty_pointname'] = self._pop_kw('measurement_uncertainty_pointname', None, kw)
        self['__details__']['enable_value'] = self._pop_kw('enable_value', None, kw)
        self['__details__']['smooth_response'] = self._pop_kw('smooth_response', None, kw)
        quiet_dummy = kw.pop('quiet_dummy', True)
        self['__details__']['xwin'] = tolist(xwin)

        # Handle key quantities; may require gathering from MDSplus using *_pointname and *_treename instructions
        self['history']['x'] = x
        if x is not None:
            self['history']['measurement'] = measurement
            self['history']['target'] = target
            self['history']['measurement_uncertainty'] = measurement_uncertainty
            self['history']['enable'] = self._pop_kw('enable', None, kw)
            self['history']['command'] = self._pop_kw('command', None, kw)
        # Run the function for gathering data as needed
        for q in quantities + ['measurement_uncertainty', 'enable']:
            self._fetch_data(q)  # Fetching skips itself if data are already present

        # Figure out units
        avail_units = [
            self['__details__'].get('{}_units'.format(rf), None)
            for rf in ['target', 'measurement']
            if self['__details__'].get('{}_units'.format(rf), None)
        ]
        if not self['__details__']['units'] and len(avail_units):
            self['__details__']['units'] = max(set(avail_units), key=avail_units.count)
        self._cleanup_units(default_units=self['__details__']['units'])

        # Process enable flag
        if (
            self['history']['enable'] is not None
            and self['__details__']['enable_value'] is not None
            and self['history']['target'] is not None
        ):
            # Suppress target when enable flag does not match designated value
            self['history']['raw_target'] = copy.copy(self['history']['target'])
            self['history']['target'][self['history']['enable'] != self['__details__']['enable_value']] = np.NaN

        # Set up critical derived quantities
        if np.all([self['history'].get(a, None) is not None for a in ['measurement', 'target']]):
            self['history']['err'] = self['history']['measurement'] - self['history']['target']
        else:
            self['history']['err'] = None
            if not quiet_dummy:
                printw("ControlQuality doesn't have enough data to initialize properly. Starting a dummy instance...")

        # Run calculations
        if (self['history']['err'] is not None) and (self['history']['x'] is not None) and len(self['history']['x']):
            # noinspection PyBroadException
            try:
                self._setup_calcs(**kw)
                self._setup_smooth(self['history']['x'], self['history']['measurement'], **kw)
                if self['history']['measurement_uncertainty'] is None:
                    self.estimate_uncertainty('measurement')
                if self['__details__']['smooth_response']:
                    self['history']['raw_measurement'] = copy.copy(self['history']['measurement'])
                    if self['__details__']['smoother'] == 'median_filter' and 'measurement_pointname' in self['__details__']:
                        del self['history']['measurement']
                        self._fetch_data('measurement', smooth_first=True)
                    else:
                        self['history']['measurement'] = self._smooth(self['history']['x'], self['history']['raw_measurement'])
                self.calculate()
            except Exception as excp:
                printe(
                    "FAILED TO COMPLETE INIT! Details saved in " "self['__details__']['init_traceback']. ({}).".format(self.describe_case())
                )
                self['__details__']['init_exception'] = excp
                exc_type, exc_value, exc_tb = sys.exc_info()
                self['__details__']['init_traceback'] = traceback.format_exception(exc_type, exc_value, exc_tb)
                self['__details__']['problems']['Exception during init/basic calculations & setup'] = 8
                if not quiet_dummy:
                    printe('    '.join(['\n'] + self['__details__']['init_traceback'] + ['\n']))
                else:
                    self.printq(''.join(self['__details__']['init_traceback']))
            else:
                self['__details__']['init_exception'] = self['__details__']['init_traceback'] = None
        else:
            if not quiet_dummy:
                printw('WARNING! ControlQuality was not able to initialize everything. Are you missing some data?')
                self['__details__']['problems']['Missing basic data'] = 8

        # Finalize setup
        self._rdb_setup(rdb_tag='cq', **kw)
        self.complain(quiet=quiet_dummy, no_good_news=True)
        return

    def make_effective_target(self):
        """
        Assumes that turning on the control counts as changing the target and makes modifications

        Prepends history with a step where the target matches the initial measured value.
        Then if the measurement is initially about 12 eV and the control is turned on with
        a target of 5 eV, it will act like the target changed from 12 to 5.
        """
        save_unaltered = ['x', 'measurement', 'target', 'measurement_uncertainty']
        self['history']['unaltered'] = SortedDict()
        for su in save_unaltered:
            self['history']['unaltered'][su] = copy.copy(self['history'][su])

        x = self['history']['x']
        y = self['history']['measurement']
        early = y[x - x[0] <= self['__details__']['scale']]
        y0 = np.nanmean(early)
        dx0 = x[1] - x[0]

        self['history']['x'] = np.append(x[0] - dx0, x)
        self['history']['measurement'] = np.append(y0, y)
        target = self['history']['target'] = np.append(y0, self['history']['target'])
        if self['history']['measurement_uncertainty'] is not None:
            self['history']['measurement_uncertainty'] = np.append(np.nanstd(early), self['history']['measurement_uncertainty'])
        quantities_to_extend = [k for k, v in self['history'].items() if len(np.atleast_1d(v)) == len(x)]
        for qex in quantities_to_extend:
            if qex in self['history']:
                self['history'][qex] = np.append(np.NaN, self['history'][qex])

        self['summary']['target_varies'] = np.nanmax(abs(target)) - np.nanmin(abs(target)) > 1e-6
        return

    def calculate(self):
        """
        Runs calculations for evaluating control quality
        """
        # Shortcuts
        x = self['history']['x']
        err = self['history']['err']
        target = self['history']['target']

        # Normalizations
        # norm = self['summary']['norm'] = 1.0 / np.max(abs(self['history']['target']))
        norm = self['summary']['norm'] = 1.0 / np.sqrt(mean_trapz(self['history']['target'] ** 2, self['history']['x']))
        self['summary']['norm_units'] = '({})^-1'.format(self['__details__']['units']) if self['__details__']['units'] else ''
        if norm < 1e-14:  # This is just noise and the target is basically 0
            printw('Warning: norm is too small. It is essentially 0.')
            norm = self['summary']['norm'] = np.NaN
        if np.isnan(norm):
            printw('Warning: norm is NaN!')
        self['summary']['xnorm'] = 1.0 / (x.max() - x.min())
        self['summary']['xnorm_units'] = '({})^-1'.format(self['__details__']['time_units']) if self['__details__']['time_units'] else ''

        # Basics
        self['summary']['target_varies'] = ((np.max(abs(target)) - np.min(abs(target))) * norm) > 1e-6
        self['raw']['RMS_error'] = np.sqrt(mean_trapz(err ** 2, x))
        self['raw']['RMS_error_units'] = self['__details__']['units']
        self['raw']['time_interval'] = np.nanmax(self['history']['x']) - np.nanmin(self['history']['x'])
        self['raw']['time_interval_units'] = self['__details__']['time_units']
        self['normalized']['RMS_error'] = np.sqrt(mean_trapz((err * norm) ** 2))
        self['history']['RMS_error'] = np.sqrt(self._smooth(x, err ** 2))
        self['history']['RMS_error_norm'] = np.sqrt(self._smooth(x, (err * norm) ** 2))

        # Advanced calculations
        self.calculate_standard_metrics()
        self.calculate_tracking_metrics()
        return

    def calculate_standard_metrics(self):
        """
        Manages calculations of standard metrics and organizes results
        """
        # Shortcuts & setup
        x = self['history']['x']
        err = self['history']['err']
        norm = self['summary']['norm']
        xnorm = self['summary']['xnorm']
        units = self['__details__']['units']
        units2 = '({})^2'.format(units) if units else ''
        xunits = self['__details__']['time_units']
        xunits2 = '({})^2'.format(xunits) if xunits else ''

        d, h = self._calc_standard_metrics(x, err, '')
        self['history'].update(h)
        self['raw'].update(d)
        self['raw']['integral_square_error_units'] = ' '.join([u for u in [units2, xunits] if u])
        self['raw']['integral_absolute_error_units'] = ' '.join([u for u in [units, xunits] if u])
        self['raw']['integral_time_absolute_error_units'] = ' '.join([u for u in [units, xunits2] if u])

        d, h = self._calc_standard_metrics(x * xnorm, err * norm, '_norm')
        self['history'].update(h)
        self['normalized'].update(d)
        if self['__details__']['xwin'][0] is not None:
            self['windowed'] = [{}] * len(self['__details__']['xwin'])
            for i, xwin in enumerate(self['__details__']['xwin']):
                o = self['windowed'][i]
                o['xwin'] = xwin
                w = (x >= xwin[0]) & (x <= xwin[1])
                h, d = self._calc_standard_metrics(x[w], err[w], '')
                o['raw'] = d
                h, d = self._calc_standard_metrics((x * xnorm)[w], (err * norm)[w], 'norm')
                o['normalized'] = d
        return

    @staticmethod
    def _calc_standard_metrics(x, err, tag=''):
        """
        Does the inner part of standard control metric calculations. See
        http://www.online-courses.vissim.us/Strathclyde/measures_of_controlled_system_pe.htm

        :param x: float array
            Independent variable. May be normalized or cropped to a particular range
        :param err: float array
            Error between measurement and target as a function of x. May be normalized or cropped.
        :param tag: string ['optional']
            Append this item to the tag name before placing results in history.
            Avoids collisions between raw and normalized data. Suggestion: use '' and '_norm'.
        :return: (dict, dict)
            Dictionary of scalar results
            Dictionary of histories
        """
        h = SortedDict()
        d = SortedDict()
        ok = ~np.isnan(x) & ~np.isnan(err)
        empty = np.empty(len(x))
        empty[:] = np.NaN
        ise = copy.deepcopy(empty)
        iae = copy.deepcopy(empty)
        itae = copy.deepcopy(empty)
        ise[ok] = scipy.integrate.cumtrapz(err[ok] ** 2, x[ok], initial=0)
        iae[ok] = scipy.integrate.cumtrapz(abs(err[ok]), x[ok], initial=0)
        itae[ok] = scipy.integrate.cumtrapz(x[ok] * abs(err[ok]), x[ok], initial=0)
        h['integral_square_error{}'.format(tag)] = ise
        h['integral_absolute_error{}'.format(tag)] = iae
        h['integral_time_absolute_error{}'.format(tag)] = itae
        d['integral_square_error'] = ise[-1]
        d['integral_absolute_error'] = iae[-1]
        d['integral_time_absolute_error'] = itae[-1]
        return d, h

    def calculate_tracking_metrics(self):
        """Tries to quantify how bad the controller is with moving targets"""
        if not self['summary']['target_varies'] and self['__details__']['allowed_to_make_effective_target']:
            self.make_effective_target()

        if self['summary']['target_varies']:
            # Target tracking

            # Shortcuts
            x = self['history']['x']
            target = self['history']['target']
            err = self['history']['err']
            rms_err = self['history']['RMS_error']

            dtdx = self['history']['dtarget_dx'] = deriv(x, target)
            if self['__details__']['causal_smoothing']:
                smo_target = self['history']['smoothed_target'] = self._smooth(x, target)
                dtdxs = self['history']['dtarget_dx_smooth'] = deriv(x, smo_target)
            else:
                # Acausal smooth of target leads to edge effects and inaccurate deriv if signal starts out ramping,
                # so in this case we must smooth the deriv and integrate to get smoothed target
                dtdxs = self['history']['dtarget_dx_smooth'] = self._smooth(x, dtdx)
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=RuntimeWarning, message='underflow.*')
                    self['history']['smoothed_target'] = scipy.integrate.cumtrapz(dtdxs, x, initial=0) + target[0]

            # dedx = deriv(x, err)
            # target_timescale = mt / np.max(abs(dtdx))
            # rms_tt = np.sqrt(self._smooth(x, err**2, target_timescale))
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=RuntimeWarning)
                w = np.isfinite(dtdxs) & np.isfinite(rms_err)
                self['normalized']['lethargy'] = abs(np.corrcoef([dtdxs[w], rms_err[w]])[0, 1])
                w = np.isfinite(target) & np.isfinite(err)
                self['normalized']['scorn'] = abs(np.corrcoef([target[w], err[w]])[0, 1])
        else:
            for tq in ['scorn', 'lethargy']:
                self['normalized'][tq] = np.NaN  # Not applicable if target doesn't vary
            self['history']['smoothed_target'] = self['history']['target']
            self['history']['dtarget_dx'] = self['history']['dtarget_dx_smooth'] = self['history']['target'] * 0
        return

    def fit(self, order=2, guess=None, force=False):
        """
        Fits response (measurement) data to model response to change in target

        :param order: int
            Order of the model. Supported: 1 and 2

        :param guess: list of floats
            Guesses / initial values for y0, gain, lag, scale, and damping (2nd order only)

        :param force: bool
            Try to fit even if it seems like a bad idea

        :return: minimizer result
        """
        if (not self['summary'].get('target_varies', True)) and (not force):
            self['__details__']['problems']['Target does not vary; fitting does not make sense.'] = 6
            raise OMFITexception('Since the target does not appear to vary, trying to fit response is a bad idea.')
        x = self['history']['x']
        y = self['history']['measurement']
        y_err = self['history']['measurement_uncertainty']
        u = self['history']['target']

        ok = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(u) & ~np.isnan(y_err)

        units = self['__details__']['units']
        xunits = self['__details__']['time_units']
        fit_out = self.fit_response_model(
            x[ok], y[ok], u[ok], y_err=y_err[ok], order=order, guess=guess, xunits=xunits, yunits=units, uunits=units, cmd=False
        )
        self.calculate_fit_based_secondary_metrics(orders=[order])
        return fit_out

    def calculate_fit_based_secondary_metrics(self, orders=None):
        """Some models have formulae for calculating derived properties and control metrics"""
        if orders is None:
            orders = [1, 2]
        for order in orders:
            tag = self._pick_name(order, new_name=False)
            if tag in self:
                gain_error = self[tag]['params']['gain'].value - 1.0  # Ideally, gain should be 1.
                self['normalized']['gain_error_order_{}'.format(order)] = gain_error
        return

    def report(self, orders=None):
        """Prints a report with key scalar metrics"""
        case = self['__details__']['case']
        if case is not None:
            print(case)
            print('-' * len(case))
        for br in ['summary', 'raw', 'normalized']:
            print(br)
            for r in self[br]:
                if (not r.startswith('__')) and (not r.endswith('units')):
                    self._print_report_formatted(r, self[br][r], self[br].get('{}_units'.format(r), ''))
        if orders is None:
            orders = [1, 2]
        self.fit_report(
            orders=orders,
            notes=[
                '    The target is being treated as the command.\n'
                '    So, the controller is part of the system & gain should be exactly 1.'
            ]
            * len(orders),
        )
        return

    def _get_time_selector(self, x=None, time_range=None):
        """
        Get a mask for selecting time data based on being within a time_range

        :param x: float array

        :param time_range: sorted two element numeric iterable
            Units should match x

        :return: bool array matching length of x
        """
        if x is None:
            printe('Cannot make a mask for selecting slices for x = {}'.format(x))
            return None
        if time_range is None:
            time_range = self['__details__']['time_range']
        if time_range is None:
            w = np.ones(len(x), bool)
        else:
            w = (x >= time_range[0]) & (x <= time_range[1])
        return w

    def plot(self, time_range=None):
        """Plots key control quality data"""
        fig, axs = pyplot.subplots(3, 3)
        xunits = self['__details__']['time_units']
        if xunits:
            for ax in axs[-1, :]:
                ax.set_xlabel('({})'.format(xunits))
        self.subplot_main_quantities(axs[0, 0], time_range=time_range)
        self.subplot_errors(axs[1, 0], time_range=time_range)
        self.subplot_errors(axs[2, 0], norm=True, time_range=time_range)
        self.subplot_control_metrics(axs[1, 1], time_range=time_range)
        self.subplot_control_metrics(axs[2, 1], norm=True, time_range=time_range)
        self.subplot_pre_correlation(axs[0, 1], time_range=time_range)
        if self['history'].get('command', None) is not None:
            self.subplot_command(axs[0, 2], time_range=time_range)
            axs[0, 2].set_xlabel('({})'.format(xunits))
            axs[0, 0].get_shared_x_axes().join(axs[0, 0], axs[0, 2])
        else:
            axs[0, 2].axis('off')
        self.subplot_correlation(axs[1, 2], which='target', norm=False, time_range=time_range)
        self.subplot_correlation(axs[2, 2], which='dtdx', norm=False, time_range=time_range)

        for ax in axs[:, 0:2].flatten():
            axs[0, 0].get_shared_x_axes().join(axs[0, 0], ax)
        for ax in axs[0:2, 0:2].flatten():
            for tick in ax.xaxis.get_ticklabels():
                tick.set_visible(False)

        axs[0, 0].set_xlim(axs[0, 0].get_xlim())  # Something like this is needed to make shared x axes wake up
        device = self['__details__'].get('device', None)
        shot = self['__details__'].get('shot', None)
        if device is None:
            device = ''
        if shot is None:
            shot = ''
        cornernote(ax=axs[0, 0], device=device, shot=shot, time='', root=None)
        return

    def subplot_main_quantities(self, ax, time_range=None, **kw):
        """
        Plots primary quantities like measurement and target

        :param ax: Axes instance

        :param time_range: sorted two element numeric iterable [optional]
            Zoom into only part of the data by specifying a new time range in xunits (probably seconds).
            If not provided, the default time_range will be used.

        :param kw: extra keywords passed to pyplot.plot()
            Recommended: instead of setting color here, set
                self['__plot__']['target_color'] and self['__plot__']['measurement_color']
            Recommended: do not set label, as it will affect both the target and measurement
        """
        x = self['history']['x']
        if x is None:
            printw('Nothing to plot')
            return
        w = self._get_time_selector(x, time_range)
        wt = w & (x != x[0])  # Additional filter: don't show the target's first element b/c it can be eff tar

        kwt = copy.copy(kw)
        kwt.setdefault('color', self['__plot__']['target_color'])
        kwt.setdefault('label', 'Target')
        ax.plot(x[wt], self['history']['target'][wt], **kwt)
        kwm = copy.copy(kw)
        kwm.setdefault('color', self['__plot__']['measurement_color'])
        kwm.setdefault('label', 'Mesurement')
        ax.plot(x[w], self['history']['measurement'][w], **kwm)
        units = self['__details__']['units']
        if units:
            ax.set_ylabel('({})'.format(units))
        ax.legend(loc=0)
        return

    def subplot_errors(self, ax, norm=False, time_range=None, quote_avg=True, **kw):
        """
        Plots error between measurement and target

        :param ax: Axes instance

        :param norm: bool
            Normalize quantities based on typical independent and dependent data scales or intervals.
            The norm factors are in self['summary']['norm'] and self['summary']['xnorm']

        :param time_range: sorted two element numeric iterable [optional]
            Zoom into only part of the data by specifying a new time range in xunits (probably seconds).
            If not provided, the default time_range will be used.

        :param quote_avg: bool
            Include all-time average in a legend label

        :param kw: extra keywords passed to pyplot.plot()
            Recommended: don't set label as it will override both series drawn by this function
            Note: if alpha is set and numeric, the unsmoothed trace will have alpha *= 0.3
        """
        x = self['history']['x']
        if x is None:
            printw('Nothing to plot')
            return
        w = self._get_time_selector(x, time_range)

        if norm:
            norm = self['summary']['norm']
            norm_tag = ' (normalized)'
            unit_tag = ' (norm)'
        else:
            units = self['__details__']['units']
            if units:
                ax.set_ylabel('({})'.format(units))
                unit_tag = ' ({})'.format(units)
            else:
                unit_tag = ''
            norm = 1
            norm_tag = ''

        err = self['history']['err'] * norm
        rms_err = self['history']['RMS_error'] * norm
        rmserravg = np.sqrt(mean_trapz(err[w] ** 2, x[w]))
        if quote_avg:
            avg_tag = ', avg = {:0.3f}'.format(rmserravg, unit_tag)
        else:
            avg_tag = ''
        kw.setdefault('color', self['__plot__']['error_color'])
        kw1 = copy.copy(kw)
        kw1.setdefault('label', '|Error{}|'.format(norm_tag))
        if is_numeric(kw1.get('alpha', 1.0)):
            kw1['alpha'] = kw1.get('alpha', 1.0) * 0.3
        kw2 = copy.copy(kw)
        kw2.setdefault('label', 'RMS error' + norm_tag + avg_tag)

        ax.plot(x[w], abs(err[w]), **kw1)
        ax.plot(x[w], rms_err[w], **kw2)
        ax.legend(loc=0)
        ax.axhline(0, linestyle='--', color='k')
        return

    def subplot_control_metrics(self, ax, norm=False, time_range=None, **kw):
        """
        Plots classic control metrics vs time

        :param ax: Axes instance

        :param norm: bool

        :param time_range: sorted two element numeric iterable [optional]
            Zoom into only part of the data by specifying a new time range in xunits (probably seconds).
            If not provided, the default time_range will be used.

        :param kw: additional keywords passed to plot
            Recommended: do not set color this way. Instead, set the list self['__plot__']['other_error_colors']
            Recommended: do not set label this way. It will override all three traces' labels.
        """
        x = self['history']['x']
        if x is None:
            printw('Nothing to plot')
            return
        w = self._get_time_selector(x, time_range)

        for ii, ie in enumerate(['integral_square_error', 'integral_absolute_error', 'integral_time_absolute_error']):
            kwi = copy.copy(kw)
            lab = ie.replace('_', ' ')
            lab = lab[0].upper() + lab[1:]
            if norm:
                lab = '{} (normalized)'.format(lab)
            else:
                ieu = self['raw']['{}_units'.format(ie)]
                if ieu:
                    lab = '{} ({})'.format(lab, ieu)
            uie = ie + '_norm' if norm else ie
            kwi.setdefault('color', self['__plot__']['other_error_colors'][ii])
            kwi.setdefault('label', lab)
            ax.plot(x[w], self['history'][uie][w], **kwi)
        ax.legend(loc=0)
        return

    def subplot_pre_correlation(self, ax, norm=True, time_range=None, **kw):
        """
        Plot derivatives and stuff that goes into correlation tests

        :param ax: Axes instance

        :param norm: bool

        :param time_range: sorted two element numeric iterable [optional]
            Zoom into only part of the data by specifying a new time range in xunits (probably seconds).
            If not provided, the default time_range will be used.

        :param kw: extra keywords passed to plot
            Recommended: don't set label or color
            Alpha will be multiplied by 0.3 for some plots if it is numeric
        """
        x = self['history']['x']
        if x is None:
            printw('Nothing to plot')
            return
        w = self._get_time_selector(x, time_range)

        if norm:
            norm = self['summary']['norm']
            xnorm = self['summary']['xnorm']
            norm_tag = ' (normalized)'
        else:
            units = self['__details__']['units']
            if units:
                ax.set_ylabel('({})'.format(units))
            norm = xnorm = 1
            norm_tag = ''
        if is_numeric(kw.get('alpha', 1.0)):
            fade_alpha = kw.get('alpha', 1.0) * 0.3
        else:
            fade_alpha = kw.get('alpha', 1.0)
        kwt = copy.copy(kw)
        kwt.setdefault('color', self['__plot__']['target_color'])
        kwst = copy.copy(kwt)
        kwst.setdefault('label', 'Smoothed target' + norm_tag)
        kwt.setdefault('label', 'Target' + norm_tag)
        kwt['alpha'] = fade_alpha
        kwdt = copy.copy(kw)
        kwdt.setdefault('color', self['__plot__']['dtdx_color'])
        kwdts = copy.copy(kwdt)
        kwdts.setdefault('label', 'smooth(d(Target)/dx)' + norm_tag)
        kwdt.setdefault('label', 'd(Target)/dx' + norm_tag)
        kwdt['alpha'] = fade_alpha
        kwe = copy.copy(kw)
        kwe.setdefault('color', self['__plot__']['error_color'])
        kwes = copy.copy(kwe)
        kwes.setdefault('label', 'RMS error' + norm_tag)
        kwe.setdefault('label', 'Error' + norm_tag)
        kwe['alpha'] = fade_alpha

        ax.plot(x[w], self['history']['smoothed_target'][w] * norm, **kwst)
        ax.plot(x[w], self['history']['target'][w] * norm, **kwt)
        ax.plot(x[w], self['history']['dtarget_dx_smooth'][w] * norm / xnorm, **kwdts)
        ax.plot(x[w], self['history']['dtarget_dx'][w] * norm / xnorm, **kwdt)
        ax.plot(x[w], self['history']['RMS_error'][w] * norm, **kwes)
        ax.plot(x[w], self['history']['err'][w] * norm, **kwe)

        ax.legend(loc=0)
        ax.axhline(0, linestyle='--', color='k')
        return

    def subplot_correlation(self, ax, which='target', norm=True, time_range=None, **kw):
        """
        Plots error vs. other quantities, like rate of change of target

        :param ax: Axes instance

        :param which: string
            Controls the quantity on the x axis of the correlation plot
            'target' has a special meaning
            otherwise, it's d(target)/dx

        :param norm: bool

        :param time_range: sorted two element numeric iterable [optional]
            Zoom into only part of the data by specifying a new time range in xunits (probably seconds).
            If not provided, the default time_range will be used.

        :param kw: Additional keywords passed to pyplot.plot()
            Recommended: Don't set marker as it is set for both series
            If alpha is numeric, it will be multiplied by 0.3 for some data but not for others
        """
        x = self['history']['x']
        if x is None:
            printw('Nothing to plot')
            return
        w = self._get_time_selector(x, time_range)

        if norm:
            norm = self['summary']['norm']
            xnorm = self['summary']['xnorm']
            norm_tag = ' (normalized)'
            units = inv_time_units = ''
        else:
            norm = xnorm = 1
            units = self['__details__']['units']
            time_units = self['__details__']['time_units']
            if time_units is None:
                time_units = ''
            if len(time_units):
                inv_time_units = time_units + '$^{-1}$'
            else:
                inv_time_units = ''
            if units:
                norm_tag = ' ({})'.format(units)
            else:
                norm_tag = ''

        if units is None:
            units = ''

        if which == 'target':
            wtag = 'target'
            wtags = 'smoothed_target'
            co = self['__plot__']['target_color']
            xunits = units
            xlabel = 'Target'
            xnorm = 1
            corr = self['normalized']['scorn']
        else:
            wtag = 'dtarget_dx'
            wtags = 'dtarget_dx_smooth'
            co = self['__plot__']['dtdx_color']
            xunits = ' '.join([units, inv_time_units]).strip()
            xlabel = 'd(Target)/dx'
            corr = self['normalized']['lethargy']

        if xunits:
            xnorm_tag = ' ({})'.format(xunits)
        else:
            xnorm_tag = ''
        ax.set_xlabel(xlabel + xnorm_tag)
        ax.set_ylabel('Error' + norm_tag)

        kw.setdefault('color', co)
        kw.setdefault('linestyle', '')
        kw1 = copy.copy(kw)
        kw1.setdefault('marker', '.')
        kw2 = copy.copy(kw)
        kw2.setdefault('marker', ',')
        if is_numeric(kw2.get('alpha', 1.0)):
            kw2['alpha'] = kw2.get('alpha', 1.0) * 0.3
        ax.plot(self['history'][wtags][w] * norm / xnorm, self['history']['RMS_error'][w] * norm, **kw1)
        ax.plot(self['history'][wtag][w] * norm / xnorm, self['history']['err'][w] * norm, **kw2)
        if np.array_equal(time_range, self['__details__']['time_range']):
            # Didn't recompute corr yet, so don't display it unless it matches selected time range
            ax.text(0.95, 0.95, 'Correlation = {:0.3f}'.format(corr), ha='right', va='top', transform=ax.transAxes)
        return

    def subplot_command(self, ax, time_range=None, **kw):
        """
        Plots the actual command to the actuator vs. time

        :param ax: Axes instance

        :param time_range: sorted two element numeric iterable [optional]
            Zoom into only part of the data by specifying a new time range in xunits (probably seconds).
            If not provided, the default time_range will be used.

        :param kw: Additional keywords passed to pyplot.plot()
            Recommended: Don't set label as it will affect both series
            If it is numeric, alpha will be multiplied by 0.3 for some data but not others
        """
        x = self['history']['x']
        y = self['history']['command']
        if x is None:
            printw('Nothing to plot')
            return
        w = self._get_time_selector(x, time_range)

        cu = self['__details__']['command_units']
        if cu:
            ax.set_ylabel('({})'.format(cu))
        kw.setdefault('color', self['__plot__']['command_color'])
        kw1 = copy.copy(kw)
        kw1.setdefault('label', 'Command')
        if is_numeric(kw1.get('alpha', 1.0)):
            kw1['alpha'] = kw1.get('alpha', 1.0) * 0.3
        ax.plot(x[w], y[w], **kw1)
        # Extend x, y for smoothing slightly to include some non-activity outside the range (just a little).
        # Avoid making it look like the smooth command starts way higher than it really does due to
        # edge effects or whatever.
        dx = np.nanmean(np.diff(x))
        x0 = np.nanmin(x)
        x1 = np.nanmax(x)
        npad = 10
        pad0 = np.arange(x0 - dx * npad, x0, dx)
        pad1 = np.arange(x1 + dx, x1 + dx * (npad + 1), dx)
        ok = np.isfinite(x) & np.isfinite(y)
        x2 = np.append(np.append(pad0, x[ok]), pad1)
        y2 = np.append(np.append(np.zeros(len(pad0)), y[ok]), np.zeros(len(pad1)))
        y2s = self._smooth(x2, y2)
        w2 = self._get_time_selector(x2, time_range)

        kw.setdefault('label', 'Command (smoothed)')
        ax.plot(x2[w2], y2s[w2], **kw)
        ax.legend(loc=0)
        return

    # End of class ControlQuality
