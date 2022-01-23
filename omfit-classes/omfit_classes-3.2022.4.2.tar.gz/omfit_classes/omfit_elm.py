"""
Contains classes and functions to perform ELM detection and ELM filtering:
- OMFITelm class; main workhorse for ELM detection
- Some smoothing functions used by OMFITelm

The regression test for OMFITelm is in regression/test_OMFITelm.py
"""

try:
    # framework is running
    from .startup_choice import *

    framework = True
except ImportError as _excp:
    # class is imported by itself
    framework = False
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

import numpy as np
from numpy.core import shape, mean
import scipy.signal
from scipy.interpolate import interp1d
import unittest
import warnings
from matplotlib import pyplot
from scipy import constants

# noinspection PyBroadException
try:
    import MDSplus
except Exception:  # MDSplus raises Exception, so this can't be more narrow
    print('Error importing MDSplus in omfit_elm.py.')
    mds_available = False
else:
    mds_available = True

from omfit_classes.utils_base import printd, tolist, printw, printe
from omfit_classes.utils_fusion import is_device, tokamak
from omfit_classes.utils_math import smooth, smooth_by_convolution, pcs_rc_smooth, function_to_tree, dimens, butter_smooth, deriv
from omfit_classes.omfit_mds import OMFITmdsValue
from omfit_classes.omfit_rdb import OMFITrdb
from omfit_classes.exceptions_omfit import OMFITexception
from omfit_classes.omfit_testing import OMFITtest, manage_tests
from omfit_classes.omfit_eqdsk import read_basic_eq_from_mds
from omfit_classes.exceptions_omfit import doNotReportException as DoNotReportException

try:
    # This should work if launched from the command line in the right path
    from omfit.omfit_plot import cornernote
    from omfit.utils_plot import contrasting_color
    from omfit.utils_math import array_info

except ImportError:
    pass

__all__ = []


try:
    scratch = OMFIT['scratch'].setdefault('OMFITelm', SortedDict())
except (KeyError, NameError):
    scratch = {}


def _available_to_user(f):
    __all__.append(f.__name__)
    return f


class OMFITelmIncompatibleData(ValueError, DoNotReportException):
    """Input data (such as filterscope signals) can't be used with current settings"""


class OMFITelmNotSupported(ValueError, DoNotReportException):
    """One of the chosen settings is not supported or not yet implemented"""


@_available_to_user
def asym_gauss_smooth(x, y, s, lag, leading_side_width_factor):
    """
    This is a smoothing function with a Gaussian kernel that does not require evenly spaced data and allows the
    Gaussian center to be shifted.

    :param x: array
        Dependent variable

    :param y: array
        Independent variable

    :param s: float
        Sigma of tailing side (same units as x)

    :param lag: float
        Positive values shift the Gaussian kernel back in time to increase weight in the past:
        makes the result laggier. (same units as x)

    :param leading_side_width_factor: float
        The leading side sigma will be this much bigger than the tailing side. Values > 1 increase the weight on
        data from the past, making the signal laggier. (unitless)

    :return: array
        Smoothed version of y
    """

    rescale = max(y)
    y2 = y / rescale
    ys = y2 * 0
    n = len(y2)
    s2 = s  # Sigma for trailing side (future)
    s1 = s * leading_side_width_factor  # Sigma for leading side (past)
    mdx = np.mean(np.diff(x))  # Average delta x
    # We will make the smoothing kernel smaller than x or y to make the calculation faster.
    # That is, we will truncate the weighting function when it gets small.
    ahead = int(np.ceil(2 * s2 / mdx))  # How many indices ahead should the kernel go? (future)
    behind = int(np.ceil(2 * s1 / mdx))  # How many indices behind should the kernel go? (past)
    shift = int(round(lag / mdx))  # How big is in terms of number of elements?
    printd('sigma past = {}'.format(s1), topic='omfit_elm')
    printd('sigma future = {}'.format(s2), topic='omfit_elm')
    printd(
        'ahead = {ahead:} samples, {ahead_ms:} ms;   behind = {behind:} samples, {behind_ms:} ms; '
        'shift = {shift:} samples, {shift_ms:} ms'.format(
            ahead=ahead, ahead_ms=ahead * np.mean(np.diff(x)), behind=behind, behind_ms=behind * mdx, shift=shift, shift_ms=shift * mdx
        ),
        topic='omfit_elm',
    )
    for i in range(n):
        a = i - behind - shift  # a is the first element to be considered in this time window (past)
        if a < 0:
            a = 0
        b = i + ahead + 1 - shift  # b is the last element to be considered in this time window (future)
        ish = i - shift  # Index of the center of the Gaussian
        if b >= n:
            # If b goes off the end of the array, then y[a:b] will return fewer than b-a samples. Can't have that!
            b = n - 1
        if b <= a:
            # Lag setting may make a few slices impossible
            ys[i] = y2[i]
            continue
        if a >= b:
            ys[i] = y2[i]
            continue
        if ish <= 0 or ish >= (n - 1):
            ys[i] = y2[i]
            continue

        center = x[i] - lag
        dx = x - center
        kernel = np.zeros(b - a)
        ia = ish - a
        ba = b - a
        kernel[0:ia] = np.exp(-((dx[a:ish] / s1) ** 2) / 2.0)
        kernel[ia:ba] = np.exp(-((dx[ish:b] / s2) ** 2) / 2.0)
        kernel = kernel / np.sum(kernel)
        ys[i] = np.sum(y2[a:b] * kernel)

    ys *= rescale
    return ys


@_available_to_user
def fft_smooth(xx, yy, s):
    """
    Smooth by removing part of the spectrum in the frequency domain

    1. FFT
    2. Cut out part of the spectrum above some frequency
    3. Inverse FFT to get back to time domain. The result will be missing some of the high frequency variation.

    :param xx: 1D array
        Independent variable, such as time

    :param yy: 1D array matching length of xx
        Dependent variable

    :param s: float
        Smoothing timescale in units matching xx. The cutoff frequency is cut = 1/(s*pi)

    :return: 1D array matching length of xx
        Smoothed (lowpass) version of yy
    """
    # Assumes that xx data are evenly spaced!
    warnings.warn('WARNING: FFT smoother is fast but does not work well. Do not use unless experimenting!')
    # This might be salvageable with special tuning. I am not happy with it. It technically works and is FAST.
    if len(xx) % 2:
        # RFFT wants an even number of elements
        cut_last = True
        xx = np.append(xx, xx[-1] * 2 - xx[-2])
        yy = np.append(yy, yy[-1])
    else:
        cut_last = False
    rft = np.fft.rfft(yy)
    freq = np.fft.rfftfreq(len(yy), d=xx[1] - xx[0])
    cut = 1.0 / s / np.pi
    # Have amplitude decay exponentially above the cutoff frequency. This seems to work better than just setting to 0.
    rft[abs(freq) > cut] *= np.exp(-(abs(freq[abs(freq) > cut]) - cut) / cut)
    ys = np.fft.irfft(rft)
    if cut_last:
        ys = ys[:-1]
    return ys


@_available_to_user
class OMFITelm(SortedDict):
    """
    Quickly detect ELMs and run a filter that will tell you which time-slices are okay and which should be rejected
    based on user specifications for ELM phase, etc.
    """

    def __init__(
        self,
        device='DIII-D',
        shot=0,
        detection_settings=None,
        filter_settings=None,
        use_filterscopes=None,
        attempt_sum_tdi_filterscopoes=False,
        debug=False,
        debug_plots=False,
        on_failure='exception',
        mode='elm',
        quiet=False,
    ):

        r"""
        :param device: string
            Name of tokamak or MDS server

        :param shot: int
            Shot number

        :param detection_settings: dict or string.
            If this is 'default' or {}, then default settings will be used. To change some of the settings from their
            machine-specific defaults, set to a dictionary that can contain:

            - default_filterscope_for_elms: string or list of strings giving filterscope(s) to use. Will be overridden
              by `use_filterscopes` keyword, if provided.
            - smoother: string giving name of smoothing function. Pick from:
                - gauss_smooth: Gaussian smoother
                - rc_smooth: RC lowpass filter, specifically implemented to mimic approximations used in the DIII-D PCS.
                - asym_gauss_smooth: Asymmetric Gaussian smoother with different sigma for past and future.
                - combo: Combination of rc_smooth and gauss_smooth
                - butter_smooth: Butterworth smoothing lowpass filter
                - fft_smooth: lowpass via FFT, cut out part of spectrum, inverse FFT
            - time_window: two element list of numbers giving ends of the time range to consider in ms
            - time_factor: float: factor to multiply into MDSplus times to get timebase in ms
            - jump_hold_max_dt: float Sets maximum dt between input data samples for the Jump&Hold method.
              Used to exclude slow data from old shots, which don't work.
            - allow_fallback_when_dt_large: bool. If a basic test of data compatibility with the chosen method
              fails, a new method may be chosen if this flag is set.
            - hold_elm_flag_until_low_dalpha: flag for turning on extra logic to hold the during-ELM state until
              D_alpha drops to close to pre-ELM levels.
            - hold_elm_low_dalpha_threshold: float: Threshold as a fraction between pre-ELM min & during-ELM max
            - hold_elm_min_finding_time_window: float: Interval before ELM start to search for pre-ELM minimum (ms)
            - hold_elm_timeout': float: Maximum time the ELM flag hold can persist (ms). The ELM can still be longer
              than this as determined by other rules, but the hold flag cannot extend the ELM past this total duration.
            - detection_method: int: 0 = classic edge detection style. 1 = new jump and hold strategy.
            - find_jump_time_window: float: Length of time window used to find nearby maximum in method 1 (ms)
            - find_jump_threshold: float: Threshold for normalized jump size in method 1 (unitless)
            - \****_tuning: dict where \**** is the name of a smoothing function. Within this dict can be:
                - mild_smooth: (ms) Smoothing timescale for mild smooth
                - heavy_smooth_factor: Heavy will be this much stronger than mild
                - mild_smooth_derivative_factor: The deriv is of already smoothed data, but it may need a bit more.
                - heavy_smooth_derivative_factor: The derivative is smoothed again harder so there can be a diff.
                - threshold_on_difference_of_smooths: When mild-heavy is greater than this threshold, it must be
                  during ELM (relative to max diff)
                - threshold_on_difference_of_smoothed_derivatives_plus: When mild(der)-heavy(der) is greater than
                  this threshold, it must be on one of the edges of an ELM.
                - threshold_on_difference_of_smoothed_derivatives_minus: Same as previous, but heavy(der)-mild(der)
                  instead.
                - d_thresh_enhance_factor: When the diff of derivs is positive but the less smoothed derivative is
                  still negative, we're in danger of getting a false positive, so make the threshold higher.
                - neg_d_thresh_enhance_factor: Same as before but for when mild(der)-heavy(der) is negative instead.
                - debounce: Number of samples in debouncing window
                - leading_side_width_factor: [asym_gauss_smooth ONLY]: how big is the asymmetry?
                - gauss_center_lag: [asym_gauss_smooth ONLY]: Shift center back in time, making the thing laggier.
                  Negative value shifts forward in time, putting more weight on the future.

        :param filter_settings: dict or string
            If this is 'default' or {}, then default settings will be used. To change some of the settings from their
            machine-specific defaults, set to a dictionary that can contain:

            - elm_phase_range: A two element list or array containing the minimum and maximum acceptable values of
              ELM phase. ELM phase starts at 0 when an ELM ends and goes to 1 just before the next ELM begins,
              then flips to -1 and is negative during ELMs. ELM phase increases from -1 to 0 during an ELM before
              becoming positive again in the next inter-ELM period.

            - elm_since_reject_below: Data are rejected if the time since the last ELM is below this threshold.
              Useful for packs of closely spaced ELMs; a double spike in D-alpha could register as two ELMs with a
              very short inter-ELM period between them when phase would increase from 0 to 1 and a slice could be
              accepted, even if there hadn't really been any time for ELM recovery.
              This setting is ignored if its value is <= -10 or if either end of the elm_phase_range is < 0.

            - elm_since_accept_above: Data are accepted if the time since the last ELM is above this threshold,
              regardless of ELM phase. Useful for analyzing shots that have a mixture of ELMing and non-ELMing
              phases. An ELM free period will normally be counted as one long inter-ELM period and it will take a
              long time for ELM phase to increase, which could lead to rejection of too many data. This setting
              overrides the ELM phase test to allow ELM-free periods to be included.

            - CER_entire_window_must_pass_ELM_filter: Relevant for CER where stime>0. If this is True, then the
              entire averaging window must be in the "good" part of the ELM phase. If this is False, only the
              middle has to be in the good part and also no ELMs are allowed to start during the time window in
              either case.

        :param use_filterscopes: None, False, or input satisfying detection_settings -> default_filterscope_for_elms
            Easier-to-access override for default_filterscope_for_elms in detection_settings

        :param attempt_sum_tdi_filterscopoes: bool
            Try to ask the server to sum D_alpha signals so that they don't have to be interpolated and summed client
            side, and so that there will only be one signal transferred. Works sometimes, but not yet entirely reliable.
            It also doesn't have an obvious speed benefit.

        :param debug: bool
            Turn on spammier debug print or printd statements and also save intermediate data

        :param debug_plots: bool
            Turn on debugging plots

        :param on_failure: string
            What action should be done for failures?
            'exception': raise an exception
            'pass': return all ones from filter(); passing all data through the ELM filter (same as no ELM filtering)

        :param mode: string
            'elm': ELM detection (what this class was always meant to do)
            'sawtooth': Sawtooth detection

        :param quiet: bool
            Suppress some warnings and error messages which would often be useful.
        """
        self.debug = debug
        self.debug_plots = debug_plots
        self.on_failure = on_failure
        self.quiet = quiet

        printd('  OMFITelm: setup started', topic='omfit_elm')
        # super().__init__()  # Breaks attempts to use reload_python(omfit_elm)
        SortedDict.__init__(self)
        self.status = {'setup': False, 'gathered': False, 'detected': False, 'calcs': False}
        # Handle basic settings
        self.device = tokamak(device)
        self.supported_devices = ['DIII-D', 'KSTAR', 'NSTX', 'NSTXU']
        if not is_device(self.device, self.supported_devices):
            printw(
                '  OMFITelm WARNING: Current device {} is not supported and you may encounter errors. Please '
                'try again with one of these supported devices: {}'.format(self.device, self.supported_devices)
            )
        if shot is None:
            shot = 0
        if shot <= 0:
            shot += self.lookup_latest_shot()
        self.shot = shot
        self.mode = mode

        # Handle machine specific setup details
        self.machine_data = {
            'DIII-D': {
                'mds_tree': None,
                'rvsout_ptname': 'rvsout',
                'rvsin_ptname': 'rvsin',
                'zvsout_ptname': 'zvsout',
                'ip_ptname': 'ip',
                'filterscope_data': {
                    'names': [
                        'FS00',
                        'FS01',
                        'FS07',
                        'FS08',
                        'FS02',
                        'FS03',
                        'FS04',
                        'FS05',
                        'FS06',
                        'FS13UP',
                        'FS12UP',
                        'FS11UP',
                        'FS00UP',
                        'FS01UP',
                        'FS02UP',
                        'FS03UP',
                        'FS04UP',
                        'FS12',
                    ],
                    'locs': np.array(
                        [
                            [1.015, -1.113],
                            [1.049, -1.256],
                            [1.114, -1.321],
                            [1.143, -1.352],
                            [1.225, -1.362],
                            [1.307, -1.362],
                            [1.347, -1.362],
                            [1.491, -1.252],
                            [1.602, -1.252],
                            [1.015, 0.616],
                            [1.015, 0.861],
                            [1.015, 1.144],
                            [1.152, 1.176],
                            [1.262, 1.293],
                            [1.413, 1.261],
                            [1.545, 1.151],
                            [1.696, 1.079],
                            [1.016, -0.140],
                        ]
                    ),
                },
            },
            'NSTX': {
                'mds_tree': 'NSTX',
                'rvsout_ptname': r'\NSTX::TOP.EFIT.EFIT01.RESULTS.AEQDSK.RVSOUT',
                'rvsin_ptname': r'\NSTX::TOP.EFIT.EFIT01.RESULTS.AEQDSK.RVSIN',
                'zvsout_ptname': r'\NSTX::TOP.EFIT.EFIT01.RESULTS.AEQDSK.ZVSOUT',
                'ip_ptname': r'\NSTX::TOP.ENGINEERING.ANALYSIS.IP1',
                'filterscope_data': {
                    'names': [
                        'PASSIVESPEC.FILTERED_VIS.BAYC_TOP.DALF_FSCOPE',
                        'PASSIVESPEC.FILTERED_VIS.BAYC_TOP.DALF_HAIFA',
                        'PASSIVESPEC.FILTERED_VIS.BAYD_TOP.DALPHA_HAIFA',
                        'PASSIVESPEC.FILTERED_VIS.BAYE_BOTTOM.DALF_FSCOPE',
                        'PASSIVESPEC.FILTERED_VIS.BAYE_BOTTOM.DALF_EIES',
                    ]
                },
            },
            'KSTAR': {
                'mds_tree': 'KSTAR',
                'filterscope_data': {
                    'names': [
                        r'\pol_ha02',
                    ]
                },
                'ip_ptname': r'\rc02',
                'rvsout_ptname': r'\KSTAR::TOP.EFIT.EFIT01.RESULTS.AEQDSK.RVSOUT',
                'zvsout_ptname': r'\KSTAR::TOP.EFIT.EFIT01.RESULTS.AEQDSK.ZVSOUT',
                'rvsin_ptname': r'\KSTAR::TOP.EFIT.EFIT01.RESULTS.AEQDSK.RVSIN',
            },
        }
        self.machine_data['NSTXU'] = self.machine_data['NSTX']

        # ELM detection settings
        self.default_settings_all = {
            'generic': {
                'detection': {
                    'default_filterscope_for_elms': 'auto_select',
                    'time_factor': 1.0,
                    'smoother': 'butter_smooth',
                    'gauss_smooth_tuning': {
                        'mild_smooth': 0.5,
                        'heavy_smooth_factor': 5.0,
                        'heavy_smooth_derivative_factor': 4.0,
                        'threshold_on_difference_of_smooths': 0.03,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.14,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.28,
                        'debounce': 7,
                        'mild_smooth_derivative_factor': 0.0,
                        'd_thresh_enhance_factor': 1.0,
                        'neg_d_thresh_enhance_factor': 1.0,
                    },
                    'rc_smooth_tuning': {
                        'mild_smooth': 0.65,
                        'heavy_smooth_factor': 3.5,
                        'heavy_smooth_derivative_factor': 3.0,
                        'threshold_on_difference_of_smooths': 0.028,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.09,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.18,
                        'debounce': 7,
                        'mild_smooth_derivative_factor': 0.5,
                        'd_thresh_enhance_factor': 3.5,
                        'neg_d_thresh_enhance_factor': 1.0,
                    },
                    'asym_gauss_smooth_tuning': {
                        'mild_smooth': 0.5,
                        'heavy_smooth_factor': 5.0,
                        'heavy_smooth_derivative_factor': 4.0,
                        'leading_side_width_factor': 2.0,
                        'center_lag': 0.0,
                        'threshold_on_difference_of_smooths': 0.03,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.14,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.28,
                        'debounce': 7,
                        'mild_smooth_derivative_factor': 0.0,
                        'd_thresh_enhance_factor': 1.0,
                        'neg_d_thresh_enhance_factor': 1.0,
                    },
                    'combo_tuning': {
                        'mild_smooth': 0.5,
                        'heavy_smooth_factor': 5.0,
                        'heavy_smooth_derivative_factor': 3.75,
                        'threshold_on_difference_of_smooths': 0.035,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.12,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.21,
                        'debounce': 7,
                        'mild_smooth_derivative_factor': 0.0,
                        'd_thresh_enhance_factor': 1.0,
                        'neg_d_thresh_enhance_factor': 1.0,
                    },
                    'butter_smooth_tuning': {
                        'mild_smooth': 0.5,
                        'heavy_smooth_factor': 5.0,
                        'mild_smooth_derivative_factor': 0.0,
                        'heavy_smooth_derivative_factor': 4.0,
                        'threshold_on_difference_of_smooths': 0.05,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.14,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.14,
                        'd_thresh_enhance_factor': 1.0,
                        'debounce': 7,
                        'neg_d_thresh_enhance_factor': 1.0,
                    },
                    'fft_smooth_tuning': {
                        'mild_smooth': 0.5,
                        'heavy_smooth_factor': 5.0,
                        'mild_smooth_derivative_factor': 0.0,
                        'heavy_smooth_derivative_factor': 3.5,
                        'threshold_on_difference_of_smooths': 0.028,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.08,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.18,
                        'd_thresh_enhance_factor': 3.0,
                        'debounce': 7,
                        'neg_d_thresh_enhance_factor': 1.0,
                    },
                    'smoother_info': {
                        'gauss_smooth': {'notes': 'SLOW', 'name': 'Gaussian smooth', 'preferred': False},
                        'rc_smooth': {'notes': 'good, RT relevant', 'name': 'RC lowpass smoothing filter', 'preferred': False},
                        'butter_smooth': {'notes': 'fast, RT relevant', 'name': 'Butterworth', 'preferred': True},
                        'asym_gauss_smooth': {'notes': 'SLOW', 'name': 'Asymmetric Gaussian smooth', 'preferred': False},
                        'combo': {'notes': 'SLOW', 'name': 'Combination: average RC & Gaussian', 'preferred': False},
                        'fft_smooth': {'notes': 'testing only', 'name': 'FFT smooth', 'preferred': False},
                    },
                    'time_window': [0, 15000],
                    'hold_elm_flag_until_low_dalpha': True,
                    'hold_elm_low_dalpha_threshold': 0.1,  # Fraction between pre-ELM min & during-ELM max
                    'hold_elm_min_finding_time_window': 0.5,  # ms
                    'hold_elm_timeout': 5.0,  # ms
                    'detection_method': 1,
                    'jump_hold_max_dt': 0.1,  # ms
                    'allow_fallback_when_dt_large': False,
                    'find_jump_time_window': 0.25,  # ms
                    'find_jump_threshold': 0.12,
                    'find_jump_presmo': 0.1,  # ms
                    'find_jump_debounce': 0,  # samples
                },
                'filtering': {
                    'elm_phase_range': np.array([0, 1]),
                    'elm_since_reject_below': 0.1,
                    'elm_since_accept_above': 25.0,
                    'CER_entire_window_must_pass_ELM_filter': False,
                },
                'misc': {'elm_freq_method': 3},
            },
            'DIII-D': {},
            'EAST': {
                'detection': {
                    'time_factor': 1e3,
                }
            },
            'KSTAR': {
                'detection': {
                    'time_factor': 1e3,
                    'find_jump_threshold': 0.05,
                }
            },
            'NSTX': {
                'detection': {
                    'time_factor': 1e3,
                    'jump_hold_max_dt': 0.21,  # ms  # TODO: check this setting
                    'gauss_smooth_tuning': {
                        'mild_smooth': 1.5,
                        'threshold_on_difference_of_smooths': 0.16,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.22,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.33,
                    },
                    'rc_smooth_tuning': {
                        'mild_smooth': 2.0,
                        'threshold_on_difference_of_smooths': 0.18,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.25,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.25,
                    },
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {
                        'mild_smooth': 2.0,
                        'heavy_smooth_factor': 4.0,
                        'threshold_on_difference_of_smooths': 0.2,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.3,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.4,
                    },
                },
                'filtering': {},
                'misc': {},
            },
            'NSTXU': {
                'detection': {
                    'jump_hold_max_dt': 0.21,  # ms  # TODO: check this setting
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {
                        'threshold_on_difference_of_smooths': 0.04,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.08,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.25,
                        'd_thresh_enhance_factor': 1.0,
                        'neg_d_thresh_enhance_factor': 0.5,
                    },
                },
                'filtering': {},
                'misc': {},
            },
        }
        self.default_settings_elm = {
            'generic': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {},
                },
                'filtering': {},
                'misc': {},
            },
            'DIII-D': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {},
                },
                'filtering': {},
                'misc': {},
            },
            'NSTX': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {},
                },
                'filtering': {},
                'misc': {},
            },
            'NSTXU': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {},
                },
                'filtering': {},
                'misc': {},
            },
        }
        self.default_settings_saw = {
            'generic': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {
                        'mild_smooth': 0.5,
                        'heavy_smooth_factor': 5.0,
                        'heavy_smooth_derivative_factor': 4.0,
                        'threshold_on_difference_of_smooths': 0.06,
                        'threshold_on_difference_of_smoothed_derivatives_plus': 0.12,
                        'threshold_on_difference_of_smoothed_derivatives_minus': 0.12,
                        'debounce': 3,
                        'mild_smooth_derivative_factor': 0.0,
                        'd_thresh_enhance_factor': 1.0,
                        'neg_d_thresh_enhance_factor': 1.0,
                    },
                    'hold_elm_flag_until_low_dalpha': False,
                    'hold_elm_low_dalpha_threshold': 0.1,  # Fraction between pre-ELM min & during-ELM max
                    'hold_elm_min_finding_time_window': 0.5,  # ms
                    'hold_elm_timeout': 5.0,  # ms
                    'detection_method': 0,
                    'jump_hold_max_dt': 0.5,  # ms
                    'find_jump_time_window': 0.25,  # ms
                    'find_jump_threshold': 0.12,
                    'find_jump_presmo': 0.1,  # ms
                    'find_jump_debounce': 0,  # samples
                },
                'filtering': {},
                'misc': {},
            },
            'DIII-D': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {},
                },
                'filtering': {},
                'misc': {},
            },
            'NSTX': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {},
                },
                'filtering': {},
                'misc': {},
            },
            'NSTXU': {
                'detection': {
                    'gauss_smooth_tuning': {},
                    'rc_smooth_tuning': {},
                    'asym_gauss_smooth_tuning': {},
                    'combo_tuning': {},
                    'butter_smooth_tuning': {},
                },
                'filtering': {},
                'misc': {},
            },
        }
        if self.mode == 'sawtooth':
            recursiveUpdate(self.default_settings_all, self.default_settings_saw)
        else:
            recursiveUpdate(self.default_settings_all, self.default_settings_elm)
        self.default_settings = copy.deepcopy(self.default_settings_all['generic'])
        recursiveUpdate(self.default_settings, self.default_settings_all.get(tokamak(device), {}))

        self['settings'] = copy.deepcopy(self.default_settings)
        recursiveUpdate(
            self['settings'],
            {
                'detection': detection_settings if isinstance(detection_settings, dict) else {},
                'filtering': filter_settings if isinstance(filter_settings, dict) else {},
            },
        )

        if not use_filterscopes:
            self['settings']['detection']['filterscopes'] = tolist(self['settings']['detection']['default_filterscope_for_elms'])
        else:
            self['settings']['detection']['filterscopes'] = tolist(use_filterscopes)
        self.attempt_sum_tdi_filterscopoes = attempt_sum_tdi_filterscopoes
        self.device_groups = {}
        self.device_group = self.device_groups.get(self.device, self.device)
        self.detection_settings_used = None
        self['plots'] = SortedDict()
        self.default_plot = 'elm_detection_plot'
        scratch['shot'] = self.shot
        scratch['device'] = self.device
        scratch['settings'] = self['settings']
        self.status['setup'] = True
        if not mds_available:
            printe('Unable to import MDSplus! OMFITelm will not be able to gather any data!')
        return

    def __call__(self, times_to_filter=None, **kwargs):
        """
        Runs detection as needed and optionally filters times (if provided)

        :param times: [Optional] 1D array or list of such arrays as would be accepted by self.filter()
            If times to filter are provided, __call__ will pass times_to_filter and kwargs to self.filter()
            (after making sure detection is complete)

        :param kwargs: keyword arguments to pass to .filter(), if applicable

        :return: None or output from self.filter(), which is a 1D array ro list of 1D arrays.
        """
        if not self.get('success', False):
            self.detect()

        if times_to_filter is None:
            return None
        else:
            return self.filter(times_to_filter, **kwargs)

    def __tree_repr__(self):
        """Provides the label that OMFIT should use while representing class instances in the tree."""
        if not mds_available:
            return 'Disabled: no MDSplus support', []
        if self.status['calcs']:
            state = 'ready (step 3/3)'
        elif self.status['detected']:
            state = 'detected (step 2/3)'
        elif self.status['gathered']:
            state = 'gathered (step 1/3)'
        else:
            state = 'blank (step 0/3)'
        label = '{mode:}{device:}#{shot:}, [{state:}], {smo:}, ph={phase_range:}, sa={since:}, sr={reject:}, ' 'fs={fs:}'.format(
            device=self.device,
            shot=self.shot,
            smo=self['settings']['detection']['smoother'],
            state=state,
            phase_range=self['settings']['filtering']['elm_phase_range'],
            since=self['settings']['filtering']['elm_since_accept_above'],
            reject=self['settings']['filtering']['elm_since_reject_below'],
            fs=self['settings']['detection']['filterscopes'],
            mode='SAWTOOTH! ' if self.mode == 'sawtooth' else '',
        )
        return label, []

    def lookup_latest_shot(self):
        """Looks up the last shot. Works for DIII-D. Used automatically if shot <= 0, in which case the shot number is
        treated as relative to the last shot."""
        import psycopg2

        if is_device(self.device, 'DIII-D'):
            try:
                last_shot = OMFITrdb(
                    "SELECT shot FROM summaries WHERE shot = (SELECT MAX(shot) FROM summaries)",
                    db='d3drdb',
                    server='d3drdb',
                    by_column=True,
                )['shot'][0]
            except (psycopg2.ProgrammingError, KeyError):
                raise OMFITexception('Shot 0 lookup failed. Please confirm access to d3drdb.')
        else:
            raise NotImplementedError(
                'OMFITelm: Shot 0 lookup functionality is not implemented for device={}. '
                'Please choose a real shot number.'.format(self.device)
            )
        return last_shot

    def guess_time_factor(self, mdsvalue=None, mds_time_units=None, device=None):
        """
        Tries to guess the time factor needed to convert to ms

        :param mdsvalue: OMFITmdsValue instance [optional]
            Used to obtain mds_time_units, if provided

        :param mds_time_units: string [optional]
            This string will be compared to common ways of representing various
            time units. If this is not provided and cannot be obtained, the guess
            will be based on device only.
            This setting is ignored if:
                - mdsvalue is provided
                - The device is one which is known to frequently have incorrect
                  units logged in MDSplus.

        :param device: string [optinal]
            Defaults to self.device. This shouldn't have to be supplied
            except for testing or exotic applications.

        :return: float
            Factor needed to convert from time units to ms.
            Returns None if it cannot be determined.
        """

        ways_to_write_seconds = ['s', 'sec', 'seconds']
        ways_to_write_ms = ['ms', 'milliseconds', 'milli-seconds', 'millisec', 'msec']
        devices_that_use_seconds_by_default = ['EAST', 'EAST_US', 'KSTAR', 'NSTX', 'NSTXU']
        devices_that_use_ms_by_default = ['DIII-D']
        devices_that_might_have_incorrect_units_listing = ['EAST', 'EAST_US', 'KSTAR']

        if device is None:
            device = self.device
        if mdsvalue is None:
            time_units = mds_time_units
        else:
            time_units = mdsvalue.units_dim_of(0).lower()

        if time_units in ways_to_write_seconds:
            tf = 1e3
        elif (time_units in ways_to_write_ms) and (device not in devices_that_might_have_incorrect_units_listing):
            tf = 1.0
        elif device in devices_that_use_seconds_by_default:
            tf = 1e3
        elif device in devices_that_use_ms_by_default:
            tf = 1.0
        else:
            tf = None

        if tf is None:
            printd('  Could not determine time factor', topic='omfit_elm')
        else:
            printd('  Set time_factor to 1e3 to convert sec to ms', topic='omfit_elm')

        return tf

    def select_filterscope(self):
        """
        Automatically pick which filterscope(s) or D_alpha measurement(s) to use as input to the ELM detection algorithm
        """
        # Original script created as part of OMFIT module ELM_processing
        # Created by eggertw at 2016 Jul 06  10:34
        # Overhauled by roelofsm at 2016 Dec 13  17:46
        # Edited more by eldond

        if self.mode == 'sawtooth':
            self.select_sawtooth_signal()
            return

        det_set = self['settings']['detection']
        tree = self.machine_data[self.device]['mds_tree']

        printd('  OMFITelm: Picking the best filterscope chord(s) to use for ELM detection...', topic='omfit_elm')

        if is_device(self.device, ['NSTX', 'NSTXU']):
            # NSTX has filterscopes with very wide views; only need one per divertor.
            # Might as well just add them together and always use the sum of both, right?
            acceptlist = ['PASSIVESPEC.FILTERED_VIS.BAYD_TOP.DALPHA_HAIFA', 'PASSIVESPEC.FILTERED_VIS.BAYE_BOTTOM.DALF_FSCOPE']
            acceptlist_clean = ['.'.join(a.split('.')[-2:]) for a in acceptlist]
            printd(' > Accepted filterscopes: for {:}#{:}: {:}'.format(self.device, self.shot, acceptlist_clean), topic='omfit_elm')

            det_set['filterscopes'] = acceptlist
            det_set['filterscope_chosen_automatically_for_shot'] = copy.copy(self.shot)
        elif is_device(self.device, 'KSTAR'):
            acceptlist = [r'\pol_ha02']
            acceptlist_clean = ['pol_ha02']
            det_set['filterscopes'] = acceptlist
            det_set['filterscope_chosen_automatically_for_shot'] = copy.copy(self.shot)
        elif is_device(self.device, 'DIII-D'):
            if not mds_available:
                printe('No MDSplus module available; cannot run filterscope selector.')
                return
            fsnames_available = []
            acceptlist = []

            # Filterscope (r,z) coordinates, organized so the first column is the radii, second column is the height
            fslocs = self.machine_data[self.device]['filterscope_data']['locs']

            # Filterscope names, in the same order as the (r,z) pairs above
            fsnames = tolist(self.machine_data[self.device]['filterscope_data']['names'])

            det_set.setdefault('bad_filterscope_channels', [])
            if det_set['bad_filterscope_channels'] is not None:
                for badone in det_set['bad_filterscope_channels']:
                    if badone in fsnames:
                        printd(' > Filterscope {} is listed as bad for this shot, removing...'.format(badone), topic='omfit_elm')
                        fsnames.remove(badone)

            # Check that all filterscopes are working (or turned on), and discard the ones that aren't.
            # Instead of setting a signal level floor, code now check for all finite or all zero.
            # There is the current assumption that some points are allowed to be non-finite, but it might be the case
            # that a chord should be removed if any value is nonfinite.
            if (
                'bad_filterscope_channels_listed_for_shot' not in det_set
                or det_set['bad_filterscope_channels_listed_for_shot'] != self.shot
            ):
                # Reset the bad fs channels if they weren't listed for this shot
                det_set['bad_filterscope_channels_listed_for_shot'] = self.shot
                det_set['bad_filterscope_channels'] = []
            validloc = np.array([])
            for i, name in enumerate(fsnames):
                try:
                    tmpval = OMFITmdsValue(server=self.device, treename=tree, shot=self.shot, TDI=name)
                except MDSplus.MdsException:
                    printd('Filterscope {} ran into an mdsException, removing...'.format(name), topic='omfit_elm')
                    bad = True
                else:
                    if tmpval.dim_of(0) is None or tolist(tmpval.dim_of(0)) == [0]:
                        printd('Filterscope {} is missing x values, removing...'.format(name), topic='omfit_elm')
                        bad = True
                    elif tmpval.data() is None or tolist(tmpval.data()) == [0]:
                        printd(' > Filterscope {} is missing y values, removing...'.format(name), topic='omfit_elm')
                        bad = True
                    elif all((~np.isfinite(tmpval.data())) | (tmpval.data() == 0)):  # If all data is non-finite or 0
                        printd(' > Filterscope {}is either off or not working, removing...'.format(name), topic='omfit_elm')
                        # Add it to the bad list
                        bad = True
                    else:
                        bad = False
                if bad:
                    det_set['bad_filterscope_channels'] = tolist(det_set['bad_filterscope_channels']) + [name]
                else:
                    validloc = np.append(validloc, [i])

            validloc = validloc.astype(int)
            # Filter to the good ones.
            good_fslocs = fslocs[validloc, :]
            good_fsnames = np.array(fsnames)[validloc]

            # Gather the data we need (distances in meters)
            rvsout = OMFITmdsValue(  # Major radius of outer strike point of primary separatrix
                server=self.device, treename=tree, shot=self.shot, TDI=self.machine_data[self.device]['rvsout_ptname']
            )
            rvsin = OMFITmdsValue(  # Major radius of inner strike point of primary separatrix
                server=self.device, treename=tree, shot=self.shot, TDI=self.machine_data[self.device]['rvsin_ptname']
            )
            zvsout = OMFITmdsValue(  # Height of outer strike point of primary separatrix
                server=self.device, treename=tree, shot=self.shot, TDI=self.machine_data[self.device]['zvsout_ptname']
            )
            ip = OMFITmdsValue(  # Plasma current in MA
                server=self.device, treename=tree, shot=self.shot, TDI=self.machine_data[self.device]['ip_ptname']
            )
            if rvsout.dim_of(0) is not None:
                t = rvsout.dim_of(0)
                printd(' > Used rvsout.dim_of(0) as time coordinate', topic='omfit_elm')
            elif rvsin.dim_of(0) is not None:
                t = rvsin.dim_of(0)
                printd(' > Used rvsin.dim_of(0) as time coordinate', topic='omfit_elm')
            elif zvsout.dim_of(0) is not None:
                t = zvsout.dim_of(0)
                printd(' > Used zvsout.dim_of(0) as time coordinate', topic='omfit_elm')
            else:
                t = None
                printe('FAILURE: The time coordinate of all the strike points was None!')

            # Extract the values
            rvs_valsout = rvsout.data()
            rvs_valsin = rvsin.data()
            zvs_vals = zvsout.data()
            ip_vals = interp1d(ip.dim_of(0), ip.data(), bounds_error=False, fill_value='extrapolate')(t)

            # Produces a filter accepting times when plasma current is >= 80% of the 95% percentile (outlier rejection)
            # and where R > 0 (when EFIT failed to find an X-point), if there are any points with R > 0
            w = abs(ip_vals) >= 0.8 * np.nanpercentile(ip_vals, 0.95)
            if np.any(rvs_valsin > 0):
                w &= rvs_valsin > 0
            else:
                printw(
                    f'WARNING: no data for strike point coordinates. EFIT may have failed for {self.shot}. '
                    f'Filterscope selection will be suboptimal because of this.'
                )

            # Average strike point for the shot
            if sum(w):
                r_avgout = np.nanmean(rvs_valsout[w])
                r_avgin = np.nanmean(rvs_valsin[w])
                z_avg = np.nanmean(zvs_vals[w])
            else:
                r_avgout = r_avgin = z_avg = np.NaN

            if abs(z_avg) < 0.8:  # Check to see if this is a double null where the x point could change sides often
                printd(' > Filterscope picker: this may be a double null. DN contingency activated.', topic='omfit_elm')
                if z_avg >= 0:  # Mostly upper biased
                    printd(
                        '  >> Looks like mostly upper biased: look for a FS near the upper outer strike point '
                        '(filter time for zvsout >= 0)',
                        topic='omfit_elm',
                    )
                    u2 = zvs_vals >= 0
                else:  # Mostly lower biased
                    printd(
                        '  >> Looks like mostly lower biased: look for a FS near the lower outer strike point '
                        '(filter time for zvsout < 0)',
                        topic='omfit_elm',
                    )
                    u2 = zvs_vals < 0
                if self.debug:
                    printd('u2 = {:}'.format(u2), topic='omfit_elm')
                printd('  >> np.shape(u2) = {:}'.format(np.shape(np.atleast_1d(u2))), topic='omfit_elm')

                printd(' > Re-filtering signals with special filter for DN cases and recomputing averages...', topic='omfit_elm')
                w *= u2  # Filter to be only upper or only lower
                r_avgout = np.mean(rvs_valsout[w])
                r_avgin = np.mean(rvs_valsin[w])
                z_avg = np.mean(zvs_vals[w])

            # Determine upper and lower chords.
            if z_avg > 0:  # Filter upper vs lower null
                i_good = good_fslocs[:, 1] > 0.5  # Also filter out middle views.
            else:
                i_good = good_fslocs[:, 1] < -0.5

            # Apply up/down filter.
            good_fslocs = good_fslocs[i_good, :]
            good_fsnames = good_fsnames[i_good]
            validloc = validloc[i_good]

            # This block ensures the chord is not looking at the private flux region.
            if r_avgin <= 1.015:
                r_avgin = 1.016  # If the inner strike point is on (or inside) the center post, pretend
            # it is 1mm out from it.
            for i in range(len(good_fsnames)):
                if (r_avgout < good_fslocs[i, 0]) or (r_avgin > good_fslocs[i, 0]):
                    acceptlist.append(good_fsnames[i])

            if self.debug:  # Avoid spam by requiring self.debug and flag for printd to be set.
                printd('    r_avgout = {}'.format(r_avgout), topic='omfit_elm')
                printd('    r_avgin = {}'.format(r_avgin), topic='omfit_elm')
                printd('    z_avg = {}'.format(z_avg), topic='omfit_elm')
                printd('    good_fslocs = {}'.format(good_fslocs), topic='omfit_elm')
                printd('    np.shape(fslocs) = {}'.format(np.shape(fslocs)), topic='omfit_elm')

            printd(' > Accepted filterscopes for {}#{}: {:}'.format(self.device, self.shot, acceptlist), topic='omfit_elm')

            # Chord selection can be improved in the future with a goodness hierachy instead of a strict filtering.
            # But currently we have not encountered robutness problems without fallback schemes.
            if len(acceptlist) <= 0:
                raise OMFITexception("Filterscope failed! No good chord found!")

            det_set['filterscopes'] = acceptlist
            det_set['filterscope_chosen_automatically_for_shot'] = copy.copy(self.shot)
        else:  # Unrecognized device
            raise OMFITelmNotSupported(
                f'Automatic filterscope selection is not supported for {device}. Please specify filterscopes manually.'
            )
        return

    def get_omega_ce(self):
        """
        Gathers equilibrium data and calculates local electron cyclotron emission frequency for use in mapping.

        This is relevant for sawtooth mode only.

        :return: time (ms), rho (unitless), psi_N (unitless), omega_ce (radians/sec)
            time is 1D with length nt
            All others are 2D vs time and space with shape (nt, nx)
        """
        eq = read_basic_eq_from_mds(
            device=self.device,
            shot=self.shot,
            g_file_quantities=['r', 'z', 'rhovn', 'fpol', 'psirz'],
            a_file_quantities=[],
            derived_quantities=['psin1d', 'time', 'psin'],
        )
        imid = abs(eq['z']).argmin()
        pm = eq['psin'][:, imid, :]
        fpol = [np.array([None])] * len(eq['time'])
        rho = [np.array([None])] * len(eq['time'])
        for i in range(len(eq['time'])):
            fpol[i] = interp1d(eq['psin1d'], eq['fpol'][i, :], bounds_error=False, fill_value='extrapolate')(pm[i, :])
            rho[i] = interp1d(eq['psin1d'], eq['rhovn'][i, :], bounds_error=False, fill_value=1.05)(pm[i, :])
        fpol = np.array(fpol)
        rho = np.array(rho)

        bt = fpol / eq['r']
        dpdt, dpdr, dpdz = np.gradient(eq['psirz'], eq['time'], eq['r'][1] - eq['r'][0], eq['z'][1] - eq['z'][0])
        br = dpdz[:, imid, :] / eq['r']
        bz = -dpdr[:, imid, :] / eq['r']
        btot = np.sqrt(br ** 2 + bz ** 2 + bt ** 2)
        if self.debug:
            self['ece_data']['bt'] = bt
            self['ece_data']['br'] = br
            self['ece_data']['bz'] = bz
            self['ece_data']['btot'] = btot
            self['ece_data']['r_midplane'] = eq['r']
            self['ece_data']['psin_midplane'] = pm

        tbt = eq['time']
        wce = constants.e * btot / constants.m_e  # radians/s, no relativistic correction
        return tbt, rho, pm, wce  # time (ms), space (unitless), space (unitless), angular frequency (rad/s)

    def select_sawtooth_signal(self, rho_close_to_axis=0.1, rho_far_from_axis=0.4):
        """
        Automatically chooses signals to use for sawtooth detection.

        First: try to get within rho < rho_close_to_axis.
        Second: avoid cut-off.
        If there are no good channels (no cut-off) within rho <= rho_close_to_axis,
        get the closest channel in that's not cut-off, but don't look at rho >= rho_far_from_axis for it.
        For cut-off, use average density to estimate local density, based on the assumption that anything farther
        out than the top of the pedestal can be ignored anyway, and that density has a small gradient in the core. This
        might be okay.

        There is no relativistic correction for frequency, which could lead to a small error in position which is
        deemed to be irrelevant for this application.

        :param rho_close_to_axis: float between 0 and 1
            The first try is to find non-cut-off channels with rho <= rho_close_to_axis

        :param rho_far_from_axis: float between 0 and 1
            If no channels with rho <= rho_close_to_axis, find the closest non-cut-off channel, but only use it if
            its rho < rho_far_from_axis

        :return: list of strings
            Pointnames for good ECE channels to use in sawtooth detection
        """
        det_set = self['settings']['detection']  # Shortcut

        def get_ece():
            """Gathers ECE data"""
            auto_sawtooth_signal_supported_devices = ['DIII-D']
            if not is_device(self.device, auto_sawtooth_signal_supported_devices):
                raise OMFITelmNotSupported(
                    f"Automatic ECE / sawtooth signal selection is not supported for device {self.device}. "
                    f"Supported devices are {auto_sawtooth_signal_supported_devices}"
                )
            tf = self['settings']['detection'].get('time_factor', 1)
            self['ece_data'] = SortedDict()
            valid = OMFITmdsValue(server=self.device, shot=self.shot, treename='ELECTRONS', TDI=r'\ELECTRONS::TOP.ECE.CAL.VALID').data()
            tedat = OMFITmdsValue(server=self.device, shot=self.shot, treename='ELECTRONS', TDI=r'\ELECTRONS::TOP.ECE.PROFS.ECEPROF')  # eV
            freq = OMFITmdsValue(server=self.device, shot=self.shot, treename='ELECTRONS', TDI=r'\ELECTRONS::TOP.ECE.SETUP.FREQ')  # GHz
            nc = len(valid)
            tte = tedat.dim_of(0) * tf  # Time in ms
            cte = tedat.dim_of(1)  # Channel numbers, counting from 1
            if self.debug:
                self['ece_data']['tedat'] = tedat
                self['ece_data']['valid'] = valid
            ite = cte - 1  # Indices
            te = tedat.data()
            nt = np.shape(te)[1]
            new_te = np.zeros((nc, nt))
            for j, i in enumerate(ite):
                new_te[i] = te[j]
            new_te[~valid.astype(bool), :] = 0

            self['ece_data']['time'] = tte  # ms
            self['ece_data']['te'] = new_te  # eV
            self['ece_data']['freq'] = freq.data()[:nc]  # GHz
            return

        def get_ece_rho(harmonic=2):
            """Gets rho values for ECE channels"""
            twce, rhowce, psiwce, wce = self.get_omega_ce()
            fce = interp1d(twce, wce, bounds_error=False, fill_value=0, axis=0)(self['ece_data']['time']) / (2 * np.pi)
            fce /= 1e9  # Hz to GHz
            fce *= harmonic
            rhowce_ = interp1d(twce, rhowce, bounds_error=False, fill_value=1.05, axis=0)(self['ece_data']['time'])
            if self.debug:
                self['ece_data']['fce'] = fce
                self['ece_data']['rhowce'] = rhowce
                self['ece_data']['rhowce_'] = rhowce_
            rho = np.array(
                [
                    interp1d(fce[i, :], rhowce_[i, :], bounds_error=False, fill_value=1.05)(self['ece_data']['freq'])
                    for i in range(len(self['ece_data']['time']))
                ]
            )
            self['ece_data']['rho'] = rho

        def get_cutoff():
            """Get information used for determining cut-off of ECE channels"""
            density_ = OMFITmdsValue(server=self.device, shot=self.shot, TDI='density')
            self['ece_data']['avg_density'] = interp1d(density_.dim_of(0), density_.data() / 1e13, bounds_error=False, fill_value=0)(
                self['ece_data']['time']
            )
            cc = constants.e ** 2 / (constants.m_e * constants.epsilon_0)  # Cool Constants
            wce = self['ece_data']['freq'] * 2 * np.pi * 1e9  # radians/sec
            self['ece_data']['cutoff_density'] = wce ** 2 / cc / 1e19  # 1e19/m^3
            self['ece_data']['cutoff_density'] /= 2.0  # Based on ECE_mapping in OMFITprofiles; maybe b/c 2nd harmonic?

        get_ece()
        get_ece_rho()
        get_cutoff()

        # Only consider which channels to use during the Ip flattop.
        ip_ = OMFITmdsValue(
            self.device,
            treename=self.machine_data[self.device]['mds_tree'],
            shot=self.shot,
            TDI=self.machine_data[self.device]['ip_ptname'],
        )
        ip = self['ece_data']['ip'] = interp1d(ip_.dim_of(0), ip_.data(), bounds_error=False, fill_value=0)(self['ece_data']['time'])
        ip_thresh = np.percentile(abs(ip), 80) * 0.95
        ip_okay = abs(ip) > ip_thresh

        # Flag channels which are in danger of cutoff
        typical_density = np.percentile(self['ece_data']['avg_density'][ip_okay], 99)
        cut_flag = typical_density > self['ece_data']['cutoff_density']
        if self.debug:
            self['ece_data']['typical_density'] = typical_density
            self['ece_data']['cutoff_flag'] = cut_flag

        # Flag channels near the axis
        rho_max = self['ece_data']['rho_max'] = np.percentile(self['ece_data']['rho'][ip_okay, :], 95, axis=0)
        # Use 95th percentile instead of max to exclude some outliers
        close = rho_max <= rho_close_to_axis
        if not np.any(close & ~cut_flag):
            rho_max2 = copy.copy(rho_max)
            rho_max2[cut_flag] = 100  # Set cut-off channels to be really far out (basically ignore them)
            if np.min(rho_max2) < rho_far_from_axis:
                # Backup plan if no chans are really close to the axis: just use the closest one unless it's really far
                # Ignore cutoff channels while selecting closest one
                close[rho_max2.argmin()] = True
        if self.debug:
            self['ece_data']['close_flag'] = close

        # Finalize channel selection
        channels = np.arange(len(close))[close] + 1
        ece_signals = ['tece{:02d}'.format(ch) for ch in channels]
        det_set['filterscopes'] = ece_signals
        det_set['filterscope_chosen_automatically_for_shot'] = copy.copy(self.shot)
        return ece_signals

    def set_filterscope(self, fs):
        """
        Change which filterscope(s) are used and delete any data which would become inconsistent with the new choice.

        :param fs: string or list of strings giving pointnames for filterscopes
            Should follow the rules for use_filterscopes keyword in __init__
        """

        det_set = self['settings']['detection']
        new_filterscopes = tolist(fs)
        if ('filterscopes' in det_set) and (tolist(det_set['filterscopes']) == new_filterscopes):
            printd('Filterscope setting was already {}. No action needed.'.format(det_set['filterscopes']), topic='omfit_elm')
        elif ('auto_select' in new_filterscopes or 'auto' in new_filterscopes or fs == 'auto') and (
            (
                'auto_select' in det_set['default_filterscope_for_elms']
                or 'auto' in det_set['default_filterscope_for_elms']
                or det_set['default_filterscope_for_elms'] == 'auto'
            )
            and ('filterscopes' in det_set)
        ):
            printd(
                'New filterscope setting instructs auto selection, but current settings are already auto select. ' 'No action needed.',
                topic='omfit_elm',
            )
        else:
            printd('New filterscope selection does not match existing settings. Purging all affected data.', topic='omfit_elm')

            del_from_self = []
            del_from_set = []

            # Erase effects of automatic filterscope selection, if any
            del_from_set += ['bad_filterscope_channels', 'filterscope_chosen_automatically_for_shot']

            # Erase effects of get_dalpha, if any
            del_from_self += ['dalpha_shot', 'dalpha_filters', 'dalpha_time', 'dalpha_y', 'get_dalpha_debugging']

            # Erase effects of detection, if any
            del_from_self += [
                'elm_phase',
                'elm_flag',
                'inter_elm_period',
                'total_elm_period',
                'since_last_elm',
                'since_last_elm_neg',
                'until_next_elm',
                'elm_time',
                'success',
                'elm_detection_details',
            ]
            # Erase effects of ELM frequency calculation, if any
            del_from_self += ['elm_freq_time', 'elm_freq', 'elm_freq_method']

            # Clear out-of-date data
            for remove_it in del_from_self:
                if remove_it in self:
                    del self[remove_it]
            for remove_it in del_from_set:
                if remove_it in det_set:
                    del det_set[remove_it]

            # Update settings
            det_set['filterscopes'] = new_filterscopes
            det_set['default_filterscope_for_elms'] = new_filterscopes
            if 'auto_select' in det_set['filterscopes'] or 'auto' in det_set['filterscopes'] or fs == 'auto':
                self.select_filterscope()
            printd('Filterscope settings updated.', topic='omfit_elm')
        return

    def set_detection_params(self, detection_settings):
        """
        Updates ELM detection settings and clears out-of-date data, if any

        :param detection_settings: dictionary consistent with the detection_settings keyword in __init__
        """
        if detection_settings != self['settings']['detection']:
            printd('New detection settings do not match existing settings. Purging affected data.', topic='omfit_elm')
            del_from_self = []

            # Erase effects of detection, if any
            del_from_self += [
                'elm_phase',
                'elm_flag',
                'inter_elm_period',
                'total_elm_period',
                'since_last_elm',
                'since_last_elm_neg',
                'until_next_elm',
                'elm_time',
                'success',
                'elm_detection_details',
            ]
            # Erase effects of ELM frequency calculation, if any
            del_from_self += ['elm_freq_time', 'elm_freq', 'elm_freq_method']

            # Clear out-of-date data
            for remove_it in del_from_self:
                if remove_it in self:
                    del self[remove_it]
            self['settings']['detection'] = copy.deepcopy(detection_settings)
            self.set_filterscope(self['settings']['detection']['default_filterscope_for_elms'])
            printd('ELM detection settings updated.', topic='omfit_elm')
        else:
            printd('New detection settings match existing settings. No action needed.', topic='omfit_elm')
        return

    def set_filter_params(self, filter_settings):
        """
        Updates ELM filter settings so that subsequent calls to .filter() may give different results.

        :param filter_settings: dictionary consistent with the filter_settings keyword in __init___
        """
        self['settings']['filtering'] = filter_settings
        return

    def get_dalpha(self):
        """
        Gathers D_alpha for use in ELM_detection
        """

        if not mds_available:
            printe('No MDSplus module available; cannot get D_alpha.')
            return

        t0 = time.time()

        if self.debug:
            self['get_dalpha_debugging'] = {}

        det_set = self['settings']['detection']

        fss = self['settings']['detection']['filterscopes']
        if fss is None or tolist(fss)[0] is None or tolist(fss)[0] == 'None':
            printd('  OMFITelm: invalid filterscope specification; resetting to auto_select')
            fss = self['settings']['detection']['filterscopes'] = ['auto_select']

        if 'auto_select' in fss or 'auto' in fss or fss == 'auto':
            printd(
                '  OMFITelm: Calling auto filterscope selector because settings/detection/filterscopes = {}'.format(
                    self['settings']['detection']['filterscopes']
                )
            )
            self.select_filterscope()
        else:
            printd(
                '  OMFITelm: SKIPPED auto filterscope selector because settings/detection/filterscopes = {}'.format(
                    self['settings']['detection']['filterscopes']
                )
            )

        printd(
            '  OMFITelm: Gathering D_alpha measurements for shot {}, filterscope(s) {}'.format(
                self.shot, self['settings']['detection']['filterscopes']
            ),
            topic='omfit_elm',
        )

        fs = det_set['filterscopes']
        treename = self.machine_data[self.device]['mds_tree']
        tf = self['settings']['detection'].get('time_factor', None)

        ip_ = OMFITmdsValue(self.device, shot=self.shot, treename=treename, TDI=self.machine_data[self.device]['ip_ptname'])
        if tf is None:
            iptf = self.guess_time_factor(mdsvalue=ip_)
            if iptf is None:
                printw('Warning! Failed to guess time unit factor for Ip. Using 1.0.')
                iptf = 1.0
        else:
             iptf = tf

        def get_mask(x_):
            if is_device(self.device, 'DIII-D'):
                mask_ = np.ones(len(x_), bool)  # No masking needed for DIII-D
            elif is_device(self.device, ['NSTX', 'NSTXU']):
                ip = interp1d(ip_.dim_of(0) * iptf, ip_.data(), fill_value=0, bounds_error=False)(x_)
                mask_ = abs(ip) > abs(ip).max() * 0.1
                # Smooth the mask then round the result up to extend it outward past the ends of the shot & debounce it.
                smo = 500.0
                dt = np.mean(np.diff(x_))
                ns = np.ceil(smo / dt).astype(int)
                mask_ = np.ceil(smooth(mask_.astype(float), window_len=ns)).astype(bool)
                if self.debug:
                    self['get_dalpha_debugging']['mask_x_'] = x_
                    self['get_dalpha_debugging']['get_dalpha_ip_'] = ip_
                    self['get_dalpha_debugging']['ip_ptname'] = self.machine_data[self.device]['ip_ptname']
                    self['get_dalpha_debugging']['ns'] = ns
                    self['get_dalpha_debugging']['dt'] = dt
                    self['get_dalpha_debugging']['smo'] = smo
                    self['get_dalpha_debugging']['mask0'] = copy.copy(mask_)
                    self['get_dalpha_debugging']['ip_interpolated'] = ip
            else:
                mask_ = np.ones(len(x_), bool)  # Not enough information to do anything better
            return mask_

        def get_dalpha_x_y(dfs):
            dalpha = 0
            dfs = tolist(dfs)  # Make sure this is a list (even if it has one element)
            datafail = True
            x0 = None
            xd = None

            if self.attempt_sum_tdi_filterscopoes:
                fs_tree = 'SPECTROSCOPY' if treename is None else treename
                start = r'\{}::'.format(fs_tree)
                mid = '+' + start
                sum_tdi = start + mid.join(dfs)
                printd('  sum_tdi = {}'.format(sum_tdi), topic='omfit_elm')
                scratch['fs_sum'] = OMFITmdsValue(server=self.device, treename=fs_tree, shot=self.shot, TDI=sum_tdi)
                if scratch['fs_sum'] is not None and scratch['fs_sum'].data() is not None and len(scratch['fs_sum'].data()) > 1:
                    xd = scratch['fs_sum'].dim_of(0)
                    dalpha = scratch['fs_sum'].data()
                    printd(
                        'Server side sum of filterscopes in TDI call appears to have succeeded! (shot {})'.format(self.shot),
                        topic='omfit_elm',
                    )
                    datafail = False
                    sum_failed_skipped = False
                else:
                    printw(
                        'Server side sum of filterscopes failed. Perhaps one of them is bad? (shot {})'.format(self.shot), topic='omfit_elm'
                    )
                    printd('Gathering individual filterscope signals and summing client side...', topic='omfit_elm')
                    sum_failed_skipped = True
            else:
                sum_failed_skipped = True

            if sum_failed_skipped:
                for fscope in dfs:
                    # Gather filterscope data
                    scratch[fscope] = OMFITmdsValue(server=self.device, treename=treename, shot=self.shot, TDI=fscope)
                    if scratch[fscope] is not None and fscope is not None:
                        if (not np.array_equal(scratch[fscope].data(), np.array([0]))) and scratch[fscope].check():
                            datafail = False
                            yd = scratch[fscope].data()  # Named it yd to avoid confusion with y that occurs later
                            xd = scratch[fscope].dim_of(0)  # times in ms to go with dalpha
                            if tf is None:
                                fstf = self.guess_time_factor(mdsvalue=scratch[fscope])
                                if fstf is None:
                                    printw(f'Warning! Could not guess time unit factor for Filterscope {fscope}! Using 1.0.')
                                    fstf = 1.0
                            else:
                                fstf = tf
                            xd *= fstf
                            valid = (
                                (xd >= self['settings']['detection']['time_window'][0])
                                & (xd <= self['settings']['detection']['time_window'][1])
                                & (np.isfinite(xd))
                                & (np.isfinite(yd))
                            )
                            yd = yd[valid]
                            xd = xd[valid]
                            if not np.array_equal(xd, x0) and x0 is not None:
                                # Interpolate in case the filterscopes are set to sample at different rates
                                yd = interp1d(xd, yd, bounds_error=False, fill_value=0)(x0)
                                # Fill with zeros outside of interp range: this would be relevant if one filterscope
                                # sampled at a faster rate for part of the shot and then ran out of samples and
                                # measured nothing. Within the time range where the fast sampling one is active, it
                                # can contribute to total signal. Outside of this range, it will just not do
                                # anything. Hopefully the time when it turns off doesn't trip the ELM detector, but
                                # one false positive probably isn't that bad. It's rare that sampling rates for
                                # filterscopes are changed.
                            else:
                                # This is guaranteed to go off on the first pass because x0 is initialized as None.
                                # After that, every new x is compared to the first one and interpolated if it
                                # doesn't match.
                                x0 = xd
                            # yd is now guaranteed to be on the same timebase as the yd from the last pass through
                            #  the loop. Maybe this was trivial or maybe we had to interpolate.

                            mask_ = get_mask(xd)
                            yd *= mask_
                            if abs(yd.min()) > abs(yd.max()) * 5:
                                # The signal appears to be negative (this does not mean inverted ELMs in detachment!)
                                yd *= -1

                            dalpha += yd  # dalpha is total light from all of the filterscopes selected by filterpicker
                        printd(' added {:} to the total dalpha signal'.format(fscope), topic='omfit_elm')

            if self.debug:
                self['get_dalpha_debugging']['dalpha'] = dalpha

            if datafail:
                if not self.quiet:
                    printe('Failed to retrieve D_alpha for {}#{} after trying {}.'.format(self.device, self.shot, dfs))
                    print('FS** signals can take time to process. ' 'If running on a very recent shot, try pcphd02 or pcphd03.')
                    print("Filterscope source can be set in root['SETTINGS']['PHYSICS']['filterScopeForELMs']")
                    print("or the fs keyword in this script.")
                    print('Must abort due to bad D_alpha.')
                settings_backup = self['settings']
                plots_backup = self['plots']
                self.clear()
                self['settings'] = settings_backup
                self['plots'] = plots_backup
                self['success'] = False
                return None, None

            data_factor = 1.0 / max(abs(dalpha))
            # The data factor rescales D_alpha to avoid floating overflow stuff with large numbers. The factor should be
            # chosen to make the result be close to 1. (anywhere between 10^-3 and 10^+3 should be fine)
            dalpha *= data_factor

            # Sawtooth modification: take -d()/dt of signal
            if self.mode == 'sawtooth':
                printd('SAWTOOTH MODE! Changing signal to -d(signal)/dt', topic='omfit_elm')
                self['raw_sawtooth_input'] = copy.copy(dalpha)
                dalpha = -deriv(xd, dalpha)

            return xd, dalpha

        try:
            filters_match = np.all(np.atleast_1d(self['dalpha_filters'] == fs))
        except (ValueError, KeyError):
            filters_match = False

        if (
            'dalpha_shot' in self
            and self['dalpha_shot'] == self.shot
            and 'dalpha_filters' in self
            and filters_match
            and 'dalpha_time' in self
            and 'dalpha_y' in self
        ):
            # We've already gathered and summed data for this setup. Reuse the result from the tree.
            printd('  OMFITelm: Existing result for D_alpha are valid; no need to gather D_alpha again.', topic='omfit_elm')
            # If you need the results, please do:
            # x = self['dalpha_time']
            # y = self['dalpha_y']
        else:
            # We don't have an appropriate past result to use
            printd('Need to gather dalpha x y...')
            if 'dalpha_shot' in self:
                tmp1 = self['dalpha_shot'] == self.shot
            else:
                tmp1 = 'N/A'
            if 'dalpha_filters' in self:
                tmp2 = filters_match
            else:
                tmp2 = 'N/A'
            printd(
                '  OMFITelm: results of tests done that led to need to gather dalpha: '
                '(must be all True to skip this part)'
                + repr(['dalpha_shot' in self, tmp1, 'dalpha_filters' in self, tmp2, 'dalpha_time' in self, 'dalpha_y' in self]),
                topic='omfit_elm',
            )

            x, y = get_dalpha_x_y(fs)
            self['dalpha_time'] = x
            self['dalpha_y'] = y
            self['dalpha_filters'] = copy.copy(fs)
            printd(
                "  OMFITelm: D_alpha data gathered for shot {} and stored in "
                "self['dalpha_time'] and self['dalpha_y'].".format(self.shot),
                topic='omfit_elm',
            )

        t1 = time.time()
        printd(
            '  OMFITelm: get_dalpha script completed in {} s with self.attempt_sum_tdi_filterscopoes = {}'.format(
                t1 - t0, self.attempt_sum_tdi_filterscopoes
            ),
            topic='omfit_elm',
        )
        self.status['gathered'] = True
        return

    def check_detection_inputs(self, method=None, count=0):
        """
        Makes sure the selected detection method is compatible with input data.

        Raises OMFITelmIncompatibleData or changes method if a problem is found,
        depending on whether fallback is allowed.

        This only catches very basic problems that can be found early in the process!
        It doesn't abort after starting detection.

        :param method: int
            Detection method index

        :param count: int
            Used to prevent infinite loops when the method updates more than once.

        :return: int
            If fallback is allowed, an invalid method may be updated to a new method and returned.
        """
        if count > 5:
            raise OMFITelmIncompatibleData(
                'OMFITelm was allowed to fall back to different detection methods too many times. '
                'It is probably passing the problem around between different methods, none of which work.'
            )
        new_method = method
        if method == 1:
            # Jump and hold
            if 'dalpha_time' not in self:
                self.get_dalpha()
            if len(np.atleast_1d(self['dalpha_time'])) > 1:
                dt = np.nanmedian(np.diff(self['dalpha_time']))
            else:
                dt = 0
            maxdt = self['settings']['detection']['jump_hold_max_dt']
            if dt > maxdt:
                if self['settings']['detection']['allow_fallback_when_dt_large']:
                    self['settings']['detection']['detection_method'] = new_method = 1
                    printw(
                        f"Raw data sample interval is too long ({dt:0.3f} > {maxdt:0.3f} ms) for the Jump&Hold "
                        f"detection method (method=1). Falling back to classic edge detection (method=0)."
                    )
                else:
                    raise OMFITelmIncompatibleData(
                        f"Raw data sample interval is too long ({dt:0.3f} > {maxdt:0.3f} ms) for the Jump&Hold "
                        f"detection method (method=1). lease switch to classic edge detection (method=0) and try "
                        f"again. Jump and hold needs faster input data sampling. For ELMs: Filterscope sample "
                        f"rates have increased over the years and shots after around 2012 (I'm guessing!) or so "
                        f"are probably okay."
                    )

        if new_method != method:
            new_method = self.check_detection(new_method, count=count + 1)
        return new_method

    def detect(self, **kw):
        """
        Chooses which ELM detection method to use and calls the appropriate function

        :param kw: keywords to pass to actual worker function
        """
        method = self['settings']['detection'].get('detection_method', 0)

        # Check for basic data problems
        method = self.check_detection_inputs(method)

        if method == 0:
            self.classic_edge_detect(**kw)
        elif method == 1:
            self.jump_and_hold_detect(**kw)
        else:
            raise ValueError('Unrecognized ELM detection method: {}\nValid options are: [0, 1]'.format(method))
        return

    def jump_and_hold_detect(self, calc_elm_freq=True):
        """
        New detection algorithm. Focuses on finding just the start of each ELM (when D_alpha jumps up) at first,
        then forcing the ELM state to be held until D_alpha drops back down again.

        :param calc_elm_freq: bool
        """

        t0 = time.time()

        # Phase one: setup ---------------------------------------------------------------------------------------------
        printd('Running jump & hold method of ELM detection for shot {:}...'.format(self.shot), topic='omfit_elm')
        if self.debug:
            self['detect_debugging'] = {}

        if tokamak(self.device) not in self.supported_devices:
            warnings.warn(
                'WARNING: Current server/device {} not found in list of supported devices. '
                'ELM detection is likely to fail! \nSuggestion: pick a device from the following list:{}'.format(
                    self.device, '\n    '.join([''] + self.supported_devices)
                )
            )

        # Tuning for finding the start
        t_win = self['settings']['detection']['find_jump_time_window']
        threshold = self['settings']['detection']['find_jump_threshold']
        presmo = float(self['settings']['detection']['find_jump_presmo'])
        debounce_setting = self['settings']['detection']['find_jump_debounce']
        rollback_fraction = 0.85  # Allow fewer rollback steps

        method = 2  # Sub-method within jump and hold. Method 2 seems to be better.
        lag_butter = False  # This has no effect because when presmo = 0 and method = 2.
        less_rollback = True

        # Get D_alpha
        self.get_dalpha()

        t = self['dalpha_time']
        y = self['dalpha_y']
        if t is None or y is None:
            if not self.quiet:
                print('Aborting ELM detection due to failure of D_alpha gathering')
            return  # Aborted during D_alpha gathering

        t1 = time.time()

        # Phase two: ELM start detection -------------------------------------------------------------------------------
        # Now get a flag for the initial phase of each ELM. We'll catch the tail later.
        ys = butter_smooth(t, y, timescale=presmo, laggy=lag_butter) if presmo > 0 else y  # Smooth for noise reduction
        dt = np.median(np.diff(t))
        n_win = int(np.ceil(t_win / dt))

        # Get the difference between each sample and the maximum in a small neighborhood
        y1 = np.concatenate((np.repeat(np.NaN, n_win), ys, np.repeat(np.NaN, n_win)))
        y2 = np.vstack(np.array([np.roll(y1, -i) for i in range(n_win)]))
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="All-NaN slice encountered")
            localmax = np.nanmax(y2, axis=0)[n_win:-n_win]
        dy0 = localmax - ys

        # This thing is always going to lead the ELM because of the roll we used. Roll it back to align properly
        nrb = int(np.round(t_win * (1 - threshold) * rollback_fraction / dt)) if less_rollback else n_win
        dy = np.roll(np.concatenate((np.repeat(0, nrb), dy0, np.repeat(0, nrb))), nrb)[nrb:-nrb]

        self['elm_detection_details'] = dict(localmax=localmax, dy=dy, n_win=n_win, nrb=nrb, ys=ys)

        if method == 1:
            # Settings for method 1 haven't been linked to proper settings dictionary because method 1 is not used
            # unless you hack, anyway. So, you can hack these, too. d4r3 2 b 1337
            smo = 0.25  # ms This one can't be zero
            postsmo = 0.25  # ms
            min_len = 0.35  # ms

            n_min_len = int(np.ceil(min_len / dt))

            dys = butter_smooth(t, dy, timescale=smo, laggy=lag_butter)
            ddys = dy - dys
            # Smooth for noise reduction
            ddyss = butter_smooth(t, ddys, timescale=postsmo, laggy=lag_butter) if postsmo > 0 else ddys
            ddyss[ddyss < 0] = 0  # The negative part is pure noise. This isn't necessary, but it makes me feel better.

            # Find maximum in small neighborhood again, this time to hold high samples in order to debounce the flag
            ddys1 = np.concatenate((np.repeat(np.NaN, n_min_len), ddyss, np.repeat(np.NaN, n_min_len)))
            ddys2 = np.vstack(np.array([np.roll(ddys1, i) for i in range(n_min_len)]))
            ddys3 = np.nanmax(ddys2, axis=0)[n_min_len:-n_min_len]

            # Here's the initial ELM flag. It should catch the start of each ELM.
            elm_flag = ddys3 / max(ddys3) > threshold
            self['elm_detection_details'].update(dict(dys=dys, ddys=ddys, ddyss=ddyss, ddys3=ddys3))

        else:  # method == 2
            with warnings.catch_warnings():
                # It's okay to underflow during this division. ndy = 0 just means there's no ELM starting: fine.
                warnings.filterwarnings("ignore", message="underflow encountered in divide")
                warnings.filterwarnings("ignore", message="underflow encountered in true_divide")
                ndy = dy / max(dy)
            elm_flag = ndy > threshold
            self['elm_detection_details'].update(dict(ndy=ndy))  # , local_scale=local_scale))

        if debounce_setting > 1:
            # Do some smoothing to eliminate one or two element periods of ELM flag or not ELM flag
            # We don't want ELM flag to look like this:  0000101011111010000
            # Instead, we would like it to be like this: 0000001111111100000
            # The filterscopes sample so quickly that getting an edge wrong by one sample is inconsequential,
            # but getting a bounce (0000101111 instead of 0000011111) will count an extra ELM that's not real.
            debounce = int(copy.copy(debounce_setting) // 2) * 2 + 1  # Force it to be odd
            pad = int(debounce // 2)
            # Pad with zeros so we don't roll in junk
            elm_flag_b = np.append(np.append(np.zeros(pad), np.atleast_1d(elm_flag).astype(int)), np.zeros(pad))
            elm_flag_b2 = elm_flag_b * 0
            # Average the neighborhood of (debounce) points
            for i in range(-pad, pad + 1):
                elm_flag_b2 += np.roll(elm_flag_b, i) / (2.0 * pad + 1)
            elm_flag = np.round(elm_flag_b2[pad:-pad]).astype(bool)  # Strip off padding, round off, & convert to bool
            printd(' Debounced', topic='omfit_elm')

        # Sanitize the flag
        elm_flag2 = self.sanitize_elm_flag(np.atleast_1d(elm_flag))

        t2 = time.time()

        # Phase tree: force the ELM state to hold until D_alpha drops back down again ----------------------------------

        self.elm_hold_correction(t, y, elm_flag2)

        t3 = time.time()

        # Phase four: process th ELM flag to get phase, period, etc. ---------------------------------------------------

        self.calculate_elm_detection_quantities(t, elm_flag2)

        # Save details
        self['elm_detection_details'].update(dict(elm_flag=elm_flag2, timestamp=datetime.datetime.now()))

        self.detection_settings_used = copy.deepcopy(self['settings']['detection'])

        try:
            self.setdefault('plots', SortedDict())['detection'] = function_to_tree(self.elm_detection_plot, self)
            # self['plots']['detection2'] = OMFITpythonTask(  # Doesn't give access to defaultVars GUI
            #     'detection.py', fromString="parent._OMFITparent.elm_detection_plot()")
        except ImportError:
            type_, val_, traceback_ = sys.exc_info()
            printd('  Failed to load plot script to tree with function_to_tree.', topic='omfit_elm')
            if self.debug:
                printd(
                    '    Exception type = {type:}\n'
                    '    Exception value = {value:}\n'
                    '    Exception traceback = \n{trace:}'.format(type=type_, value=val_, trace=traceback_),
                    topic='omfit_elm',
                )
            # This won't work outside of OMFIT and we don't want it to

        printd('ELM detection finished for shot {:}'.format(self.shot), topic='omfit_elm')

        if calc_elm_freq:
            self.calc_frequency(plot_result=False)
            printd('Finished with extra ELM-related calculations.', topic='omfit_elm')

        self.status['detected'] = True

        t4 = time.time()
        printd(
            'New detection method took (s): total: {total:0.3f} setup: {setup:0.3f}, find start: {start:0.3f}, '
            'find end: {end:0.3f}, final processing: {process:0.3f}'.format(
                total=t4 - t0, setup=t1 - t0, start=t2 - t1, end=t3 - t2, process=t4 - t3
            ),
            topic='omfit_elm',
        )
        return

    def classic_edge_detect(self, report_profiling=False, calc_elm_freq=True):
        """
        Uses a Difference of Smooths (generalized from difference of gaussians edge detection) scheme to find the edges
        of D_alpha bursts. It also runs a DoS scheme on the derivative of D_alpha w.r.t. time.
        This allows time points (in the D_alpha series) to be flagged as soon as the ELM starts: it doesn't just get
        the tip, but instead it takes the whole thing.

        :param calc_elm_freq: bool
            Run ELM frequency calculation

        :param report_profiling: bool
            Reports time taken to reach / time taken between checkpoints in the code.
            Used to identify bottlenecks and support optimization.
        """

        t0 = time.time()
        printd('Running ELM detection for shot {:}...'.format(self.shot), topic='omfit_elm')
        if self.debug:
            self['detect_debugging'] = {}

        if tokamak(self.device) not in self.supported_devices:
            warnings.warn(
                'WARNING: Current server/device {} not found in list of supported devices. '
                'ELM detection is likely to fail! \nSuggestion: pick a device from the following list:{}'.format(
                    self.device, '\n    '.join([''] + self.supported_devices)
                )
            )

        # Shortcut
        elmdet1 = self['settings']['detection']
        elmdet = elmdet1['{:}_tuning'.format(self['settings']['detection']['smoother'])]

        # There are two smooths in the difference of gaussian scheme; one is typically 5-6x stronger than the other
        printd('  elm det: mild_smooth', elmdet['mild_smooth'], topic='omfit_elm')
        printd(
            '  elm det: threshold_on_difference_of_smoothed_derivatives_plus',
            elmdet['threshold_on_difference_of_smoothed_derivatives_plus'],
            topic='omfit_elm',
        )
        printd(
            '  elm det: threshold_on_difference_of_smoothed_derivatives_minus',
            elmdet['threshold_on_difference_of_smoothed_derivatives_minus'],
            topic='omfit_elm',
        )

        t1 = time.time()

        def smoother(sx, sy, s):  # this function selects which actual smoothing function to use and calls it
            t1_ = time.time()
            if self['settings']['detection']['smoother'] == 'gauss_smooth':
                ys = smooth_by_convolution(sy, xi=sx, window_size=s * 4, window_function='gaussian')
            elif self['settings']['detection']['smoother'] == 'asym_gauss_smooth':
                ys = asym_gauss_smooth(sx, sy, s, elmdet['gauss_center_lag'], elmdet['leading_side_width_factor'])
            elif self['settings']['detection']['smoother'] == 'rc_smooth':
                ys = pcs_rc_smooth(sx, sy, s)
            elif self['settings']['detection']['smoother'] == 'fft_smooth':
                ys = fft_smooth(sx, sy, s)
            elif self['settings']['detection']['smoother'] == 'combo':
                ys1 = pcs_rc_smooth(sx, sy, s)
                ys2 = smooth_by_convolution(sy, xi=sx, window_size=s * 4, window_function='gaussian')
                ys = (ys1 + ys2) / 2.0
            elif self['settings']['detection']['smoother'] == 'butter_smooth':
                ys = butter_smooth(sx, sy, cutoff=1.0 / (s * np.pi))  # s * pi gives s the same feel as in other functions
            else:
                raise ValueError(
                    "INVALID SMOOTHING FUNCTION IN ELM_DETECTION! Please set root['SETTINGS']['PHYSICS']['{}']"
                    "['ELM_detection']['smoother'] to one of the following: Valid options for smoothing function: "
                    "'gauss_smooth', 'rc_smooth', 'asym_gauss_smooth', 'combo', fft_smooth, butter_smooth".format(self.device_group)
                )
            t2_ = time.time()
            printd(' time taken = {} s'.format(t2_ - t1_), topic='omfit_elm')
            return ys

        t2 = time.time()

        # Get D_alpha
        self.get_dalpha()

        x = self['dalpha_time']
        y = self['dalpha_y']
        if x is None or y is None:
            if not self.quiet:
                print('Aborting ELM detection due to failure of D_alpha gathering')
            return  # Aborted during D_alpha gathering

        t3 = time.time()

        # Smooth D_alpha with two different timescales and take the difference
        s1 = smoother(x, y, elmdet['mild_smooth'])  # smooth 1 (mild smooth is in ms)
        s2 = smoother(x, y, elmdet['mild_smooth'] * elmdet['heavy_smooth_factor'])  # smooth 2
        ds = s1 - s2  # This is the difference of Gaussians which is central to the edge detection scheme

        printd(' s1, s2, and ds calculated for shot {:}'.format(self.shot), topic='omfit_elm')

        t4 = time.time()

        # When mild-heavy is greater than this threshold, it must be during ELM (relative to max diff)
        # Turn the relative threshold into an absolute threshold to which data can be compared
        thresh1 = elmdet['threshold_on_difference_of_smooths'] * max(ds)

        dyt = ds - thresh1  # Difference between ds and the threshold

        with warnings.catch_warnings():
            # It's okay to underflow during this division.
            warnings.filterwarnings("ignore", message="underflow encountered in divide")
            warnings.filterwarnings("ignore", message="underflow encountered in true_divide")
            d1 = np.gradient(s1) / np.gradient(x)  # Calculate time derivative of the smoothed D_alpha trace.

        printd(' gradient', topic='omfit_elm')
        if elmdet['mild_smooth_derivative_factor'] > 0:
            # Although the derivative is of smoothed data, it may still have too much noise & require more smoothing.
            d1 = smoother(x, d1, elmdet['mild_smooth'] * elmdet['mild_smooth_derivative_factor'])
        # Smooth the time derivative again. Now there are two versions of the smooth so we can take the difference.
        d2 = smoother(x, d1, elmdet['mild_smooth'] * elmdet['heavy_smooth_derivative_factor'])

        # Here's the difference of the smoothed derivatives.
        # We can now extend the difference of Gaussians technique to the derivative.
        dd = d1 - d2
        printd(' d1, d2, and dd calculated for shot {:}'.format(self.shot), topic='omfit_elm')

        t5 = time.time()

        # When mild(der)-heavy(der) is greater than a threshold, it must be on one of the edges of an ELM
        # Translate relative thresholds into absolute thresholds
        thresh2 = elmdet['threshold_on_difference_of_smoothed_derivatives_plus'] * max(dd)
        thresh3 = elmdet['threshold_on_difference_of_smoothed_derivatives_minus'] * min(dd)

        # When the diff of derivs is positive but the less smoothed derivative is still negative, we're in danger of
        # getting a false positive, so make the threshold higher
        if elmdet['d_thresh_enhance_factor'] != 1.0 or elmdet['neg_d_thresh_enhance_factor'] != 1.0:
            thresh2b = thresh2 * elmdet['d_thresh_enhance_factor']  # Enhanced +threshold on dd when ds is low
            thresh3b = thresh3 * elmdet['neg_d_thresh_enhance_factor']  # Enhanced -threshold on dd when ds is high
            thresh2 += d1 * 0
            thresh3 += d1 * 0
            thresh2[ds < (-thresh1)] = thresh2b
            thresh3[ds > thresh1] = thresh3b

        dd2 = dd - thresh2  # Compare difference of smoothed derivatives to threshold
        dd3 = thresh3 - dd

        # Make a flag to mark where the ELMs are - this is full length so saving it will be slow
        elm_flag = (dyt > 0) | (dd2 > 0) | (dd3 > 0)

        printd(' elm_flag calculated for shot {:}'.format(self.shot), topic='omfit_elm')

        t6 = time.time()

        if elmdet['debounce'] > 1:
            # Do some smoothing to eliminate one or two element periods of ELM flag or not ELM flag
            # We don't want ELM flag to look like this:  0000101011111010000
            # Instead, we would like it to be like this: 0000001111111100000
            # The filterscopes sample so quickly that getting an edge wrong by one sample is inconsequential,
            # but getting a bounce (0000101111 instead of 0000011111) will count an extra ELM that's not real.
            debounce = int(copy.copy(elmdet['debounce'])) / 2 * 2 + 1  # Force it to be odd
            pad = int(debounce // 2)
            elm_flag_b = np.append(np.append(np.zeros(pad), elm_flag), np.zeros(pad))  # Pad with zeros so we don't roll in junk
            elm_flag_b2 = elm_flag_b * 0
            # Average the neighborhood of (debounce) points
            for i in range(-pad, pad + 1):
                elm_flag_b2 += np.roll(elm_flag_b, i) / (2 * pad + 1)
            elm_flag = np.round(elm_flag_b2[pad:-pad]).astype(bool)  # Strip off padding, round off, & convert to bool
            printd(' Debounced', topic='omfit_elm')

        # Calculate useful quantities related to ELMs
        elm_flag2 = self.sanitize_elm_flag(elm_flag)

        t7 = time.time()

        if elmdet1['hold_elm_flag_until_low_dalpha']:
            self.elm_hold_correction(x, y, elm_flag2)

        t8 = time.time()

        self.calculate_elm_detection_quantities(x, elm_flag2)

        t9 = time.time()

        # Save details
        self['elm_detection_details'] = dict(
            s1=s1,
            s2=s2,
            ds=ds,
            d1=d1,
            d2=d2,
            dd=dd,
            dd2=dd2,
            dd3=dd3,
            dyt=dyt,
            thresh1=thresh1,
            thresh2=thresh2,
            thresh3=thresh3,
            elm_flag=elm_flag2,
            timestamp=datetime.datetime.now(),
        )

        self.detection_settings_used = copy.deepcopy(self['settings']['detection'])

        try:
            self.setdefault('plots', SortedDict())['detection'] = function_to_tree(self.elm_detection_plot, self)
            # self['plots']['detection2'] = OMFITpythonTask(  # Doesn't give access to defaultVars GUI
            #     'detection.py', fromString="parent._OMFITparent.elm_detection_plot()")
        except ImportError:
            type_, val_, traceback_ = sys.exc_info()
            printd('  Failed to load plot script to tree with function_to_tree.', topic='omfit_elm')
            if self.debug:
                printd(
                    '    Exception type = {type:}\n'
                    '    Exception value = {value:}\n'
                    '    Exception traceback = \n{trace:}'.format(type=type_, value=val_, trace=traceback_),
                    topic='omfit_elm',
                )
            # This won't work outside of OMFIT and we don't want it to

        printd('ELM detection finished for shot {:}'.format(self.shot), topic='omfit_elm')

        if calc_elm_freq:
            self.calc_frequency(plot_result=False)
            printd('Finished with extra ELM-related calculations.', topic='omfit_elm')

        t10 = time.time()
        self.status['detected'] = True

        if report_profiling:
            print('-----')
            print(
                'Time required to reach checkpoints in ELM_detection script with smooth_funct = {}: (shot {})'.format(
                    self['settings']['detection']['smoother'], self.shot
                )
            )
            times = [t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10]
            names = [
                '0',
                'setup',
                'function def',
                'd_alpha',
                'initial smoothing',
                'derivatives & smo',
                'define flag',
                'cleanup',
                'processing',
                'storage',
            ]
            for i, t in enumerate(times):
                print('t{}-t0 = {} s'.format(i, t - t0))
            print('')
            for i in range(1, len(times)):
                print('t{}-t{} = {} ms  {}'.format(i, i - 1, (times[i] - times[i - 1]) * 1000, names[i]))

            print('total time = {} ms'.format((t10 - t0) * 1000))
        printd(
            'Old detection method took (s): total: {total:0.3f} setup: {setup:0.3f}, find start: {start:0.3f}, '
            'find end: {end:0.3f}, final processing: {process:0.3f}'.format(
                total=t10 - t0, setup=t3 - t0, start=t7 - t3, end=t8 - t7, process=t10 - t8
            ),
            topic='omfit_elm',
        )
        return

    @staticmethod
    def sanitize_elm_flag(elm_flag):
        """
        Force ELM flag to start and stop in non-ELM state

        :param elm_flag: array (bool-like 1s & 0s or Trues & Falses)

        :return: Sanitized ELM flag that follows the rules
        """
        printd('  OMFITelm.sanitize_elm_flag() starting...', topic='omfit_elm')

        elm_flag2 = elm_flag.astype(int)  # Copy and a convert bool to int
        if elm_flag2[0] == 1:
            # Assuming the shot starts in a non-ELMing state and force the data to comply with this assumption.
            ww = tolist(np.where(elm_flag2 == 0)[0])[0]  # First element that's 0
            printd(' Need to fix problem w/ starting during ELM. Index of first non ELM slice: ww = {}'.format(ww), topic='omfit_elm')
            elm_flag2[0:ww] = 0  # Make any starting ELM state go away. If D_alpha measurement starts
            #                       during an ELM, we'll miss the first ELM. This is not a physically
            #                       realistic scenario, so it's okay
            # If we don't do this cleanup, then we'll have more ELM ends than ELM starts. Uneven numbers here will ruin
            # everything. This cannot be allowed.
        if elm_flag2[-1] == 1:
            # Also assume that we end in a non-ELMing state. This assumption will be enforced so that we have the same
            # number of ELM starts as ELM ends.
            ww = tolist(np.where(elm_flag2 == 0)[0])[-1]  # Last element that's 0
            printd(' Need to fix problem w/ ending during ELM. Index of last non ELM slice: ww = {:} .'.format(ww), topic='omfit_elm')
            elm_flag2[ww + 1 :] = 0
            # Need matching numbers of ELM starts and ELM ends, as noted above.

        return elm_flag2

    def elm_hold_correction(self, x, y, elm_flag2):
        """
        Forces ELM flag to stay in ELMy state (set) until D_alpha level returns to low (close to pre-ELM) level

        :param x: 1D float array
            Time base for data

        :param y: float array matching shape of x
            D_alpha measurements or similar signal

        :param elm_flag2: int array matching shape of x
            Flag for during-ELM state (1) vs. no-ELM state (0)

        :return: Adjusted ELM flag
        """

        ta0 = time.time()
        printd('  OMFITelm.elm_hold_correction() starting...', topic='omfit_elm')
        elmdet1 = self['settings']['detection']

        # Get the local minimum within a small window before each sample
        dx = np.median(np.diff(x))
        nwin = int(np.ceil(elmdet1['hold_elm_min_finding_time_window'] / dx))  # Time window size in samples
        n_hold_timeout = int(np.ceil(elmdet1['hold_elm_timeout'] / dx))
        y1 = np.concatenate((np.repeat(y.max(), nwin), y, np.repeat(y.max(), nwin)))  # Pad so we can roll nicely
        y2 = np.vstack(np.array([np.roll(y1, i) for i in range(nwin)]))  # Make a stack of rolls to different positions
        localmins = y2.min(axis=0)[nwin:-nwin]  # Each element is min from window from t-adv_t_win to t

        # Find start and end of each ELM
        starts = np.where(np.append(0, np.diff(elm_flag2) == 1))[0]
        ends = np.where(np.append(0, np.diff(elm_flag2) == -1))[0]

        if self.debug:
            self['detect_debugging']['starts'] = starts
            self['detect_debugging']['ends'] = ends
            self['detect_debugging']['elm_det_localmins'] = localmins
            self['detect_debugging']['elm_det_localmaxs'] = np.array([np.NaN] * len(starts))
            self['detect_debugging']['elm_det_threshs'] = np.array([np.NaN] * len(starts))
            self['detect_debugging']['elm_det_adv_starts'] = starts
            self['detect_debugging']['elm_det_adv_ends_pre'] = ends
            self['detect_debugging']['elm_det_adv_hold_until'] = np.zeros(len(starts), int)
            self['detect_debugging']['elm_det_changed'] = np.array([np.NaN] * len(starts))

        # Revise ELM flag
        unhandled = []
        for i in range(len(starts)):
            imax = y[starts[i] : ends[i]].argmax() + starts[i]
            localmax = y[imax]
            localmin = localmins[starts[i]]
            thresh = (localmax - localmin) * elmdet1['hold_elm_low_dalpha_threshold'] + localmin
            hold0 = np.where(y[imax:] < thresh)[0]
            if len(hold0):
                hold_until = hold0[0] + imax
                hold_limit = starts[i] + n_hold_timeout
                hold_until = min([hold_until, hold_limit])
                saveit = elm_flag2[hold_until - 1]
                elm_flag2[starts[i] : hold_until] = 1
            else:
                unhandled += [(i, starts[i], x[starts[i]])]
                saveit = hold_until = 0

            if self.debug:
                self['detect_debugging']['elm_det_localmaxs'][i] = localmax
                self['detect_debugging']['elm_det_threshs'][i] = thresh
                self['detect_debugging']['elm_det_adv_hold_until'][i] = hold_until
                self['detect_debugging']['elm_det_changed'][i] = elm_flag2[hold_until - 1] - saveit
                self['detect_debugging']['elm_det_hold_failed'] = unhandled

        ta1 = time.time()
        printd(
            '  Time required for correction to initial ELM detection (hold flag until low D_alpha): {} s'.format(ta1 - ta0),
            topic='omfit_elm',
        )

        return elm_flag2

    def calculate_elm_detection_quantities(self, x, elm_flag2, no_save=False, shot=None):
        """
        Finish detection by compressing the ELM flag to 4 points per ELM and calculating quantities like ELM phase

        Separate from .detect() to make room for different detection algorithms which will all finish the same way.

        Could also be used for convenience with an externally calculated ELM flag by passing in your own ELM detection
        results (and using no_save=True to avoid disturbing results calculated by the class, if you like).

        :param x: float array
            Time base in ms

        :param elm_flag2: int array matching length of x
            Flag indicating when ELMs are happening (1) or not (0)

        :param no_save: bool
            Disable saving of results; return them in a dictionary instead

        :param shot: [optional]
            Only used in announcements. If None, self.shot will be used. If you are passing in some other stuff and
            don't want inconsistent printd statements, you can pass in a different thing for shot.
            It would traditionally be an int, but it could be a string or something since it only gets printed here.

        :return: None or dict
            Returns results in a dict if no_save is set. Otherwise, results are just saved into the class and nothing is
            returned.
        """

        printd('  OMFITelm.calculate_elm_detection_quantities() starting...', topic='omfit_elm')
        shot = self.shot if shot is None else shot
        big_time = 2e6  # (ms)  A time so big that it will always be past the end of the time array.

        # Difference in ELM flag detects when the flag changes between ELM and no-ELM and marks with 1 and -1.
        # Leading zero inserted to make dimensions match.
        def2 = np.insert(np.diff(elm_flag2), 0, 0)
        w = np.where(def2 == 1)[0]  # Entered ELM state
        w2 = np.where(def2 == -1)[0]  # Exited ELM state
        spacer = np.mean(np.diff(x)) / 50.0  # This should be a small number, much smaller than other timescales of
        #                               interest, but it can't get so small that it underflows because then
        #                               there will be more than one point with the same time value, and that
        #                               will confuse the interpolation routine.
        if self.debug:
            self['detect_debugging']['elm_det_w'] = w
            self['detect_debugging']['elm_det_w2'] = w2

        # The times in newtime are when the ELM starts (x[w]), an
        # infinitesimal time later (x[w]+spacer), when the ELM ends (x[w2]),
        # and another infinitesimal time after that (x[w2]+spacer). This
        # lets us draw the nearly vertical line at the time when we go from
        # being in an ELM to not. Instead of storing all this ELM information
        # on the filterscope time base, we only need to store when the ELMs
        # start and stop, and we can interpolate everything else from there
        # (all the quantities we're dealing with here are linear, such as
        # time since last ELM, etc.)
        newtime = [x[w], x[w] + spacer, x[w2], x[w2] + spacer]

        # New ELM flag for storing ELM on/off without hogging all
        # the space used by elm_flag. Whereas elm_flag has as
        # many elements as the original d_alpha, new_elm_flag only
        # has four elements per ELM.
        new_elm_flag = [w * 0, w * 0 + 1, w2 * 0 + 1, w2 * 0]

        # ELM phase is ramps from 0 to 1 between ELMs, then jumps from 1 to
        # -1 when an ELM starts. So at x[w], ELM phase has reached 1. At
        # x[w]+spacer, it has changed to -1. At x[w2], the ELM is just ending
        # and ELM phase has recovered to 0. At x[w2]+spacer, it is still 0.
        elmphase = [w * 0 + 1, w * 0 - 1, w2 * 0, w2 * 0]

        printd(' Calculated elmphase for {:}'.format(shot), topic='omfit_elm')

        # Now we can figure out the the local ELM period and related quantities, which are useful in some filters.
        prev_elm_end = np.roll(x[w2], 1)  # The roll is so that this corresponds to the PREVIOUS ELM
        prev_elm_end[0] = 0
        prev_elm_start = np.roll(x[w], 1)
        prev_elm_start[0] = 0
        next_elm_start = np.roll(x[w], -1)
        next_elm_start[-1] = big_time
        since_last_elm = [x[w] - prev_elm_end, w * 0, w * 0, w * 0]
        since_last_elm_neg = [x[w] - prev_elm_end, x[w] - x[w2], w * 0, w * 0]
        # until_next_elm = [w*0, w*0, w*0, next_elm_start-x[w2]]
        until_next_elm = [w * 0, w * 0, x[w] - x[w2], next_elm_start - x[w2]]
        # Time from the end of one ELM to the start of the next one
        local_inter_elm_period = [x[w] - prev_elm_end, x[w2] - x[w], x[w2] - x[w], next_elm_start - x[w2]]
        # Time from the start of one ELM to the start of the next one
        local_total_elm_period = [x[w] - prev_elm_start, next_elm_start - x[w], next_elm_start - x[w], next_elm_start - x[w]]

        printd(' Calculated elm prev/next/since/period   {:}'.format(shot), topic='omfit_elm')

        # Format the arrays properly. They come out as a list of four arrays,
        # with an array of start times, start times+epsilon, end times, and
        # end times + epsilon. This has to be converted into a 1D array vs.
        # time.
        newtime = np.reshape(np.transpose(newtime), -1)
        elmphase = np.reshape(np.transpose(elmphase), -1)
        new_elm_flag = np.reshape(np.transpose(new_elm_flag), -1)
        since_last_elm = np.reshape(np.transpose(since_last_elm), -1)
        since_last_elm_neg = np.reshape(np.transpose(since_last_elm_neg), -1)
        until_next_elm = np.reshape(np.transpose(until_next_elm), -1)
        local_inter_elm_period = np.reshape(np.transpose(local_inter_elm_period), -1)
        local_total_elm_period = np.reshape(np.transpose(local_total_elm_period), -1)

        # Now pad all quantities so that ELM phase starts at 0
        start_time = 0  # ms
        first_elm_start = newtime[0]
        newtime = np.append(start_time, newtime)
        elmphase = np.append(0, elmphase)
        new_elm_flag = np.append(0, new_elm_flag)
        since_last_elm = np.append(0, since_last_elm)
        since_last_elm_neg = np.append(0, since_last_elm_neg)
        until_next_elm = np.append(newtime[1] - start_time, until_next_elm)
        local_inter_elm_period = np.append(first_elm_start, local_inter_elm_period)
        local_total_elm_period = np.append(first_elm_start, local_total_elm_period)

        if no_save:
            return dict(
                elm_phase=elmphase,
                elm_flag=new_elm_flag,
                inter_elm_period=local_inter_elm_period,
                total_elm_period=local_total_elm_period,
                since_last_elm=since_last_elm,
                since_last_elm_neg=since_last_elm_neg,
                until_next_elm=until_next_elm,
                elm_time=newtime,
                success=True,
            )
        else:
            # Store the results
            self['elm_phase'] = elmphase
            self['elm_flag'] = new_elm_flag
            self['inter_elm_period'] = local_inter_elm_period
            self['total_elm_period'] = local_total_elm_period
            self['since_last_elm'] = since_last_elm
            self['since_last_elm_neg'] = since_last_elm_neg
            self['until_next_elm'] = until_next_elm
            self['elm_time'] = newtime
            self['success'] = True
        return

    def calc_frequency(self, method=None, plot_result=False):
        """
        Calculates ELM frequency

        :param method: None or int
            None: use value in settings
            int: manual override: ID number of method you want to use
            - 0: very simple: 1 / local period
            - 1: simple w/ smooth
            - 2: process period then invert
            - 3: method 0 then interpolate and smooth

        :param plot_result: bool
            Make a plot at the end
        """

        t0 = time.time()

        printd('Starting ELM_frequency calculation...', topic='omfit_elm')
        method = self['settings']['misc']['elm_freq_method'] if method is None else method

        if 'total_elm_period' not in self:
            printd(
                '  ELM_detection needs to be done prior to ELM frequency calculation. Results not ready: '
                '"total_elm_period" in self = {}.'.format('total_elm_period' in self),
                topic='omfit_elm',
            )
            self.detect(calc_elm_freq=False)

        t = self['elm_time']
        period = self['total_elm_period']

        # Define smoothing timescale in ms
        smo = np.median(period) * 3  # Smooth over about 3 ELM periods

        if method == 1:
            printd('ELM frequency method 1: simple w/ smooth', topic='omfit_elm')
            # This method doesn't give enough weight to ELM free periods
            fr = 1.0 / period
            fr = smooth(fr, 4 * 5)  # There are 4 points per ELM. 20 point smoothing smooths over 5 ELMs.
            tf = t

        elif method == 2:
            printd('ELM frequency method 2: process period then invert', topic='omfit_elm')
            # This method is very similar to what the PCS does in real time, the only differences being that this one
            # has access to offline ELM detection, which is potentially better, and it can use a forward-backward
            # smoothing filter.

            # Get the previous period
            prev_period = np.roll(period, 4)  # There are 4 points per ELM
            prev_period[0] = 1e3

            # Calculate time since the START of the last ELM (the value in the tree is since the END of the last ELM).
            it_start0 = np.arange(len(t))
            it_start = ((it_start0 - 1) // 4).astype(np.int64) * 4 + 1
            it_start[0] = 0
            t_start = t[it_start]
            since_start = t - t_start

            # Interpolate onto a nicer time base
            cut = 4 + 1  # Cut off large period at the start of the shot (it doesn't mean anything anyway)
            t2 = self['dalpha_time']
            pp = interp1d(t[cut:], prev_period[cut:], bounds_error=False, fill_value=0)(t2)
            s = interp1d(t[cut:], since_start[cut:], bounds_error=False, fill_value=0)(t2)

            # Don't let time since ELM be less than the previous ELM period. This prevents division by small numbers and
            # reports of high ELM frequency right after ELMs.
            s2 = copy.copy(s)
            s2[s < pp] = pp[s < pp]

            # Cut off the extra large since value at the start of the shot to prevent long periods from smoothing into
            # the start of ELMing.
            s2[s2 > 1000] = 1000.0

            # Smooth before taking reciprocal to get frequency.
            s3 = butter_smooth(t2, s2, cutoff=1.0 / (smo * np.pi))

            # Calculate frequency
            fr = 1.0 / s3
            tf = t2  # Record the time relevant for this calculation of ELM frequency

        elif method == 3:
            printd('ELM frequency method 3: take very simple method 0 then interpolate and smooth', topic='omfit_elm')
            fr0 = 1.0 / period

            t2 = self['dalpha_time']
            fr = interp1d(t, fr0, bounds_error=False, fill_value=0)(t2)
            fr_norm = np.nanmean(fr)
            fr_norm = 1 if fr_norm == 0 or np.isnan(fr_norm) else fr_norm
            with warnings.catch_warnings():
                # It's okay to underflow during this division.
                warnings.filterwarnings("ignore", message="underflow encountered in multiply")
                fr = butter_smooth(t2, fr / fr_norm, cutoff=1.0 / (smo * np.pi)) * fr_norm
            tf = t2

        else:  # method == 0
            printd('ELM frequency method 0: very simple', topic='omfit_elm')
            # This method could be noisy because of no smoothing
            fr = 1.0 / period
            tf = t

        fr *= 1000.0  # Convert kHz to Hz

        self['elm_freq_time'] = tf
        self['elm_freq'] = fr
        self['elm_freq_method'] = copy.copy(method)

        if plot_result:
            self.elm_frequency_plot()
        t1 = time.time()

        try:
            self.setdefault('plots', SortedDict())['frequency'] = function_to_tree(self.elm_frequency_plot, self)
        except ImportError:
            printd('  Failed to load plot script to tree with function_to_tree', topic='omfit_elm')
            # This won't work outside of OMFIT and we don't want it to

        printd('ELM frequency calculation took {} ms'.format((t1 - t0) * 1000), topic='omfit_elm')
        self.status['calcs'] = True
        return

    def filter(self, times_to_filter, cer_mode=False, stimes=0.0, apply_elm_filter=True, debug=None, on_failure=None):
        """
        Use ELM detector & ELM filtering settings to determine whether each element in an array of times is good or bad.

        :param times_to_filter: numeric 1d array or a list of such arrays
            For most signals (like Thomson scattering data): a single 1D array of times in ms. For CER: a list of
            1D arrays, one for each CER channel.

        :param cer_mode: bool
            Assume times_to_filter is a list of lists/arrays, one entry per channel (loop through elements of
            times, each one of which had better itself have several elements)

        :param stimes: float -OR- array or list of arrays matching dimensions of times_to_filter
            Averaging time window for CER. This typically set to 2.5 ms, but it can vary (read it from your data if
            possible)

        :param apply_elm_filter: bool
            Debugging option: if this is set False, the script will go through its pre-checks and setup without actually
            doing any ELM-filtering.

        :param debug: bool [optional]
            Override class debug flag for just the filtering run. Leave at None to use self.debug instead of overriding.

        :param on_failure: str [optional]
            Override class on_failure flag. Sets behavior when filtering is not possible.
            'pass': Pass all data (elm_okay = 1 for all)
            'exception': raise an exception. (default for unrecognized)

        :return: array of bools or list of arrays matching shape of times_to_filter
            Flag indicating whether each sample in times_to_filter is okay according to ELM filtering rules
        """

        debug = self.debug if debug is None else debug
        if debug:
            self.setdefault('debug_elm_filter', dict())

        # Sanitize
        times_to_filter = np.atleast_1d(times_to_filter)

        # Find number of timing channels being used. CER has potentially different timing for each channel, so we treat
        # each channel on its own timing. Thomson has the same timing for every spatial chord on the same system, so
        # it's done as if it has only one timing channel.
        dtf = dimens(times_to_filter)
        if dtf == 1:
            # This is Thomson-like. ELM filter will be put inside a loop over Thomson systems (probably only one or two
            # are used at a time; maybe all three)
            nchan = 1
        else:
            # This is CER-like. Times to filter is a list of timing arrays. The length of the top level list is the
            # number of channels.
            nchan = len(times_to_filter)

        printd('nchan = {}'.format(nchan), topic='omfit_elm')

        # Warn the user if they made a weird setup (hopefully it works, anyway)
        if nchan == 1 and cer_mode:
            printw(
                "WARNING: ELM filter on shot {:}  detected only one channel, but this is CER mode. More than one "
                "channel expected. Do you know what you're doing? Let's see if this will work.".format(self.shot)
            )
        if nchan != 1 and not cer_mode:
            printw(
                "WARNING: ELM filter on shot {:} detected more than one channel, but CER mode was not enabled. "
                "This could be a problem.".format(self.shot)
            )

        # Process stimes
        if np.all(np.atleast_1d(stimes == 0)):
            # Turn off strict ELM filtering for stime=0. There is no averaging window so we don't have to worry about
            # how we treat the averaging window.
            strict = False
        else:
            strict = self['settings']['filtering']['CER_entire_window_must_pass_ELM_filter']

        dst = dimens(stimes)
        printd('dimens(stimes) = {}'.format(dst), topic='omfit_elm')
        if dst == 0:
            printd('stimes input as scalar or single element vec: {}'.format(stimes), topic='omfit_elm')
            # A scalar was provided. Make it be shaped like times_to_filter so they can zip together
            if nchan > 1:  # CER-like: times_to_filter is a list of timing arrays
                st0 = []
                for t in times_to_filter:
                    st = stimes + t * 0
                    st0 += [st]
                stimes = st0
                printd('stimes transformed from scalar into list of arrays vs time (CER-like)', topic='omfit_elm')
            else:  # Thomson-like: times_to_filter is a single timing array
                stimes += times_to_filter * 0
                printd('stimes transformed from scalar into array vs time (Thomson-like)', topic='omfit_elm')
        elif dst == 1:
            printd('stimes input as vector', topic='omfit_elm')
            if nchan == 1:
                # Everything is fine. stimes and times_to_filter are both Thomson-like. No action required. If they have
                # different lengths, the setup is wrong somewhere else and cannot be salvaged here.
                printd('times_to_filter and stimes both were 1D. No transformation performed on stimes', topic='omfit_elm')
            else:
                # This is a problem. stimes and times_to_filter do not match. This is probably going to be fatal,
                # but there is ONE thing we can try.
                # The only way this works is if stime is constant with time and varies by channel.
                # Assume that the user gave us stime vs. channel with no time dependence.
                # YOU PROBABLY SHOULD NOT DO IT THIS WAY
                printw('WARNING: times_to_filter is CER-like but stimes has only one dimension.')
                if len(tolist(stimes)) != len(times_to_filter):
                    # This should just fail if the lengths aren't the same. If the lengths aren't the same, then our
                    # assumption is wrong and the setup flaw cannot be solved here, so it's okay to just fail and let
                    # debugging commence elsewhere.
                    raise OMFITexception('FAIL: Lengths do not match: stimes & times_to_filter.')
                printw(
                    'Assuming that stimes was specified as one scalar per CER channel. This is not a great way to '
                    'set this up! Do it some other way, please!'
                )
                st0 = []
                for s, t in zip(tolist(stimes), times_to_filter):
                    st = s + t * 0  # s should be a scalar and t should be a vector
                    st0 += [st]
                stimes = st0  # stimes should be a list of vectors
                printd(
                    'times_to_filter was CER-like list of arrays but stimes was just a vector.\nTransformed each '
                    'scalar element of stimes into an array vs. time, giving a list of arrays.',
                    topic='omfit_elm',
                )
        else:  # stimes should be 2D
            if nchan > 1:
                # Everything is fine. stimes and times_to_filter are both CER-like
                printd('times_to_filter and stimes were both lists of arrays (CER-like). No transformation performed.', topic='omfit_elm')
            else:
                # Problem! stimes is CER-like and times_to_filter is Thomson-like. I don't know how to deal with this
                # so just fail.
                raise OMFITexception("ERROR: stimes has more dimensions than times_to_filter. I can't deal with this")

        if (not self.get('success', False)) or (self.detection_settings_used != self['settings']['detection']):
            # Run ELM detection if needed
            self.detect()
        if not self.get('success', False):
            fail_msg = 'Aborting ELM filter due to failure in ELM detection ({}#{}).'.format(self.device, self.shot)
            if (on_failure or self.on_failure) == 'pass':
                print(fail_msg)
                return np.ones(len(times_to_filter), bool)
            else:
                raise OMFITexception(
                    fail_msg + ' Set on_failure="pass" during OMFITelm init or change self.on_failure="pass" to '
                    'disable ELM filtering instead of raising an exception for this type of failure.'
                )

        # Try to form an ELM filter
        if apply_elm_filter:
            elm_time = copy.copy(self['elm_time'])
            elm_phase = copy.copy(self['elm_phase'])
            elm_since = copy.copy(self['since_last_elm'])

            # Need to add a point to elm since so that the time after the last detected ELM can be processed correctly
            # with regards to elm_since_accept_above.
            elm_phase = np.append(elm_phase, max(elm_phase[-1], 0.00))  # If there is no more ELMs, there is no more phase.
            elm_since = np.append(elm_since, max(self['settings']['detection']['time_window']) + 1 - max(elm_time))
            elm_time = np.append(elm_time, max(self['settings']['detection']['time_window']) + 1)
            # Pad max time by 1ms to gurantee that elm_time does not contain repeat time points.

            # Inject poinits to allow the correct processing of the time before the first ELM.
            elm_time = np.insert(elm_time, 0, [min(elm_time) - 0.2, min(elm_time) - 0.1])
            elm_phase = np.insert(elm_phase, 0, [0, 0])
            elm_since = np.insert(elm_since, 0, [1000, 1000])

            # filterCER had assume_sorted=True here. Faster? How much faster?
            elm_since_i = interp1d(elm_time, elm_since, bounds_error=False, fill_value=0.0)
            elm_phase_i = interp1d(elm_time, elm_phase, bounds_error=False, fill_value=0.0)

            if debug:
                try:
                    OMFIT['scratch']['elm_phase_i'] = copy.copy(elm_phase_i)
                except (NameError, KeyError):
                    self['debug_elm_filter']['elm_phase_i'] = copy.copy(elm_phase_i)
                else:
                    self['debug_elm_filter']['elm_phase_i'] = "see OMFIT['scratch']"

                printd(
                    '  OMFITelm.filter(): Minimum timestep between ELM timing data: min(diff(elm_time)) = {}. '
                    'THIS WILL RUIN THE INTERPOLATION IF IT IS NOT GREATER THAN ZERO'.format(min(np.diff(elm_time)))
                )
                printd('  OMFITelm.filter(): elm_time = {}'.format(array_info(elm_time)))
            if self.debug_plots:
                import matplotlib as mpl
                from matplotlib import pyplot

                fig, ax = pyplot.subplots(1)
                fig.canvas.set_window_title('OMFITelm.filter() debugging')
                ax.plot(elm_time[:-1], np.diff(elm_time))
                ax.set_xlabel('elm_time[:-1] (ms)')
                ax.set_ylabel('diff(elm_time) (ms)')

            elm_okay = []
            if not cer_mode:
                times_to_filter = [times_to_filter]  # Make this a 1 element list containing one time array
                # If it is cer mode, then times_to_filter should be a many element list containing a time array for
                # each channel

            if debug:
                # Make sure these are defined in case the loop variable is empty
                self['debug_elm_filter']['elm_time_in'] = []
                self['debug_elm_filter']['elm_phase_ts'] = []

            for times_to_f, stime in zip(times_to_filter, stimes):  # Loop through CER channels.
                # If not doing CER, then there will only be one pass through this loop
                if times_to_f is None:  # Check for bad channels
                    printw('Invalid list of times for this channel. Skipping...')
                    elm_okay_i = True  # This should be just one element I think because the None is one element
                    elm_okay += [elm_okay_i]
                    continue  # Stop processing this channel

                # Test 1: does an ELM start within the averaging window? The discontinuity in ELM phase could cause a
                # problem with checking the endpoints of the window. This is CER relevant.
                elm_start_in_window = (times_to_f * 0).astype(bool)  # Setup array
                if np.any(np.atleast_1d(stime > 0)):  # We can leave this as all False if stime == 0.
                    twin_end = times_to_f + stime  # End of time window
                    # twin_mid = times_to_f+stime/2.0
                    for i, t in enumerate(times_to_f):  # Loop through CER time slices
                        # Find all the ELMs that started in this window (if any)
                        w = np.where((elm_time > times_to_f[i]) * (elm_time < twin_end[i]))[0]
                        if len(w) > 0:  # If at least one ELM started in this window, it's an ELMy window.
                            elm_start_in_window[i] = True

                # Evaluate the interpolation at the middle of the time window
                # elm_since_mid = elm_since_i(times_to_f + stime / 2.0)
                elm_phase_mid = elm_phase_i(times_to_f + stime / 2.0)

                if debug:
                    self['debug_elm_filter']['elm_time_in'] = copy.copy(times_to_f)
                    self['debug_elm_filter']['elm_phase_ts'] = copy.copy(elm_phase_mid)

                # Elm filter
                if strict:
                    # Evaluate the interpolation at the start/end of the time window and make sure the whole time
                    # window passes the ELM filter

                    # Set the elm_since value to use to be the one from the end of the time window
                    elm_since_use = elm_since_i(times_to_f)
                    # Find elm phase at the start and end end of the time window
                    elm_phase_st = elm_phase_i(times_to_f)
                    elm_phase_end = elm_phase_i(times_to_f + stime)

                    # Are the endpoints of the time window within the acceptable ELM phase range?
                    elm_okay_i = (
                        (elm_phase_st >= self['settings']['filtering']['elm_phase_range'][0])
                        * (elm_phase_st <= self['settings']['filtering']['elm_phase_range'][1])
                        * (elm_phase_end >= self['settings']['filtering']['elm_phase_range'][0])
                        * (elm_phase_end <= self['settings']['filtering']['elm_phase_range'][1])
                    )
                else:
                    # Not strict: just test the middle of the window for phase

                    # Evaluate the interpolation at the middle of the time window

                    # Set the elm_since value to use to be the one from the middle of the time window
                    elm_since_use = elm_since_i(times_to_f + stime / 2.0)
                    # Find ELM phase at the middle of the time window
                    elm_phase_mid = elm_phase_i(times_to_f + stime / 2.0)

                    # Is the slice within the acceptable ELM phase range?
                    elm_okay_i = (elm_phase_mid >= self['settings']['filtering']['elm_phase_range'][0]) * (
                        elm_phase_mid <= self['settings']['filtering']['elm_phase_range'][1]
                    )

                if self['settings']['filtering']['elm_since_accept_above'] > 0:
                    # Has so much time passed since the ELM that we don't care what the ELM phase is anymore?
                    # (i.e. it's gone ELM-free)
                    elm_okay_i += elm_since_use > self['settings']['filtering']['elm_since_accept_above']

                if (self['settings']['filtering']['elm_since_reject_below'] > -10) and (
                    min(self['settings']['filtering']['elm_phase_range']) >= 0
                ):
                    # Make sure that this filter does not affect time after detection_window (~last point in elm_time)
                    w = np.where((times_to_f > min(elm_time)) * (times_to_f < max(elm_time)))
                    # elm_okay_i[w]: Has so little time passed since the last ELM that we don't want this slice,
                    # regardless of the phase?
                    # (i.e. two ELMs in rapid succession made ELM phase ramp really fast and it's misleading).
                    # Be careful to apply this only to the time range where ELM data exist, because ELM since is set to
                    # zero outside of this range even though it's not really the same meaning of zero there.
                    elm_okay_i[w] *= elm_since_use[w] > self['settings']['filtering']['elm_since_reject_below']

                    printd('elm_since_reject_below =', self['settings']['filtering']['elm_since_reject_below'], topic='omfit_elm')
                else:
                    printd('elm_since_reject_below was <= -10, so this check is disabled', topic='omfit_elm')

                # Flag any time where an ELM starts in the averaging window. Relevant for CER where stime > 0.
                # Does nothing if stime == 0 because elm_start_in_window should be all False.
                elm_okay_i = elm_okay_i * (~elm_start_in_window)

                elm_okay += [elm_okay_i]
            if not cer_mode and len(elm_okay):
                elm_okay = elm_okay[0]  # Strip away the 1 element list if not CER mode
        else:
            # If the ELM filter is not being applied, then mark all slices as okay with respect to ELMs
            if cer_mode:
                elm_okay = [(t * False + True).astype(bool) for t in times_to_filter]
            else:
                elm_okay = (times_to_filter * 0 + 1).astype(bool)

        printd('ELM filter complete for shot {:}'.format(self.shot), topic='omfit_elm')
        return elm_okay

    # Plots

    def plot(self, fig=None, axs=None):
        """
        Launches default plot, which is normally self.elm_detection_plot(). Can be changed by setting self.default_plot.

        :return: (Figure instance, array of Axes instances)
            Tuple containing references to figure and axes used by the plot
        """
        from matplotlib import pyplot

        if fig is None:
            fig = pyplot.gcf()
        return getattr(self, self.default_plot, self.elm_detection_plot)(fig=fig, axs=axs)

    def elm_frequency_plot(self, time_range=None, time_range_for_mean=None, overlay=False, fig=None, axs=None, quiet=False, **plotkw):
        """
        Plots calculated ELM frequency

        :param time_range: two element iterable with numbers
            The plot will initially zoom to this time range (ms).

        :param time_range_for_mean: two element numeric, True, or False/None
            - True: time_range will be used to define the interval, then the mean ELM frequency will be calculated
            - False or None: no mean ELM frequency calculation
            - Two element numeric: mean ELM frequency will be calculated in this interval; can differ from time_range.

        :param overlay: bool
            Overlay on existing figure instead of making a new one

        :param fig: matplotlib Figure instance
            Figure to use when overlaying.

        :param axs: List of at least two matplotlib Axes instances
            Axes to use when overlaying

        :param quiet: bool
            Convert all print to printd

        :param plotkw: Additional keywords are passed to pyplot.plot()

        :return: (Figure instance, array of Axes instances)
        """
        import matplotlib as mpl
        from matplotlib import pyplot

        def printq(*args):
            if quiet:
                printd(*args, topic='OMFITelm')
            else:
                print(*args)

        # Make sure results are ready
        if 'elm_freq' not in self:
            self.calc_frequency(plot_result=False)

        # Figure setup
        if overlay or fig:
            if fig is None:
                fig = pyplot.gcf()
            if axs is None:
                ax0 = fig.add_subplot(211)
                ax1 = fig.add_subplot(212, sharex=ax0)
                axs = [ax0, ax1]
        else:
            fig, axs = pyplot.subplots(2, sharex='col')

        axs[0].set_ylabel(r'$D_{\alpha}$ (AU)')
        axs[1].set_xlabel('Time (ms)')
        axs[1].set_ylabel('ELM frequency (Hz)')
        axs[1].set_title('Frequency calculation method {}'.format(self['elm_freq_method']))
        axs[0].label_outer()
        axs[0].xaxis.get_offset_text().set_visible(False)

        # Data setup
        which_fs = self['dalpha_filters']
        x = self['dalpha_time']
        y = self['dalpha_y']

        xf = self['elm_freq_time']
        f = self['elm_freq']

        if time_range is None:
            # Pick time range
            tw = self['settings']['detection']['time_window']
            time_range = [max([tw[0], x.min()]), min([tw[1], x.max()])]
        axs[1].set_xlim(time_range)

        # Do plot
        use_mf = time_range_for_mean is not None and time_range_for_mean is not False
        axs[0].plot(x, y, **plotkw)
        fllw = plotkw.pop('lw', mpl.rcParams['lines.linewidth'] * (0.5 if use_mf else 1))
        fllw = plotkw.pop('linewidth', fllw)
        freq_line = axs[1].plot(xf, f, zorder=0, lw=fllw, **plotkw)
        axs[0].set_title('+'.join(tolist(which_fs)))

        if use_mf:
            if time_range_for_mean is True:
                time_range_for_mean = time_range
            w = (x >= time_range_for_mean[0]) & (x <= time_range_for_mean[1])
            f1 = interp1d(xf, f, bounds_error=False, fill_value=np.NaN)(x)[w]
            mean_freq = np.nanmean(f1)
            std_freq = np.nanstd(f1)
            printq('Mean ELM frequency during interval {} ms = {:0.3f}+/-{:0.3f} Hz'.format(time_range_for_mean, mean_freq, std_freq))
            try:
                # Importing from omfit_classes.utils_plot has side effects that may be undesirable in command-line stand-alone testing
                contrast_color = contrasting_color(freq_line)
            except NameError:
                contrast_color = 'r'
            axs[1].errorbar(
                np.mean(time_range_for_mean),
                mean_freq,
                std_freq,
                np.std(time_range_for_mean),
                marker='d',
                ls=' ',
                zorder=2,
                lw=mpl.rcParams['lines.linewidth'] * 1.3 + 1.3,
                label=r'$\langle f_{{ELM}} \rangle$ = {:0.2f} Hz'.format(mean_freq),
                color=contrast_color,
            )
            axs[1].legend(loc=0, numpoints=1)

        try:
            # Getting at OMFIT plot utilities when doing stand-alone command-line stuff can be a burden
            cornernote(shot=self.shot, device=self.device, time='')
        except NameError:
            fig.text(0.99, 0.01, '{}#{}'.format(self.device, self.shot), fontsize=10, ha='right', transform=pyplot.gcf().transFigure)

        return fig, axs

    def elm_detection_plot(self, **kw):
        """
        Plots important variables related to ELM detection

        :return: (Figure instance, array of Axes instances)
        """
        method = self['settings']['detection'].get('detection_method', 0)
        method = self.check_detection_inputs(method)
        if method == 0:
            f, ax = self.classic_elm_detection_plot(**kw)
        elif method == 1:
            f, ax = self.jump_and_hold_elm_detection_plot(**kw)
        else:
            raise ValueError('Unrecognized ELM detection method: {}\nValid options are: [0, 1]'.format(method))

        return f, ax

    def get_quantity_names(self):
        """
        Gives names of quantities like D_alpha or d/dt(T_e) and ELM vs sawtooth
        :return: tuple of strings containing:
            - Name of the raw Y variable (like D_alpha)
            - Name of the event being detected (like ELM or sawtooth) for use in middle of sentence
            - Name of event being detected (like ELM or Sawtooth) for use at start of sentence (capitalized 1st letter)
        """
        if self.mode == 'sawtooth':
            tn = r'\frac{d}{dt}T_e'  # thing name
            en = 'sawtooth'  # event name
            cen = 'Sawtooth'
        else:
            tn = r'D_\alpha'
            en = cen = 'ELM'
        return tn, en, cen

    def _generate_filterscope_label(self):
        """
        Set up label for list of "filterscopes", which are now generalized to input signals

        :return: string
            Label to use for "filterscopes" or other raw input signals
        """
        filterscope = self['settings']['detection']['filterscopes']
        fsl = tolist(filterscope)
        if len(fsl) > 1:
            filterscope_label = []
            k = 0
            while (len(', '.join(filterscope_label)) < 24) and k < (len(fsl)):
                filterscope_label += ['{:}'.format(fsl[k])]
                k += 1
            if k < len(fsl):
                filterscope_label += ['...']
            filterscope_label = ', '.join(filterscope_label)
        else:
            filterscope_label = fsl[0]
        return filterscope_label

    def _get_time_mask(self, crop_data_to_zoom_range=True, time_zoom=None):
        """
        Prepares mask for plotting only part of the time history
        :param crop_data_to_zoom_range: bool
        :param time_zoom: two element numeric iterable
        :return: tuple containing:
            time_range: a two element list containing the start and stop times in ms
            wt: bool array for masking things shaped like dalpha_time.
        """
        time_zoom = (
            {'DIII-D': [0, 8000], 'NSTX': [0, 6000], 'NSTXU': [0, 6000]}.get(tokamak(self.device), [0, 8000])
            if time_zoom is None
            else time_zoom
        )
        timemin = max([time_zoom[0], min(self['dalpha_time'])])
        timemax = min([time_zoom[1], max(self['dalpha_time'])])
        time_range = [timemin, timemax]

        if crop_data_to_zoom_range:
            wt = (self['dalpha_time'] >= timemin) & (self['dalpha_time'] <= timemax)
        else:
            wt = self['dalpha_time'] > -1e20  # Should be all True

        return time_range, wt

    def plot_phase(self, ax=None, standalone=True):
        """Plots ELM phase"""
        ax = pyplot.gca() if ax is None else ax
        tn, en, cen = self.get_quantity_names()
        ax.set_title('{} phase is < 0 during events, > 0 between events'.format(cen))
        ax.plot(self['elm_time'], self['elm_phase'], label='{} phase'.format(cen))
        ax.axhline(0, color='k', linestyle='-.')

        # Add in ELM phase as it is evaluated on TS time base
        try:  # Might not work: is fastTS even hooked up?
            ts_sys0 = fastTS['SETTINGS']['PHYSICS']['TS_systems'][0]
            ts_time = fastTS['INPUTS']['current']['filtered_TS'][ts_sys0]['time']
        except (NameError, KeyError, TypeError):
            pass
        else:
            elm_phase_ts = interp1d(self['elm_time'], self['elm_phase'], fill_value=0, bounds_error=False)(ts_time)
            ax.plot(ts_time, elm_phase_ts, '.', label='{} phase on TS time'.format(cen))
        if standalone:
            self._generic_plot_annotations(ax=ax)
        return

    def _generic_plot_annotations(self, f=None, ax=None):
        """
        Convenient annotation package to be used for most plots
        :param f: Figure instance
        :param ax: Axes instance
        """
        f = (pyplot.gcf() if ax is None else ax.get_figure()) if f is None else f
        ax = f.gca() if ax is None else ax
        ax.set_xlabel('Time (ms)')
        try:
            # Getting at OMFIT plot utilities when doing stand-alone command-line stuff can be a burden
            cornernote(shot=self.shot, device=self.device, time='', ax=ax)
        except NameError:
            f.text(0.99, 0.01, '{}#{}'.format(self.device, self.shot), fontsize=10, ha='right', transform=f.transFigure)
        return

    def plot_signal_with_event_id(self, ax=None, wt=None, shade_elms=True, standalone=True):
        """
        Plots the signal used for detection and shades or recolors intervals where events are detected
        :param ax: Axes instance
        :param wt: array for masking
        :param shade_elms: bool
        :param standalone: bool
        """
        ax = pyplot.gca() if ax is None else ax
        tn, en, cen = self.get_quantity_names()
        if wt is None:
            time_range, wt = self._get_time_mask()
        ax.set_title('${}$ with final {} identification in red'.format(tn, en))
        ax.plot(self['dalpha_time'][wt], self['dalpha_y'][wt], label='${}$'.format(tn))
        yy = copy.copy(self['dalpha_y'])
        not_elm = ~self['elm_detection_details']['elm_flag'].astype(bool)
        # elm = dets['elm_flag']  # If you needed a flag for when an ELM is happening
        yy[not_elm] = np.NaN
        xx = copy.copy(self['dalpha_time'])
        xx[not_elm] = np.NaN

        if shade_elms:
            ax.plot(xx[wt], yy[wt], 'r')
            ax.fill_between(xx[wt], yy[wt] * 0, yy[wt], color='r', alpha=0.25, label=cen)
        else:
            ax.plot(xx[wt], yy[wt], 'r', label=cen)

        if standalone:
            self._generic_plot_annotations(ax=ax)
        return

    def plot_more_event_timing_info(self, ax, crop_elm_since=True, standalone=True):
        """
        Plots details related to ELM/sawtooth/whatever timing, like time since the last event
        :param ax: Axes instance
        :param crop_elm_since: bool
        :param standalone: bool
        """
        ax = pyplot.gca() if ax is None else ax
        tn, en, cen = self.get_quantity_names()
        ax.set_title('More {} timing info'.format(en))
        ax.plot(self['elm_time'], self['since_last_elm'], label='Time since last {} (ms)'.format(en))
        ax.plot(self['elm_time'], self['until_next_elm'], label='Time until next {} (ms)'.format(en))
        ax.plot(self['elm_time'], self['total_elm_period'], label='Local {} period duration start-start (ms)'.format(en))
        ax.plot(self['elm_time'], self['inter_elm_period'], label='Local inter/intra {} period start-end or end-start (ms)'.format(en))
        if crop_elm_since > 0:
            if crop_elm_since is True:
                crop_elm_since = np.mean(self['total_elm_period'])
            ax.set_ylim([0, min([crop_elm_since, ax.get_ylim()[1]])])
        if standalone:
            self._generic_plot_annotations(ax=ax)
        return

    def plot_raw_sawtooth_info(self, ax=None, wt=None, standalone=True, shade_elms=True):
        """
        Plots raw sawtooth signal (not -dTe/dt). Only makes sense in sawtooth mode.

        :param ax: Axes instance
        :param wt: array of bools
            Mask for time range to plot
        :param standalone: bool
        :param shade_elms: bool
        """
        dets = self['elm_detection_details']  # Shortcut
        ax = pyplot.gca() if ax is None else ax
        if wt is None:
            time_range, wt = self._get_time_mask()
        ax.set_title('Raw signal')
        ax.plot(self['dalpha_time'][wt], self['raw_sawtooth_input'][wt], label='$T_e$ from {}'.format(self._generate_filterscope_label()))
        yy = copy.copy(self['raw_sawtooth_input'])
        not_elm = ~dets['elm_flag'].astype(bool)
        # elm = dets['elm_flag']  # If you needed a flag for when an ELM is happening
        yy[not_elm] = np.NaN
        xx = copy.copy(self['dalpha_time'])
        xx[not_elm] = np.NaN
        if shade_elms:
            ax.plot(xx[wt], yy[wt], 'r')
            ax.fill_between(xx[wt], yy[wt] * 0, yy[wt], color='r', alpha=0.25, label='Sawteeth')
        else:
            ax.plot(xx[wt], yy[wt], 'r', label='Sawteeth')
        if standalone:
            self._generic_plot_annotations(ax=ax)
        return

    def plot_hold_correction(self, ax=None, wt=None, time_range=None, standalone=True, shade_elms=True):
        """
        Plot explanation of the hold correction to the ELM flag
        Only works if detection was done with debug = True
        :param ax: Axes instance
        :param wt: array of bools
            time mask
        :param time_range: two element numeric iterable
        :param standalone: bool
        :param shade_elms: bool
        """
        ax = pyplot.gca() if ax is None else ax
        if (wt is None) or (time_range is None):
            time_range, wt = self._get_time_mask()
        if standalone:
            self._generic_plot_annotations(ax=ax)

        t = self['dalpha_time']
        y = self['dalpha_y']

        min_window = self['settings']['detection']['hold_elm_min_finding_time_window']
        starts = self['detect_debugging']['starts']
        ends = self['detect_debugging']['ends']
        localmins = self['detect_debugging']['elm_det_localmins']
        localmax = self['detect_debugging']['elm_det_localmaxs']
        thresh = self['detect_debugging']['elm_det_threshs']
        new_ends = self['detect_debugging']['elm_det_adv_hold_until']

        ax.plot(t[wt], y[wt], label='$y$')
        needlab = True
        for i in range(len(starts)):
            # Mark up individual ELMs
            x = [t[starts[i]], t[new_ends[i]]]
            if ((np.max(x) >= time_range[0]) and (np.max(x) <= time_range[1])) or (
                (np.min(x) >= time_range[0]) and (np.min(x) <= time_range[1])
            ):
                # Only mark ELMs that are within the time window

                xx = t[ends[i] : new_ends[i] + 1]
                yy = y[ends[i] : new_ends[i] + 1]
                label = 'Hold' if needlab else ''
                if shade_elms:
                    ax.plot(xx, yy, 'r')
                    ax.fill_between(xx, yy * 0, yy, color='r', alpha=0.25, label=label)
                else:
                    ax.plot(xx, yy, 'r', label=label)
                    ax.axvline(t[starts[i]], color='r', linestyle=':', label='Start' if needlab else '')
                    ax.axvline(t[ends[i]], color='r', linestyle='-.', label='Original end' if needlab else '')
                    ax.axvline(t[new_ends[i]], color='r', linestyle='--', label='New end' if needlab else '')

                xmn = [t[starts[i]] - min_window, t[new_ends[i]]]
                ax.plot(x, [localmax[i]] * 2, color='k', label='$max_{local}(y)$ level' if needlab else '', linestyle='--')
                ax.plot(xmn, [localmins[starts[i]]] * 2, color='g', linestyle='-.', label='$min_{local}(y)$ level' if needlab else '')
                ax.plot(x, [thresh[i]] * 2, color='m', label='Local hold-release threshold' if needlab else '')
                needlab = False
        return

    @staticmethod
    def _prepare_fig_axs(fig=None, axs=None, nplot=1, figsize=None, legend_outside=False):
        """
        Creates figure and axes as needed to accommodate a given number of plots
        :param fig: [optional] figure instance
        :param axs: [optional] axes instance
        :param nplot: int
        :param figsize: two element numeric iterable giving the figure size
        :param legend_outside: bool
        :return: fig, axes to use for plotting, all axes (including blanks to reserve space for a legend)
        """
        if fig is not None and axs is not None:
            f, ax0 = fig, axs
        elif fig is not None and axs is None:
            f = fig
            nax = nplot * (1 + int(legend_outside))
            ax0 = [None] * nax
            ax0[0] = fig.add_subplot(nplot, 1 + int(legend_outside), 1)
            for i in range(1, nax):
                ax0[i] = fig.add_subplot(nplot, 1 + int(legend_outside), i + 1, sharex=ax0[0])
            ax0 = np.squeeze(np.atleast_1d(ax0).reshape((nplot, 1 + int(legend_outside))))
        else:
            f, ax0 = pyplot.subplots(nplot, 1 + int(legend_outside), sharex='all', figsize=figsize)
        ax0 = np.atleast_1d(ax0)
        if legend_outside:
            ax = ax0[:, 0]
            for i in range(nplot):
                ax0[i, 1].axis('off')
        else:
            ax = ax0
        return f, ax, ax0

    def jump_and_hold_elm_detection_plot(
        self,
        time_zoom=None,
        crop_data_to_zoom_range=True,
        crop_elm_since=True,
        show_phase=True,
        show_more_timing=True,
        show_details=True,
        hide_y=False,
        hide_numbers=False,
        legend_outside=False,
        notitles=False,
        shade_elms=True,
        figsize=None,
        fig=None,
        axs=None,
    ):
        """
        Plots important variables related to jump & hold ELM detection

        This both demonstrates how the ELM detector works and serves as a diagnostic plot that can help with tuning.

        :param time_zoom: two element iterable containing numbers
            Zoom in to this time range in ms
            If None, auto selects the default for the current device

        :param crop_data_to_zoom_range: bool
            Crop data to range given by time_zoom before calling plot. This can prevent resampling, which will make the
            plot better.

        :param crop_elm_since: float or bool
            float = plot max in ms. True = auto-scale sensibly. False = auto-scale stupidly.

        :param show_phase: bool
            Plot ELM phase in an additional subplot. Phase is 0 at the end of an ELM, then increases during the
            inter-ELM period until it reaches +1 at the start of the next ELM.
            Then it jumps to -1 and increases back to 0 during the ELM.

        :param show_more_timing: bool
            Include an additional subplot showing more timing details like time since last ELM & local ELM period length

        :param show_details: bool
            Shows details of how ELM detection works (individual terms like DS, DD, etc.) in a set of add'l subplots.

        :param hide_y: bool
            Turns off numbers on the y-axis and in some legend entries. Useful if you want to consider D_alpha to be in
            arbitrary units and don't want to be distracted by numbers.

        :param hide_numbers: bool
            Hides numerical values of smoothing time scales and other settings used in ELM detection.
            Useful if you want shorter legend entries or a simpler looking plot.

        :param legend_outside: bool
            Place the legends outside of the plots; useful if you have the plots positioned so there is empty space to
            the right of them.

        :param notitles: bool
            Suppress titles on the subplots.

        :param shade_elms: bool
            On the ELM ID plot, shade between 0 and D_alpha

        :param figsize: Two element iterable containing numbers
            (X, Y) Figure size in cm

        :param fig: Figure instance
            Used for overlay

        :param axs: List of Axes instances
            Used for overlay. Must be at least long enough to accommodate the number of plots ordered.

        :return: (Figure instance, array of Axes instances)
        """
        from matplotlib import pyplot

        printd('Running J&H ELM detection demo plot (shot {:})...'.format(self.shot), topic='omfit_elm')

        if 'elm_detection_details' not in self:
            self.detect()

        elmdet = self['settings']['detection']['{:}_tuning'.format(self['settings']['detection']['smoother'])]
        printd('mild_smooth = {}'.format(elmdet['mild_smooth']), topic='omfit_elm')

        show_hold = self.debug * self['settings']['detection']['hold_elm_flag_until_low_dalpha']
        nplot = (3 + show_hold) * show_details + 1 + show_phase + show_more_timing + int(self.mode == 'sawtooth')

        f, ax, ax0 = self._prepare_fig_axs(fig=fig, axs=axs, nplot=nplot, figsize=figsize, legend_outside=legend_outside == 1)

        time_range, wt = self._get_time_mask(crop_data_to_zoom_range=crop_data_to_zoom_range, time_zoom=time_zoom)
        ax[0].set_xlim(time_range)

        def draw_legend(axx, ii):
            if legend_outside == 2:
                axx[ii].legend(loc='center left', bbox_to_anchor=(1, 0.5)).set_draggable(True)
            elif legend_outside:
                axx[ii, 0].legend(loc='center left', bbox_to_anchor=(1, 0.5)).set_draggable(True)
            else:
                axx[ii].legend(loc=0).set_draggable(True)
            return

        # List of plots that draw their own legends so they shouldn't get legend calls at the end when all the normal
        # legends would be drawn
        skip_legends = []

        filterscope_label = self._generate_filterscope_label()
        tn, en, cen = self.get_quantity_names()

        plotnum = 0
        # Possible zeroth plot: sawtooth raw input
        if self.mode == 'sawtooth':
            self.plot_raw_sawtooth_info(ax=ax[plotnum], wt=wt, standalone=False, shade_elms=shade_elms)
            plotnum += 1

        if show_details:
            # First plot: D_alpha, smoothed D_alpha, and localmax
            nwin = self['elm_detection_details']['n_win']

            def rollit(a, n):
                return np.roll(np.concatenate((np.repeat(0, n), a, np.repeat(0, n))), n)[n:-n]

            t = self['dalpha_time'][wt]
            y = self['dalpha_y'][wt]
            ax[plotnum].plot(t, y, label='$y = {}$ (from {:})'.format(tn, filterscope_label))
            ys = rollit(self['elm_detection_details']['ys'], nwin)[wt]
            localmax = rollit(self['elm_detection_details']['localmax'], nwin)[wt]
            ys_label = '$y_s = delay(smooth(y))$'
            threshold_label = 'Threshold'
            threshold = self['settings']['detection']['find_jump_threshold']
            if not hide_numbers:
                ys_label += r', $\tau = {:0.2f}, L = {:0.2f}$ ms'.format(
                    float(self['settings']['detection']['find_jump_presmo']), self['settings']['detection']['find_jump_time_window']
                )
                threshold_label += ' = {:0.2f}'.format(threshold)
            ax[plotnum].plot(t, ys, label=ys_label)
            ax[plotnum].plot(t, localmax, label='$max_{local}(smooth(y))$')
            plotnum += 1

            dy = self['elm_detection_details']['dy'][wt]
            ax[plotnum].plot(t, dy, label='$dy = max_{local}(y_s) - y_s$')
            plotnum += 1

            ndy = self['elm_detection_details']['ndy'][wt]
            ax[plotnum].plot(t, ndy, label='Normalized $dy$')
            ax[plotnum].axhline(threshold, color='m', label=threshold_label)

            yy = copy.copy(ndy)
            yy[ndy < threshold] = np.NaN

            olabel = 'Jump detected'
            if shade_elms:
                ax[plotnum].plot(t, yy, 'r')
                ax[plotnum].fill_between(t, yy * 0, yy, color='r', alpha=0.25, label=olabel)
            else:
                ax[plotnum].plot(t, yy, 'r', label=olabel)

            plotnum += 1

            if self.debug:
                # Only works if debug data are saved
                self.plot_hold_correction(ax=ax[plotnum], wt=wt, time_range=time_range, standalone=False, shade_elms=shade_elms)
                plotnum += 1
            # Next...

        # D_alpha with ELM identification (or -d/dt(T_e) with sawtooth ID)
        self.plot_signal_with_event_id(ax=ax[plotnum], wt=wt, shade_elms=shade_elms, standalone=False)

        if show_phase:
            # ELM phase
            plotnum += 1
            self.plot_phase(ax=ax[plotnum], standalone=False)

        if show_more_timing:
            # Misc. ELM timing info
            plotnum += 1
            self.plot_more_event_timing_info(ax=ax[plotnum], crop_elm_since=crop_elm_since, standalone=False)

        for i in range(nplot):
            if i not in skip_legends:
                draw_legend(ax0, i)

            if notitles:
                ax[i].set_title('')
            if hide_y:
                ax[i].get_yaxis().set_ticks([0])

        self._generic_plot_annotations(f, ax[-1])

        printd('Done with elm det demo {:}'.format(self.shot), topic='omfit_elm')
        return f, ax0

    def classic_elm_detection_plot(
        self,
        time_zoom=None,
        crop_data_to_zoom_range=True,
        crop_elm_since=True,
        show_phase=True,
        show_more_timing=True,
        show_details=True,
        hide_y=False,
        hide_numbers=False,
        legend_outside=False,
        notitles=False,
        shade_elms=True,
        figsize=None,
        fig=None,
        axs=None,
    ):
        """
        Plots important variables related to classic ELM detection

        This both demonstrates how the ELM detector works and serves as a diagnostic plot that can help with tuning.

        :param time_zoom: two element iterable containing numbers
            Zoom in to this time range in ms
            If None, auto selects the default for the current device

        :param crop_data_to_zoom_range: bool
            Crop data to range given by time_zoom before calling plot. This can prevent resampling, which will make the
            plot better.

        :param crop_elm_since: float or bool
            float = plot max in ms. True = auto-scale sensibly. False = auto-scale stupidly.

        :param show_phase: bool
            Plot ELM phase in an additional subplot. Phase is 0 at the end of an ELM, then increases during the
            inter-ELM period until it reaches +1 at the start of the next ELM.
            Then it jumps to -1 and increases back to 0 during the ELM.

        :param show_more_timing: bool
            Include an additional subplot showing more timing details like time since last ELM & local ELM period length

        :param show_details: bool
            Shows details of how ELM detection works (individual terms like DS, DD, etc.) in a set of add'l subplots.

        :param hide_y: bool
            Turns off numbers on the y-axis and in some legend entries. Useful if you want to consider D_alpha to be in
            arbitrary units and don't want to be distracted by numbers.

        :param hide_numbers: bool
            Hides numerical values of smoothing time scales and other settings used in ELM detection.
            Useful if you want shorter legend entries or a simpler looking plot.

        :param legend_outside: bool
            Place the legends outside of the plots; useful if you have the plots positioned so there is empty space to
            the right of them.

        :param notitles: bool
            Suppress titles on the subplots.

        :param shade_elms: bool
            On the ELM ID plot, shade between 0 and D_alpha

        :param figsize: Two element iterable containing numbers
            (X, Y) Figure size in cm

        :param fig: Figure instance
            Used for overlay

        :param axs: List of Axes instances
            Used for overlay. Must be at least long enough to accommodate the number of plots ordered.

        :return: (Figure instance, array of Axes instances)
        """
        from matplotlib import pyplot

        printd('Running classic ELM detection demo plot (shot {:})...'.format(self.shot), topic='omfit_elm')

        if 'elm_detection_details' not in self:
            self.detect()

        elmdet = self['settings']['detection']['{:}_tuning'.format(self['settings']['detection']['smoother'])]
        dets = self['elm_detection_details']
        printd('mild_smooth = {}'.format(elmdet['mild_smooth']), topic='omfit_elm')

        if self['settings']['detection']['detection_method'] != 0 and show_details:
            print('"show_details" is currently incompatible with selected ELM detection method and has been disabled')
            show_details = False

        show_hold = self.debug * self['settings']['detection']['hold_elm_flag_until_low_dalpha']
        nplot = (4 + show_hold) * show_details + 1 + show_phase + show_more_timing + int(self.mode == 'sawtooth')

        f, ax, ax0 = self._prepare_fig_axs(fig=fig, axs=axs, nplot=nplot, figsize=figsize, legend_outside=legend_outside == 1)

        time_range, wt = self._get_time_mask(crop_data_to_zoom_range=crop_data_to_zoom_range, time_zoom=time_zoom)
        ax[0].set_xlim(time_range)

        def draw_legend(axx, ii):
            if legend_outside == 2:
                axx[ii].legend(loc='center left', bbox_to_anchor=(1, 0.5)).set_draggable(True)
            elif legend_outside:
                axx[ii, 0].legend(loc='center left', bbox_to_anchor=(1, 0.5)).set_draggable(True)
            else:
                axx[ii].legend(loc=0).set_draggable(True)
            return

        # List of plots that draw their own legends so they shouldn't get legend calls at the end when all the normal
        # legends would be drawn
        skip_legends = []

        filterscope_label = self._generate_filterscope_label()
        tn, en, cen = self.get_quantity_names()

        plotnum = 0
        # Possible zeroth plot: sawtooth raw input
        if self.mode == 'sawtooth':
            self.plot_raw_sawtooth_info(ax=ax[plotnum], wt=wt, standalone=False)
            plotnum += 1

        if show_details:
            # First plot: D_alpha and smoothed D_alpha
            ax[plotnum].set_title('Signal and smoothed signal')
            ax[plotnum].plot(self['dalpha_time'][wt], self['dalpha_y'][wt], label='$y = {}$ (from {:})'.format(tn, filterscope_label))
            if hide_numbers:
                tmplabel1 = '$S1 = $MildSmooth(y)'
                tmplabel2 = '$S2 = $AggressiveSmooth(y)'
            else:
                tmplabel1 = r'$S1 = $MildSmooth(y), $\tau={:}$ ms'.format(elmdet['mild_smooth'])
                tmplabel2 = r'$S2 = $AggressiveSmooth(y), $\tau={:}$ ms'.format(elmdet['mild_smooth'] * elmdet['heavy_smooth_factor'])
            ax[plotnum].plot(self['dalpha_time'][wt], dets['s1'][wt], label=tmplabel1)
            ax[plotnum].plot(self['dalpha_time'][wt], dets['s2'][wt], label=tmplabel2)
            plotnum += 1

            # Difference of smoothed D_alpha vs. threshold
            ax[plotnum].set_title('Difference of smooths & threshold; red = identified as {} by this test'.format(en))
            ax[plotnum].plot(self['dalpha_time'][wt], dets['ds'][wt], label='$DS = S1-S2$')
            if hide_y:
                tmplabel = r'Threshold$ = {:0.2f} \times $max(DS)'.format(elmdet['threshold_on_difference_of_smooths'])
            else:
                tmplabel = r'Threshold$ = {:+0.4f} = {:+0.4f} =\times $max(DS)'.format(
                    dets['thresh1'], elmdet['threshold_on_difference_of_smooths']
                )
            if hide_numbers:
                tmplabel = 'Threshold'
            ax[plotnum].axhline(dets['thresh1'], color='k', linestyle='--', label=tmplabel)
            dyt = dets['dyt']
            y1 = dets['ds'] + 0
            x1 = self['dalpha_time'] + 0
            y1[np.where(dyt <= 0)] = None
            x1[np.where(dyt <= 0)] = None
            ax[plotnum].plot(x1[wt], y1[wt], 'r', label=cen)
            ax[plotnum].axhline(0, color='k', linestyle=':', label='Zero')
            plotnum += 1

            # Derivative of D_alpha and smoothed derivative
            ax[plotnum].set_title('Derivative of smooth & more smoothed derivative')
            if elmdet['mild_smooth_derivative_factor'] > 0:
                if hide_numbers:
                    tmplabel1 = '$D1 = $MildSmooth$($Deriv$(S1))$'
                else:
                    tmplabel1 = r'$D1 = $MildSmooth$($Deriv$(S1))$, $\tau={:}$ ms'.format(
                        elmdet['mild_smooth'] * elmdet['mild_smooth_derivative_factor']
                    )
            else:
                tmplabel1 = '$D1 = $Deriv$(S1)$'
            if hide_numbers:
                tmplabel2 = '$D2 = $AggressiveSmooth$(D1)$'
            else:
                tmplabel2 = r'$D2 = $AggressiveSmooth$(D1)$, $\tau={:}$ ms'.format(
                    elmdet['mild_smooth'] * elmdet['heavy_smooth_derivative_factor']
                )
            ax[plotnum].plot(self['dalpha_time'][wt], dets['d1'][wt], label=tmplabel1)
            ax[plotnum].plot(self['dalpha_time'][wt], dets['d2'][wt], label=tmplabel2)
            ax[plotnum].axhline(0, color='k', linestyle=':')
            plotnum += 1

            # Difference of smoothed derivatives and threshold
            ax[plotnum].set_title('Difference of derivatives & thresholds; red = identified as {} by this test'.format(en))
            ax[plotnum].plot(self['dalpha_time'][wt], dets['dd'][wt], label='$DD = D1-D2$')
            if hide_y:
                if elmdet['d_thresh_enhance_factor'] == 1:
                    tmplabel1 = r'Threshold$ = {:0.2f} \times $max(DD)'.format(
                        elmdet['threshold_on_difference_of_smoothed_derivatives_plus']
                    )
                else:
                    tmplabel1 = r'Threshold$ = {:0.2f}$ or ${:0.2f} \times $max(DD)'.format(
                        elmdet['threshold_on_difference_of_smoothed_derivatives_plus'],
                        elmdet['threshold_on_difference_of_smoothed_derivatives_plus'] * elmdet['d_thresh_enhance_factor'],
                    )
                tmplabel2 = r'Threshold$ = {:0.2f} \times $min(DD)'.format(elmdet['threshold_on_difference_of_smoothed_derivatives_minus'])
            else:
                if elmdet['d_thresh_enhance_factor'] == 1:
                    tmplabel1 = r'Threshold$ = {:+0.4f} = {:+0.4f} \times $max(DD)'.format(
                        np.mean(dets['thresh2']), elmdet['threshold_on_difference_of_smoothed_derivatives_plus']
                    )
                else:
                    tmplabel1 = r'Threshold$ = {:+0.4f}$ or ${:+0.4f} = {:+0.4f}$ or ${:+0.4f} \times $max(DD)'.format(
                        min(dets['thresh2']),
                        max(dets['thresh2']),
                        elmdet['threshold_on_difference_of_smoothed_derivatives_plus'],
                        elmdet['threshold_on_difference_of_smoothed_derivatives_plus'] * elmdet['d_thresh_enhance_factor'],
                    )
                if elmdet['neg_d_thresh_enhance_factor'] == 1:
                    tmplabel2 = r'Threshold$ = {:+0.4f} = {:+0.4f} \times $min(DD)'.format(
                        np.mean(dets['thresh3']), elmdet['threshold_on_difference_of_smoothed_derivatives_minus']
                    )
                else:
                    tmplabel2 = r'Threshold$ = {:+0.4f}$ or ${:+0.4f} = {:+0.4f}$ or ${:+0.4f} \times $min(DD)'.format(
                        min(dets['thresh3']),
                        max(dets['thresh3']),
                        elmdet['threshold_on_difference_of_smoothed_derivatives_minus'],
                        elmdet['threshold_on_difference_of_smoothed_derivatives_minus'] * elmdet['neg_d_thresh_enhance_factor'],
                    )
            if hide_numbers:
                tmplabel1 = 'Threshold'
                tmplabel2 = None
            if elmdet['d_thresh_enhance_factor'] == 1:
                ax[plotnum].axhline(np.mean(dets['thresh2']), color='k', linestyle='--', label=tmplabel1)
            else:
                ax[plotnum].plot(self['dalpha_time'][wt], dets['thresh2'][wt], color='k', linestyle='--', label=tmplabel1)
            if elmdet['neg_d_thresh_enhance_factor'] == 1:
                ax[plotnum].axhline(np.mean(dets['thresh3']), color='k', linestyle='--', label=tmplabel2)
            else:
                ax[plotnum].plot(self['dalpha_time'][wt], dets['thresh3'][wt], color='k', linestyle='--', label=tmplabel2)
            ax[plotnum].axhline(0, color='k', linestyle=':')
            dd2 = dets['dd2']
            dd3 = dets['dd3']
            x2 = self['dalpha_time'] + 0
            y2 = dets['dd'] + 0
            x2[(dd2 <= 0) * (dd3 <= 0)] = None
            y2[(dd2 <= 0) * (dd3 <= 0)] = None
            ax[plotnum].plot(x2[wt], y2[wt], 'r', label=cen)
            plotnum += 1

            if show_hold:
                self.plot_hold_correction(ax=ax[plotnum], wt=wt, time_range=time_range, standalone=False, shade_elms=shade_elms)
                plotnum += 1
            # Next...

        # D_alpha with ELM identification (or -d/dt(T_e) with sawtooth ID)
        self.plot_signal_with_event_id(ax=ax[plotnum], wt=wt, shade_elms=shade_elms, standalone=False)

        if show_phase:
            # ELM phase
            plotnum += 1
            self.plot_phase(ax=ax[plotnum], standalone=False)

        if show_more_timing:
            # Misc. ELM timing info
            plotnum += 1
            self.plot_more_event_timing_info(ax=ax[plotnum], crop_elm_since=crop_elm_since, standalone=False)

        for i in range(nplot):
            if i not in skip_legends:
                draw_legend(ax0, i)

            if notitles:
                ax[i].set_title('')
            if hide_y:
                ax[i].get_yaxis().set_ticks([0])

        self._generic_plot_annotations(f, ax[-1])

        printd('Done with elm det demo {:}'.format(self.shot), topic='omfit_elm')
        return f, ax0


############################################
if __name__ == '__main__':
    test_classes_main_header()

    # Default functionality: Just test OMFITelm.__init__()
    # To run the unit tests, provide a number > 0 or the word test as a command line argument while calling
    if len(sys.argv) > 1:
        try:
            test_flag = int(sys.argv[1])
        except ValueError:
            test_flag = int(sys.argv[1] == 'test')
    else:
        test_flag = 0

    if test_flag > 0:
        sys.argv.pop(1)
        manage_tests(TestOMFITelm, failfast=False)
    else:
        OMFITelm(shot=154754)  # Test init, but don't try to use shot 0 as it will try to connect to d3drdb
