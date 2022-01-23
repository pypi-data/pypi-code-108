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

from omfit_classes.omfit_error import OMFITerror
from omfit_classes.omfit_elm import OMFITelm
from omfit_classes.utils_base import printd, tolist
from omfit_classes.utils_fusion import is_device, tokamak, lambda_debye
from omfit_classes.utils_math import closestIndex
from omfit_classes.omfit_mds import OMFITmdsValue
from omfit_classes.omfit_rdb import OMFITrdb
from omfit_classes.omfit_eqdsk import read_basic_eq_from_mds

import numpy as np
from numpy.core import shape
from scipy.interpolate import interp1d
from scipy import constants
import unittest
from uncertainties.unumpy import uarray, std_devs, nominal_values

try:
    import MDSplus
except Exception:  # MDSplus raises Exception, so this can't be more narrow
    print('Error importing MDSplus in omfit_elm.py.')
    mds_available = False
else:
    mds_available = True

__all__ = []


def _available_to_user(f):
    __all__.append(f.__name__)
    return f


@_available_to_user
class OMFITthomson(SortedDict):
    """
    Helps with fetching data from the Thomson Scattering diagnostic.

    It also has some other handy features to support analysis based on Thomson data:

    - Filter data by fractional error (e.g. throw out anything with > 10% uncertainty)
    - Filter data by reduced chi squared (e.g. throw out anything with redchisq > 8)
    - Filter data using ELM timing (e.g. only accept data if they are sampled between 50 and 99% of their local
      inter-ELM period)
    """

    def __init__(
        self,
        device='DIII-D',
        shot=0,
        efitid='EFIT01',
        revision_num=-1,
        subsystems='auto_select',
        override_default_measurements=None,
        quality_filters='default',
        elm_filter=None,
        efit_data=None,
        allow_backup_efitid=False,
        debug=False,
        verbose=False,
    ):
        """
        :param device: Device name, like 'DIII-D'

        :param shot: Shot number to analyze.

        :param efitid: String describing the EFIT to use for mapping, such as 'EFIT01'.
            For DIII-D, 'EFIT03' and 'EFIT04' are recommended because they are calculated on the same time base as TS.S

        :param revision_num: A string specifying a revision like 'REVISION00' or just the number like 0.
            -1 Selects the "blessed" or "best" revision automatically.
            -2 selects the best revision the same as in -1, but also creates a folder with raw data from all revisions.

        :param subsystems: List of Thomson systems to do handle. For DIII-D, this can be any subset of
            ['core', 'divertor', 'tangential'].
            For other devices, this setting does nothing and the systems list will be forced to ['core'].
            Set this to 'auto_select' to pick a setting that's a good idea for your device.
            (Currently, all non-DIII-D devices are forced to ['core'].)

        :param override_default_measurements: list of strings [optional]
            Use this to do lightweight gathering of only a few quantities. More advanced uses, like filtering,
            require all of the default quantities.

        :param quality_filters: Set to 'default' or a dictionary structure specifying settings for quality filters.
            Missing settings will be set to default values (so an empty dictionary {} is a valid input here).
            Top level settings in quality_filters:

            - remove_bad_slices: Any time-slice which is all bad measurements or any chord which is all bad will be
              identified. These can be removed from the final dataset, which saves the user from carting around
              bad data.

            - set_bad_points_to_zero: Multiply data by the okay flag, which will set all points marked as bad to 0+/-0

            - ip_thresh_frac_of_max: Set a threshold on Ip so that slices with low Ip (such as at the start of the
              shot or during rampdown) will not pass the filter.

            In addition, there are filters specified on a subsystem-by-subsystem basis. In addition to the real
            subsystems, there is a 'global_override' subsystem, which takes precedence if its settings aren't None.

            - bad_chords: array or list of bad chord indices for this subsystem. Set to empty list if no bad channels.
              (Real subsystems only, no global override)

            - redchisq_limit: A number specifying the maximum acceptable reduced chi squared value. This refers to the
              fit to Thomson's raw pulsed and DC data signals to determine Te and ne.

            - frac_temp_err_hot_max: Upper limit on acceptable fractional uncertainty in Te when Te is above the
              hot_cold_boundary threshold.

            - frac_temp_err_cold_max: Upper limit on acceptable fractional uncertainty in Te when Te is below the
              hot_cold_boundary threshold.

            - hot_cold_boundary: Te boundary between "hot" and "cold" temperatures, which have different fractional
              uncertainty limits.

            - frac_dens_err_max: Maximum fractional uncertainty in ne measurements.

        :param elm_filter: Provide an instance of an ELM filtering class like OMFITelm or set to None to have
            OMFITthomson set this up automatically.

        :param efit_data: This is usually None, which instructs OMFITthomson to gather its own EFIT data to use in
            mapping. However, you can pass in a dictionary with contents matching the format returned by
            self.gather_efit_data() and then self.gather_efit_data() will be skipped.

        :param allow_backup_efitid: T/F: Allow self.gather_efit_data() to choose self.efitid if it fails to find data
            for the requested EFIT.

        :param debug: bool
            Debug mode saves some intermediate results in a special dictionary.

        :param verbose: bool
            Always print debugging statements. May be useful when using this class outside the framework.
        """
        # super().__init__()
        SortedDict.__init__(self)
        self.status = {'setup': False, 'gathered': False, 'mapped': False, 'filtered': False, 'calcs': False}
        self.verbose = verbose

        # Handle basic settings
        self.device = tokamak(device)
        self.supported_devices = ['DIII-D', 'NSTX', 'NSTXU']
        if shot is None:
            shot = 0
        if shot <= 0:
            shot += self.lookup_latest_shot()
        self.shot = shot
        self.efitid = efitid
        self.allow_backup_efitid = allow_backup_efitid
        self.revision_num = revision_num
        if subsystems == 'auto_select':
            self.subsystems = ['core', 'tangential'] if is_device(device, 'DIII-D') else ['core']
        else:
            self.subsystems = tolist(subsystems) if is_device(self.device, 'DIII-D') else ['core']
        if override_default_measurements is None:
            self.measurements = ['r', 'z', 'temp', 'temp_e', 'density', 'density_e', 'redchisq']
        else:
            printw(
                'WARNING! OMFITthomson needs all of the default measurements to optimally perform key functions '
                'like filtering. You should not change the measurements list unless you are doing lightweight raw '
                'data gathering only.'
            )
            self.measurements = override_default_measurements

        # Figure out the revision number. It should be a string. If the user supplied just a number, build a string
        # from that. If the number is -1, that indicates that the blessed revision should be used (-1 is not a valid
        # revision # in MDS)
        if isinstance(revision_num, str):
            # The user supplied a string
            self.revision = revision_num
            self.revision_num = re.findall(r'\d+', revision_num)[0]
        elif revision_num in [-1, -2]:
            # Special case: -1 means that the blessed/best revision should be used. For DIII-D, "BLESSED" is a
            # pointer to one of the numbered revisions that is controlled by the Thomson scattering group. The TS
            # group should've pointed blessed at the best revision.
            if is_device(self.device, 'DIII-D'):
                self.revision = 'blessed'
            elif is_device(self.device, ('NSTX', 'NSTX-U')):
                self.revision = 'best'
            else:
                raise IOError(
                    'Unrecognized server/device option: {}. Please choose an option from {}.'.format(self.device, self.supported_devices)
                )
        else:
            # The user supplied a number, so convert it into a proper string
            if is_device(self.device, 'DIII-D'):
                self.revision = 'REVISIONS.REVISION{:02d}'.format(revision_num)
            elif is_device(self.device, ('NSTX', 'NSTX-U')):
                self.revision = 'TS{:0d}'.format(revision_num)
            else:
                raise IOError(
                    'Unrecognized server/device option: {}. Please choose an option from {}.'.format(self.dvecice, self.supported_devices)
                )

        # Handle quality filters
        self.default_quality_filters = {
            'ip_thresh_frac_of_max': 0.2,
            'set_bad_points_to_zero': True,
            'remove_bad_slices': True,
            'global_override': {
                'redchisq_limit': None,
                'frac_temp_err_hot_max': None,
                'frac_temp_err_cold_max': None,
                'hot_cold_boundary': None,
                'frac_dens_err_max': None,
            },
            'core': {
                'redchisq_limit': 8.0,
                'bad_chords': np.array([40]),
                'frac_temp_err_hot_max': 0.5,
                'frac_temp_err_cold_max': 0.95,
                'hot_cold_boundary': 50.0,
                'frac_dens_err_max': 0.5,
            },
            'tangential': {
                'redchisq_limit': 8.0,
                'bad_chords': None,
                'frac_temp_err_hot_max': 0.5,
                'frac_temp_err_cold_max': 0.95,
                'hot_cold_boundary': 100.0,
                'frac_dens_err_max': 0.5,
            },
            'divertor': {
                'redchisq_limit': 8.0,
                'bad_chords': None,
                'frac_temp_err_hot_max': 0.5,
                'frac_temp_err_cold_max': 0.95,
                'hot_cold_boundary': 15.0,
                'frac_dens_err_max': 0.5,
            },
        }
        self.quality_filters = self.default_quality_filters
        if quality_filters == 'default':
            self.printdq('  Using default quality filters', )
        elif isinstance(quality_filters, dict):
            self.printdq('  Got dictionary of quality filters', )
            sub_keys = ['core', 'tangential', 'divertor', 'global_override']
            non_sub_keys = [k for k in list(self.default_quality_filters.keys()) if k not in sub_keys]
            for k in non_sub_keys:
                qf = quality_filters.get(k, None)
                if qf is None:
                    self.printdq('  {} not found in quality filter spec. Using default value for {}'.format(k, k), )
                    qf = self.default_quality_filters[k]
                else:
                    self.printdq('  {} found in quality filters specified in input!'.format(k), )
                self.quality_filters[k] = qf
            for sk in sub_keys:
                if sk in quality_filters:
                    self.printdq('  Input quality filter spec has data for {} subsystem, updating values...'.format(sk), )
                    keys = list(qualit_filters[sk].keys())
                    for k in keys:
                        qf = quality_filters[sk].get(k, None)
                        if qf is None:
                            self.printdq(
                                '    {} not found in quality filter spec for {} subsystem. '
                                'Using default value for {}/{}'.format(k, sk, sk, k),
                            )
                            qf = self.default_quality_filters[sk][k]
                        else:
                            self.printdq('    {}/{} found in quality filters specified in input!'.format(sk, k), )
                        self.quality_filters[sk][k] = qf
        else:
            printw('  Did not understand what to do with quality filter specification. Using defaults instead.')

        # Handle ELM filter
        self.elm_filter = False  # This would be an instance of the ELM filtering module if it were in use.
        if elm_filter is None:
            self.elm_filter = OMFITelm(shot=shot, device=device)
        elif elm_filter in ['disabled', 'off', 'no']:
            print('  ELM filter disabled')
        elif isinstance(elm_filter, OMFITelm):
            self.elm_filter = elm_filter
        else:
            print('  Unhandled ELM filter setup.')
            printw('  ELM filter disabled due to unhandled setup!')

        # Make labels
        global_redchisq = self.quality_filters['global_override']['redchisq_limit']
        if global_redchisq is None:
            global_redchisq = 0.0
        try:
            elm_phase = elm_filter['elm_phase_range']
            elm_reject = elm_filter['elm_since_reject_below']
            elm_since = elm_filter['elm_since_accept_above']
            elm_smoother = elm_filter['smoother']
        except (KeyError, NameError, TypeError):
            # KeyError if one of the tags is missing, NameError if a dependency isn't defined,
            # and TypeError if one of the intermediate tags can't be indexed by a string.
            elm_phase = [0, 0]
            elm_reject = 0
            elm_since = 0
            elm_smoother = 'x'

        self.short_label = ''.join(['{device:}_{shot:06d}_rev{revision:}']).format(
            device=device, shot=shot, revision=int(self.revision_num)
        )

        self.label = ''.join(
            [
                '{shot:06d}_rev{revision:}_rchsq-g{global_redchisq:05.1f}'
                'c{core_redchisq:05.1f}d{div_redchisq:05.1f}t{tan_redchisq:05.1f}_{efitid:}_',
                'elm-ph{elm_phase_min:04.2f}:{elm_phase_max:04.2f}',
                'r{elm_reject:04.1f}s{elm_since:05.1f}{elm_smoother:1s}',
            ]
        ).format(
            shot=shot,
            global_redchisq=global_redchisq,
            core_redchisq=self.quality_filters['core']['redchisq_limit'],
            div_redchisq=self.quality_filters['divertor']['redchisq_limit'],
            tan_redchisq=self.quality_filters['tangential']['redchisq_limit'],
            efitid=efitid,
            elm_phase_min=elm_phase[0],
            elm_phase_max=elm_phase[1],
            elm_reject=elm_reject,
            elm_since=elm_since,
            elm_smoother=elm_smoother[0],
            revision=int(self.revision_num),
        )

        # Handle efit_data
        if efit_data is not None:
            self['efit_data'] = efit_data
            self.efit_data_provided = True
        else:
            self.efit_data_provided = False

        self.status['setup'] = True

        self.debug = debug
        if self.debug:
            self['debugging'] = SortedDict()

        # Setup details to support convenient plotting
        self.default_plot = 'contour_plot'
        self['plots'] = SortedDict()

        if not mds_available:
            printe('Unable to import MDSplus! OMFITthomson will not be able to gather any data!')

    def __call__(self, report=False):
        """
        Performs all primary operations: gather, map, filter, calculate derived quantities, and package dataset.

        After running, data will be loaded into the class.

        :param report: bool
            Print a status report when done
        """
        self.gather()
        self.gather_efit_info()
        self.map()
        self.filter()
        self.calculate_derived()
        if report:
            self.report_status()

    def printdq(self, *args):
        """Wrapper for controlling verbosity locally"""
        if self.verbose:
            tag_print(*args, tag='DEBUG')
        else:
            printd(*args, topic='omfit_ts')

    def __tree_repr__(self):
        """Provides the label that OMFIT should use while representing class instances in the tree."""
        if not mds_available:
            return 'Disabled: no MDSplus support', []
        subs = ''.join([subsys[0] for subsys in tolist(self.subsystems)])
        state = (
            'done (step 4/4)'
            if self.status['calcs']
            else 'filtered (step 3/4)'
            if self.status['filtered']
            else 'mapped (step 2/4)'
            if self.status['mapped']
            else 'gathered (step 1/4)'
            if self.status['gathered']
            else 'blank (step 0/4)'
        )
        label = '{device:}#{shot:}, [{status:}], map={efitid:}, subs={subs:}, rev={rev:}'.format(
            device=self.device, shot=self.shot, efitid=self.efitid, subs=subs, rev=self.revision, status=state
        )
        return label, []

    # Utilities
    def lookup_latest_shot(self):
        """Looks up the last shot. Works for DIII-D. Used automatically if shot <= 0, in which case the shot number is
        treated as relative to the last shot."""
        import psycopg2

        if is_device(self.device, 'DIII-D'):
            print('    Looking up latest DIII-D shot...')
            try:
                last_shot = OMFITrdb(
                    "SELECT shot FROM summaries WHERE shot = (SELECT MAX(shot) FROM summaries)",
                    db='d3drdb',
                    server='d3drdb',
                    by_column=True,
                )['shot'][0]
            except (psycopg2.ProgrammingError, KeyError):
                raise OMFITexception(
                    'OMFITthomson is Unable to connect to d3drdb for shot 0 lookup! ' 'Please try again with a real shot number!'
                )
        else:
            raise NotImplementedError(
                'OMFITthomson: Shot 0 lookup functionality is not implemented for device={}. '
                'Please choose a real shot number.'.format(self.device)
            )
        print('    last_shot = {}'.format(last_shot))
        return last_shot

    def report_status(self):
        """
        Prints out a report that can be read easily from the command line
        """
        print('OMFITthomson instance: status and contents:')
        print('  Settings for this instance:')
        print('     device = {}, shot = {}'.format(self.device, self.shot))
        print('     revision_num = {}, revision = {}'.format(self.revision_num, self.revision))
        print('     efitid = {}, subsystems = {}'.format(self.efitid, self.subsystems))
        print('     measurements = {}'.format(self.measurements))
        print('  Status = {}'.format(self.status))
        print('  Contents:')
        print('    self.keys() = {}'.format(list(self.keys())))
        for group in ['raw', 'processed', 'filtered']:
            if group in self:
                print("      self['{}'].keys() = {}".format(group, list(self[group].keys())))
                sub_keys_present = [k for k in list(self[group].keys()) if k in ['core', 'tangential', 'divertor']]
                k0 = sub_keys_present[0] if len(sub_keys_present) else list(self[group].keys())[0] if len(self[group]) else None
                if k0 is not None:
                    print("        self['{}']['{}'].keys() = {}".format(group, k0, list(self[group][k0].keys())))

    def find_all_revisions(self, verbose=True):
        """Looks up all extant revisions of DIII-D Thomson data for the current shot."""
        if verbose:
            print('\n-----')
            print('Looking up which Thomson scattering analysis revisions exist for {:}#{:}...'.format(self.device, self.shot))

        if not is_device(self.device, 'DIII-D'):
            raise NotImplementedError('OMFITthomson can only search all revisions for DIII-D so far.')
        rev_tree = OMFITmdsValue(self.device, treename='electrons', shot=self.shot, TDI=r'getnci("ts.revisions\***","FULLPATH")').data()

        self['all_revisions'] = []

        for r in rev_tree:
            tmp = r.split('TOP.TS.')[1].split('.')
            revision = '.'.join(tmp[0:2]).strip()
            if len(tmp) < 3:
                tmp = revision.split(':')
                if len(tmp) < 2:
                    self['all_revisions'] += [revision]

        if verbose:
            print('Found revisions:')
            for r in self['all_revisions']:
                print('    {:}'.format(r))
            print("Saved revision list as self['all_revisions']")

    def check_filtered_data(self):
        """
        Check that results are available and that they match shot and filter settings
        """

        if 'filtered' not in list(self.keys()):
            # This definitely isn't done if the key isn't even in self!
            self.status['filtered'] = False
            return False

        # Settings to check for consistency
        check_elm = ['elm_phase_range', 'elm_since_reject_below', 'elm_since_accept_above']
        check_ts = ['redchisq_limit', 'bad_chords', 'frac_temp_err_hot_max', 'frac_temp_err_cold_max', 'hot_cold_boundary']

        filter_settings_okay = True  # Everything is okay unless it isn't

        elm_settings = {}  # Not hooked up yet, sorry.

        print('  OMFITthomson: Checking filtered data...')
        # Check saved settings from the TS group vs. the settings namelist; they should match
        for i in check_elm:
            try:
                self.printdq('    elm check: {}'.format(i), )
                self.printdq('    saved: {}'.format(self['filtered']['settings'][i]), )
                self.printdq('    settings: {}'.format(elm_settings['ELM_filter'][i]), )
                if np.any(np.atleast_1d(self['filtered']['settings'][i] != elm_settings['ELM_filter'][i])):
                    filter_settings_okay = False
                    print(
                        'ELM filter settings do not match: saved {:} = {:} vs. tree settings {:} = {:}. Need to '
                        're-filter...'.format(i, self['filtered']['settings'][i] + 0, i, elm_settings['ELM_filter'][i] + 0)
                    )
            except KeyError:
                filter_settings_okay = False

        # Check saved settings from the ELM group vs. the settings namelist; they should match
        for subsys in self.subsystems:
            self.printdq('  OMFITthomson: Checking TS sys: {}'.format(subsys), )
            if subsys in self['filtered']:
                for i in check_ts:
                    try:
                        self.printdq('TS check: {}'.format(i), )
                        if i in self.quality_filters['global_override']:
                            set_tmp = self.quality_filters['global_override'][i]
                        else:
                            set_tmp = None
                        self.printdq('    {} = {}'.format(i, set_tmp), )
                        if set_tmp is None:
                            set_tmp = self.quality_filters[subsys][i]
                            self.printdq(
                                '    > {} = {}   (None as a global setting is code for use the subsys '
                                'specific setting)'.format(i, set_tmp),

                            )
                            self.printdq('       {}'.format(self['filtered'][subsys]['settings'][i]), )
                        if self['filtered'][subsys]['settings'][i] != set_tmp:
                            filter_settings_okay = False
                            print(
                                'TS quality filter settings do not match: saved {:} = {:} vs current tree setting {:}'
                                ' = {:}. Need to refilter...'.format(i, self['filtered'][subsys]['settings'][i], i, set_tmp)
                            )
                    except KeyError:
                        filter_settings_okay = False
                        print(
                            'Failed when checking {} filter settings for consistency in subsys {}. '
                            'Need to re-filter...'.format(i, subsys)
                        )
            else:
                self.printdq('    subsys {} not in filtered output', )

        self.status['filtered'] *= filter_settings_okay
        return filter_settings_okay

    def check_efit_info(self):
        """
        Checks for consistency of any currently loaded EFIT data

        :return: Flag indicating whether new EFIT data are needed (T) or not (F).
        """
        need_new_efit_data = False
        check_if_match = {'shot': [self.shot], 'efitID': [self.efitid, 'CAKE']}
        for check_name, check_values in list(check_if_match.items()):
            try:
                match = self['efit_data'][check_name] in check_values
            except KeyError:
                self.printdq('  KeyError when checking {}: need to gather new EFIT data'.format(check_name), )
                need_new_efit_data = True
            else:
                need_new_efit_data *= not match
                self.printdq('   {} matches = {};  need_new_efit = {}'.format(check_name, match, need_new_efit_data), )
        return need_new_efit_data

    def to_dataset(self):
        """
        Packs data into a list of xarray Dataset instances, one per subsystem

        :return: dictionary with one Dataset instance for each subsystem
        """
        from xarray import DataArray, Dataset

        data = {}
        for sub in self.subsystems:
            coords = dict(time=self['filtered'][sub]['time'], channel=self['filtered'][sub]['chord_index'])
            dims = ['channel', 'time']

            psi = DataArray(self['filtered'][sub]['psin_TS'], coords=coords, dims=dims, name='psi_N')
            r = DataArray(self['filtered'][sub]['r'], coords=dict(channel=self['filtered'][sub]['chord_index']), dims=['channel'], name='R')
            z = DataArray(self['filtered'][sub]['z'], coords=dict(channel=self['filtered'][sub]['chord_index']), dims=['channel'], name='Z')

            meas = []
            if 'temp' in self.measurements:
                meas += ['T_e']
            if 'density' in self.measurements:
                meas += ['n_e']
            d = Dataset(dict(psi=psi, r=r, z=z), coords=coords, attrs=dict(measurements=meas))

            params = [par for par in self.measurements if par in ['temp', 'density', 'redchisq']]
            try:
                _ = self['filtered'][sub]['press']
            except KeyError:
                pass
            else:
                params += ['press']

            for param in params:
                y = self['filtered'][sub][param]
                if param + '_e' in self['filtered'][sub]:
                    y = uarray(y, self['filtered'][sub][param + '_e'])
                d[param] = DataArray(y, coords=coords, dims=dims, name=param)

            data[sub] = d

        return data

    # Primary class methods
    def gather(self, verbose=True):
        """
        Gathers Thomson scattering data from MDSplus
        """

        print('  OMFITthomson: gathering data...')

        self['raw'] = SortedDict()

        treename = {'DIII-D': 'ELECTRONS', 'NSTX': 'ACTIVESPEC', 'NSTXU': 'ACTIVESPEC'}.get(tokamak(self.device), None)  # MDS tree name

        if verbose:
            print('Fetching TS data')

        measurement_translations = {
            'NSTX': {'temp': 'fit_te', 'temp_e': 'fit_te_err', 'density': 'fit_ne', 'density_e': 'fit_ne_err', 'r': 'fit_radii'}
        }
        unit_conversion_factors = {  # Accessed w/ .get(server, {}).get(meas, 1), so don't define things w/ ucf = 1
            'NSTX': {
                'temp': 1000.0,  # keV to eV
                'temp_e': 1000.0,  # keV to eV
                'density': 1e6,  # cm^-3 to m^-3
                'density_e': 1e6,  # cm^-3 to m^-3
                'r': 0.01,  # cm to m
                'time': 1000.0,  # s to ms
            }
        }
        measurement_translations['NSTXU'] = measurement_translations['NSTX']
        unit_conversion_factors['NSTXU'] = unit_conversion_factors['NSTX']

        if verbose:
            print('Retrieving Thomson data for {} shot {:}'.format(self.device, self.shot))
            print('Revision: {:}'.format(self.revision))

        if self.revision_num == -2 and is_device(self.device, 'DIII-D'):
            # Handle the case where the user wants all the revisions
            self.find_all_revisions(verbose=False)
            revisions = [self.revision] + self['all_revisions']
        elif self.revision_num == -2 and is_device(self.device, ('NSTX','NSTX-U')):
            printw('All-revision gathering capability not implemented for NSTX/NSTX-U yet')
            revisions = [self.revision]
        else:
            revisions = [self.revision]

        # Loop through revisions
        for r, revision in enumerate(revisions):
            # Direct output so that the blessed revision goes to the main raw_TS tree and the other revs go to sub-trees
            if r == 0:
                out = self['raw']
            else:
                if is_device(self.device, 'DIII-D'):
                    rev = revision.split('.')[1]  # Take REVISIONS. out of REVISIONS.REVISION00 so it's just REVISION00.
                elif is_device(self.device, ('NSTX','NSTX-U')):
                    rev = revision
                else:
                    raise IOError('Unrecognized server/device option: {}. ' 'How did you even get this far?'.format(server))
                out = self['raw'][rev] = SortedDict()  # Make a shortcut to revision subtree

            if is_device(self.device, 'DIII-D'):
                # Handle DIII-D version, which has subsystems.

                # Loop through TS subsystems
                for subsys in self.subsystems:
                    # Build the base of the call so we can add just the measurement to the end of it later
                    basecall = '.ts.{:}.{:}.'.format(revision, subsys)
                    self.printdq('  sys = {}, basecall = {}'.format(subsys, basecall), )

                    out[subsys] = SortedDict()  # Make sure the output location exists

                    # Loop through quantities to gather
                    for meas in self.measurements:
                        call = basecall + meas
                        data = OMFITmdsValue(server=self.device, treename=treename, shot=self.shot, TDI=call)
                        out[subsys][meas] = data.data()

                        if (meas in ['temp', 'temp_e', 'density', 'density_e', 'redchisq']) and ('time' not in out[subsys]):
                            # These signals better have the same time dimension, or else something is very wrong.
                            # We don't even have to bother covering for a case where the time dimensions within a TS
                            # subsystem don't match because the case is probably un-salvageable and horribly corrupted.
                            out[subsys]['time'] = data.dim_of(0)

            elif is_device(self.device, ('NSTX','NSTX-U')):
                # Handle NSTX/U version, which does not have subsystems.
                basecall = '.mpts.output_data.{:}.'.format(revision)
                self.printdq('  basecall = {}'.format(basecall), )
                subsys = tolist(self.subsystems)[0]
                print(
                    'NSTX/NSTX-U do not have sub-systems like at DIII-D, so we will pretend that all data are from '
                    'the first subsystem in the list, which is {}'.format(subsys)
                )
                out[subsys] = SortedDict()  # Make sure the output location exists
                data = None

                self.printdq('  Starting loop through measurements: {}'.format(measurements), )
                for meas_ in measurements:
                    meas = measurement_translations.get(server, {}).get(meas_, None)
                    ucf = unit_conversion_factors.get(server, {}).get(meas_, 1)
                    if meas is not None:
                        call = basecall + meas
                        self.printdq(
                            '   call = {}, shot = {}, server = {}, treename = {}'.format(call, self.shot, self.device, treename),

                        )
                        data = OMFITmdsValue(server=self.device, treename=treename, shot=self.shot, TDI=call)
                        out[subsys][meas_] = data.data() * ucf

                    # These signals better have the same time dimension, or else something is very wrong. We don't
                    # even have to bother covering for a case where the time dimensions don't match because the case
                    # is probably un-salvageable and horribly corrupted.
                    ucf = unit_conversion_factors.get(self.device, {}).get('time', 1)
                    out[subsys]['time'] = data.dim_of(0) * ucf  # Just use the last `data` that's left over from the loop

                    measurements_l = [meas_.lower() for meas_ in measurements]
                    out_k_l = [k.lower() for k in list(out[sys].keys())]
                    if 'r' in measurements_l and 'z' in measurements_l and 'z' not in out_k_l:
                        out[subsys]['z'] = out[subsys]['r'] * 0
                    if 'redchisq' in measurements_l and 'redchisq' not in out_k_l:
                        if 'temp' in out[subsys]:
                            out[subsys]['redchisq'] = out[subsys]['temp'] * 0
                        elif 'density' in out[sys]:
                            out[subsys]['redchisq'] = out[subsys]['density'] * 0
                        else:
                            printw('WARNING: Unable to properly assign redchisq or even redchisq placeholder!')
                            out[subsys]['redchisq'] = None
            else:
                raise IOError(
                    'Unrecognized server/device option: {}. Honestly, how have you not been caught before '
                    'this? You should not have gotten this far (you are a bad person).'.format(self.device)
                )

        if is_device(self.device, 'DIII-D'):
            self['raw']['blessed_id'] = OMFITmdsValue(server=self.device, treename=treename, shot=self.shot, TDI='ts.blessed_id').data()[0]

        # Save shot & revision so data can be checked against input settings in the future
        self['raw']['device'] = copy.copy(self.device)
        self['raw']['shot'] = copy.copy(self.shot)  # Copy so that they don't update when settings in the tree change
        self['raw']['revision_num'] = copy.copy(self.revision_num)
        self['raw']['revision'] = copy.copy(self.revision)

        self.status['gathered'] = True
        print('Done gathering raw Thomson data.')

    def gather_efit_info(self):
        """
        Gathers basic EFIT data for use in mapping.
        """
        self.setdefault('efit_data', SortedDict())
        if self.check_efit_info():
            print('  Gathering EFIT {:}...'.format(self.efitid))

            g_file_quantities = ['rhovn', 'pres', 'bcentr', 'rmaxis', 'zmaxis', 'r', 'z', 'lim', 'cpasma']
            a_file_quantities = []
            derived_quantities = ['psin', 'psin1d', 'time']

            backup_plans = {'EFIT04': 'EFIT03', 'EFIT03': 'EFIT01', 'EFIT02': 'EFIT01'}

            efit_data = read_basic_eq_from_mds(
                device=self.device,
                server=None,
                shot=self.shot,
                tree=self.efitid,
                g_file_quantities=g_file_quantities,
                a_file_quantities=a_file_quantities,
                derived_quantities=derived_quantities,
            )

            backup_plan = backup_plans.get(self.efitid, None)
            if not self.allow_backup_efitid:
                backup_plan = None
            while backup_plan and not efit_data:
                printw('Could not find {}, so falling back to {}...'.format(self.efitid, backup_plan))

                efit_data = read_basic_eq_from_mds(
                    device=self.device,
                    server=None,
                    shot=self.shot,
                    tree=self.efitid,
                    g_file_quantities=g_file_quantities,
                    a_file_quantities=a_file_quantities,
                    derived_quantities=derived_quantities,
                )
                if not efit_data:
                    backup_plan = backup_plans.get(backup_plan, None)
                else:
                    print('It worked! Got equilibrium from backup source: {}'.format(backup_plan))
                    self['efit_data']['original_request_efitid'] = copy.copy(self.efitid)
                    self.efitid = backup_plan

            if not efit_data:
                raise OMFITerror(
                    'Could not read equilibrium data from {} and no backup plan found! ' 'Unable to map TS data!'.format(self.efitid)
                )

            self['efit_data'] = SortedDict()  # Clobber any existing efit_data to avoid mixing with old results.

            if efit_data:
                # Record which shot we're doing this for so we can compare later to ensure that data are current
                efit_data['shot'] = copy.copy(self.shot)
                efit_data['efitID'] = self.efitid
                efit_data['gathered_by'] = 'OMFITthomson'

                for a in list(efit_data.keys()):
                    self['efit_data'][a] = efit_data[a]

        else:
            print('OMFITthomson already has appropriate EFIT data for shot {}. ' 'Skipping EFIT gathering.'.format(self.shot))

    def map(self, note='', remove_efits_with_large_changes=False):
        """
        Maps Thomson to the EFIT. Because most of the TS data are at the
        same radial location, the interpolation of psi(r,z) onto R,Z for Thomson is
        sped up by first interpolating to the R for most Thomson, then interpolating
        along the resulting 1D psi(z). If there is more than one R value (such as if
        tangential TS is included), the program loops over each unique R value. This
        could be done with one 2D interpolation, but I think it would be slower.

        :param note: Prints a note when starting mapping.

        :param remove_efits_with_large_changes: Filter out EFIT time slices where the axis or boundary value of
            un-normalized psi changes too fast. It's supposed to trim questionable EFITs from the end, but it doesn't
            seem to keep them all out with reasonable thresholds. This feature was a nice idea and I think it's
            coded properly, but it isn't performing at the expected level, so either leave it off or tune it up better.
        """

        # Three segments of TS data: pulses before the first EFIT slice (may be empty)
        #                            pulses after the last EFIT slice (may be empty)
        #                            pulses between first & last EFIT slice

        # Just use the nearest slice.
        # If using EFIT03 or EFIT04 (as recommended), the EFIT goes on the TS timebase, anyway.

        print('Mapping TS to EFIT...' + note)

        if is_device(self.device, ['NSTX', 'NSTXU']) and self.efitid.upper().startswith('EFIT'):
            printw(
                'WARNING: Mapping of NSTX/U data to basic EFITs typically produces inaccurate results! '
                'Watch out for double valued profiles in the pedestal. Properly tuning psi_N mapping of NSTX '
                'Thomson data is complicated.'
            )

        self.printdq('map_TS systems = {}'.format(self.subsystems), )

        # Make sure the tree is set to accept processed data (psin for TS)
        self['processed'] = SortedDict()

        # Gather data
        need_to_gather = False  # For Thomson
        try:  # The recorded shot for gathered data should match the shot in the settings tree. Otherwise, gather.
            if self['raw']['shot'] != self.shot:
                need_to_gather = True
            for subsys in self.subsystems:
                if subsys not in self['raw']:
                    need_to_gather = True
        except KeyError:
            need_to_gather = True

        if need_to_gather:
            self.gather()

        need_to_gather_efit = False  # Do it again for EFIT
        try:  # The recorded shot for gathered data should match the shot in the settings tree. Otherwise, gather.
            if self['efit_data']['shot'] != self.shot:
                need_to_gather_efit = True
            if self['efit_data']['efitid'] != self.efitid:
                need_to_gather_efit = True
        except KeyError:
            need_to_gather_efit = True

        if need_to_gather_efit:
            self.printdq('  map_TS: need to gather EFIT info again', )
            self.gather_efit_info()

        self.printdq('  map_TS: done dealing with gathering stuff', )
        # At this point, data should be available.

        # Get some info out of EFIT
        efit_r = self['efit_data']['r']
        efit_z = self['efit_data']['z']
        if len(np.atleast_1d(np.shape(efit_r))) == 2:
            # Oh great, someone decided to save R as being time dependent, even though it probably isn't.
            # If it is, this script will be WRONG and bad. Note that the IMAS standard uses a time-dependent R-grid,
            # so this will have to be supported properly in the future. This script will have to be updated or replaced.
            printw(
                'WARNING: EFIT R grid was saved as 2D. If it is actually time dependent (probably is not), '
                'then mapping in fastTS will be wrong!'
            )
            nt = len(self['efit_data']['time'])
            wta = np.where(np.array(np.shape(efit_r)) == nt)[0][0]  # Where's the time axis?
            ii = 0
            if wta == 0:
                while efit_r[ii, :].max() == 0:
                    ii += 1  # Find a slice that's not blank. Some might be, but non-blanks should be the same.
                efit_r = efit_r[ii, :]
                efit_z = efit_z[ii, :]
            elif wta == 1:
                while efit_r[:, ii].max() == 0:
                    ii += 1
                efit_r = efit_r[:, ii]
                efit_z = efit_z[:, ii]
            else:
                raise ValueError('Problem finding which axis to deal with when collapsing EFIT R grid.')
        elif len(np.atleast_1d(np.shape(efit_r))) == 1:
            self.printdq('  EFIT R grid is 1D, which is how we like it. Good.', )
        else:
            raise ValueError('EFIT R grid has too many dimensions! np.shape(efit_r) = {}'.format(np.shape(efit_r)))

        # We have to make sure we get the best EFIT slice for each Thomson slice. We will compare timings.
        efit_time = self['efit_data']['time']
        # Filter EFIT slices to remove slices that are full of all zeros
        psin = self['efit_data']['psin']  # This psin is a function of efit_time, efit_r, and efit_z
        maxpsin = np.max(psin, axis=(1, 2))  # Maximum value at any point in space for each time slice
        self.printdq(
            '  map_TS: max value in space at each time slice maxpsin: np.shape(maxpsin) = {}'.format(np.shape(maxpsin)),
        )

        if remove_efits_with_large_changes:
            # Fine idea, but it doesn't seem to reliably get rid of EFITs where the innermost TS point jumps really far,
            # so the plot still looks stupid. Maybe we just need a better plot than tricontourf.
            sm = self['efit_data']['ssimag']  # un-normalized pSI values at the MAGnetic axis and at the BoundaRY
            bm = self['efit_data']['ssibry']
            #                             Sorry, I don't know what's up with the first s or why it's ssi instead of psi.
            dsm = deriv(efit_time, sm)  # Time derivative to check for changes
            dbm = deriv(efit_time, bm)
            sdsm = smooth(dsm, 5)
            sdbm = smooth(dbm, 5)
            dsmthresh = 0.025
            dbmthresh = 5e-4
            if debug:
                print('removing EFITs with large changes')
                f, ax = pyplot.subplots(2, sharex=True)
                ax[0].plot(dsm, label='time deriv of un-normalized psi value on axis')
                ax[0].plot(sdsm)
                ax[0].axhline(dsmthresh, color='k', linestyle='--')
                ax[0].axhline(-dsmthresh, color='k', linestyle='--')

                ax[1].plot(dbm, label='time deriv of un-normalized psi value on boundary')
                ax[1].plot(sdbm)
                ax[1].axhline(dbmthresh, color='k', linestyle='--')
                ax[1].axhline(-dbmthresh, color='k', linestyle='--')

            wefg = np.where((maxpsin != 0) * (abs(sdsm) < dsmthresh) * (abs(sdbm) < dbmthresh))[0]
        else:
            wefg = np.where(maxpsin != 0)[0]  # Find slices where max value is non-zero
        psin = psin[wefg, :, :]
        efit_time = efit_time[wefg]  # Filtered EFIT doesn't have blank (all zero) slices.

        # Loop through Thomson subsystems. 'core' is the most popular,
        # but you could also do ['core', 'divertor', 'tangential'] or any subset thereof.
        for subsys in self.subsystems:
            # Make sure the output has a place to go
            self['processed'].setdefault(subsys, SortedDict())

            try:
                ts_time = self['raw'][subsys]['time']  # Thomson timing to compare to EFIT
            except KeyError:
                ts_time = None
            if ts_time is None:
                printw('WARNING! System {:} appears to be missing data! Mapping aborted!'.format(sys))
                self['processed'][subsys]['psin_TS'] = None  # Leaving this here signals that mapping was attempted
                continue

            slice_to_use = np.zeros(len(ts_time))  # Record best EFIT slice for each TS slice and put it in this array

            # If thomson starts before EFIT (often does), then use the first valid EFIT slice for early Thomson data.
            # Bad, but nothing better. User should be able to notice this happening from a contour.
            w = np.where(ts_time < min(efit_time))[0]
            if len(w) > 0:
                slice_to_use[w] = 0
                first_ts = max(w) + 1
            else:
                first_ts = 0
            self.printdq(
                '  OMFITthomson.map: first_ts = {:}   (first TS time-slice that is within EFIT time range; '
                'earlier TS slices use the first available EFIT although it '
                'happens later than the early TS data)'.format(first_ts),

            )

            # If Thomson ends after EFIT (also often happens), then use the last valid EFIt slice for late Thomson data.
            # Thomson after EFIT probably happened after the flattop and you don't care, anyway. It should be apparent
            # that the same EFIT is being used if you look at a contour.
            w = np.where(ts_time > max(efit_time))[0]
            if len(w) > 0:
                slice_to_use[w] = len(efit_time) - 1
                last_ts = min(w) - 1
            else:
                last_ts = len(ts_time) - 1
            self.printdq(
                '  map_TS: last_ts = {:}  (last TS time-slice that is within EFIT time range; '
                'any slice later than this will use the last EFIT available)'.format(last_ts),

            )

            # Now go slice by slice and find the closest EFIT slice to each TS slice.
            ts_slices = np.arange(first_ts, last_ts + 1)  # This is a list of indices of TS slices that are within the
            #                                               EFIT time range and we should bother to find them the
            #                                               closest EFIT.
            self.printdq('     ts_slices = {}    (indices of TS slices that are within EFIT time range)'.format(ts_slices), )
            self.printdq('     len(ts_slices) = {}'.format(len(ts_slices)), )
            self.printdq('     ts_time[ts_slices] = {}'.format(ts_time[ts_slices]), )

            for i in ts_slices:
                # For each TS time slice, find index of the EFIT slice to use
                slice_to_use[i] = closestIndex(efit_time, ts_time[i])

            slice_to_use = slice_to_use.astype(int)

            if self.debug:
                self['debugging']['slice_to_use'] = slice_to_use
            self.printdq('     np.shape(slice_to_use) = {}'.format(np.shape(slice_to_use)), )
            self.printdq('     np.shape(efit_time) = {}   (this is after the wefg filter)'.format(np.shape(efit_time)), )
            self.printdq(
                '     np.shape(psin) = {}   (this is the psin from the EFIT after filtering out bad slices)'.format(np.shape(psin)),

            )

            # #############---------------------------------
            # Okay, great. We should know which EFIT slice is best for each TS slice. You could interpolate the EFIT in
            # time to be fancier, but this probably doesn't matter. It's fine. Let's go!

            # We're going to do a fast spatial interpolation.
            # This is optimized using specific information about the Thomson system: that almost all of the chords
            # are in the same radial position. That means that we can calculate the coefficients for the R
            # interpolation once for each unique R value (there is only 1 for the core, and only 1 for divertor.
            # Tangential is different). We do the R interpolation once, get psi_N vs Z at the correct R, and then
            # do a simple 1D interpolation. Fast! For the tangential system, it will loop through the 6 unique R
            # values instead of doing just 1 unique R value for core & div. Oh well.
            ts_r = self['raw'][subsys]['r']
            ts_z = self['raw'][subsys]['z']

            # Set of unique R and Z
            ur = set(ts_r)
            uz = set(ts_z)

            # zcheck = np.zeros(np.shape(ts_z))  # Set up debugging array

            # Make an array to catch psin at the TS locations vs EFIT time base. This guy needs to be converted to the
            # TS time base later. The mapping for this conversion was calculated earlier.
            psin_ts_almost = np.zeros([len(ts_r), len(efit_time)])

            for i, r in enumerate(ur):
                # Do the R interpolation for each Unique R value (ur)
                dr = r - efit_r
                right = np.searchsorted(efit_r, r, side="left")  # Find closest EFIT R on the left & right of TS R value
                if efit_r[right] == r:
                    # Shortcut in case of exact match
                    psin_slice = psin[:, :, right]
                else:
                    left = right - 1  # Find closest EFIT R values on the left and right of TS R value
                    dlr = efit_r[right] - efit_r[left]  # Find the spacing between the EFIT R values on L and R
                    left_weight = -dr[right] / dlr  # Large diff between TS & right EFIT ==> large weight on left value
                    right_weight = dr[left] / dlr  # Large diff between TS & left EFIT ==> large weight on right value
                    # Weighted sum of psin from left and right sides:
                    psin_slice = psin[:, :, left] * left_weight + psin[:, :, right] * right_weight
                    # This has reduced psin from psin(R,Z) to psin(Z)

                for j, z in enumerate(uz):
                    # Do the Z interpolation for each Unique Z value (uz)
                    # Same idea as before, except it reduces a line to a point instead of a grid to a line.
                    dz = z - efit_z
                    right = np.searchsorted(efit_z, z, side='left')
                    if efit_z[right] == z:
                        psin_pt = psin_slice[:, right]
                    else:
                        left = right - 1
                        dlr = efit_z[right] - efit_z[left]
                        left_weight = -dz[right] / dlr
                        right_weight = dz[left] / dlr

                        psin_pt = psin_slice[:, left] * left_weight + psin_slice[:, right] * right_weight

                    # Now we map this back into the shape of TS data. Remember, this interpolation operated on unique
                    # values within the TS coordinates, not on each point. This result here does not necessarily have
                    # compatible dimensions with the original TS, so we have to map it in.
                    wc = np.where((ts_r == r) * (ts_z == z))[0]
                    psin_ts_almost[wc, :] = psin_pt[np.newaxis, :]
                    # Now we have psi_N at each Thomson spatial location vs the EFIT time base.

            # It's simple to translate to the TS time base since we already figured out which EFIT slice was best to use
            self['processed'][subsys]['psin_TS'] = psin_ts_almost[:, slice_to_use]

        # Tag the output with shot and EFIT ID so it can be checked vs. user settings later (make sure data are current)
        self['processed']['psin_TS_shot'] = copy.copy(self.shot)
        self['processed']['psin_TS_efitID'] = copy.copy(self.efitid)
        self.status['mapped'] = True

    def filter(self):
        """
        Data quality and ELM filter

        ELM phase and timing data are used to select slices.
        Individual data are flagged to indicate whether they passed the filter.
        If any chords are completely bad, then they are just removed from the output.
        """

        print('  OMFITthomson: filtering data...')

        # Set up ELM filter
        apply_elm_filter = self.elm_filter is not False
        elm_phase_range = self.elm_filter['settings']['filtering']['elm_phase_range'] if apply_elm_filter else 0
        elm_since_reject_below = self.elm_filter['settings']['filtering']['elm_since_reject_below'] if apply_elm_filter else 0
        elm_since_accept_above = self.elm_filter['settings']['filtering']['elm_since_accept_above'] if apply_elm_filter else 0

        # Make sure things are ready
        if not self.status['mapped']:
            self.map()

        # Get plasma current for later
        if is_device(self.device, 'DIII-D'):
            ip = OMFITmdsValue(self.device, treename=None, shot=self.shot, TDI='ip')
            ipi = interp1d(ip.dim_of(0), ip.data(), bounds_error=False, fill_value=0)
        elif is_device(self.device, ('NSTX', 'NSTX-U')):
            ip = OMFITmdsValue(self.device, treename='engineering', shot=self.shot, TDI='analysis.ip1')
            ipi = interp1d(ip.dim_of(0) * 1000, ip.data(), bounds_error=False, fill_value=0)
        else:
            raise IOError(
                'No instructions for looking up plasma current for this device: {}. '
                'Unable to apply Thomson data filters. Please try again with a supported device from this '
                'list: {}'.format(self.device, self.supported_devices)
            )

        # Prepare tree to catch results
        fsetg = self.setdefault('filtered', SortedDict()).setdefault('settings', SortedDict())

        for subsys in self.subsystems:
            ts_time = self['raw'][subsys]['time']
            if ts_time is None:
                printw('WARNING! System {:} appears to be missing data. ' 'Aborting filtering for {:}.'.format(subsys, subsys))
                fsys = self['filtered'].setdefault(subsys, SortedDict())
                for a in ['time', 'r', 'z', 'chord_index', 'psin_TS', 'temp', 'density']:
                    # Throw None into a few key parameter names to make it clear that nothing good happened here.
                    fsys[a] = None
                fsys.setdefault('filters', SortedDict())['okay'] = None
                fsys['filters'].setdefault('raw', SortedDict())['raw_okay'] = None
                continue
            temp = copy.copy(self['raw'][subsys].get('temp', None))
            tempe = copy.copy(self['raw'][subsys].get('temp_e', None))
            density = copy.copy(self['raw'][subsys].get('density', None))
            density_e = copy.copy(self['raw'][subsys].get('density_e', None))

            # Figure out filters
            fs = self.quality_filters[subsys]  # Shortcut to system specific filter settings
            fg = self.quality_filters['global_override']  # Shortcut to global filter settings
            #                                               Global filter settings take precedence if not ==None
            selected_filters = {}
            # Things where the global should be able to take over
            for thing in ['redchisq_limit', 'frac_temp_err_hot_max', 'frac_temp_err_cold_max', 'frac_dens_err_max', 'hot_cold_boundary']:
                if fg[thing] is not None:
                    self.printdq(
                        '  Using GLOBAL OVERRIDE setting for {:} filter setting {:}, value = {:}  '
                        '<<<< OVERRIDE'.format(subsys, thing, fg[thing]),

                    )
                    selected_filters[thing] = fg[thing]
                else:
                    self.printdq(
                        'Using system specific setting for {:} filter setting {:}, value = {:}'.format(subsys, thing, fs[thing]),

                    )
                    selected_filters[thing] = fs[thing]
            # Things which are system-specific only
            for thing in ['bad_chords']:
                selected_filters[thing] = fs[thing]

            # Unpack (not all of them need to be unpacked because I put in selected_filters[''] around them
            redchisq_limit = selected_filters['redchisq_limit']
            bad_chords = selected_filters['bad_chords']
            frac_temp_err_hot_max = selected_filters['frac_temp_err_hot_max']
            frac_temp_err_cold_max = selected_filters['frac_temp_err_cold_max']
            hot_cold_boundary = selected_filters['hot_cold_boundary']

            # Time flags #---------------------------------------------------------------------------

            if int(apply_elm_filter) > 0:
                ep_devices = self.elm_filter.supported_devices
                if self.device in ep_devices:
                    # ELM filter
                    elm_okay = self.elm_filter.filter(times_to_filter=ts_time, cer_mode=False, stimes=0.0)
                else:
                    printw('WARNING: Current device ({}) is not supported by ELM_processing. Skipping ELM filter...'.format(device))
                    print('    ELM_processing supported devices: {}'.format(ep_devices))
                    elm_okay = np.ones(len(ts_time), bool)
                    apply_elm_filter = False
            else:
                elm_okay = np.ones(len(ts_time), bool)

            # Filter to cut negative time
            inshot_okay = ts_time > 0

            # Filter to select where ip is okay
            ipts = ipi(ts_time)
            if self.debug:
                self['debugging']['ipts'] = ipts
            ipokay = abs(ipts) > self.quality_filters['ip_thresh_frac_of_max'] * max(abs(ipts))

            # Combine all time-slice filters
            timeslice_okay = elm_okay * ipokay * inshot_okay

            # Position flags #-----------------------------------------------------------------------
            # Manual chord rejection
            manual_chord_okay = np.ones(len(self['raw'][subsys]['r']))
            if len(tolist(bad_chords, [None])):
                w = len(manual_chord_okay) > bad_chords > 0
                if np.sum(np.atleast_1d(w)):
                    manual_chord_okay[np.atleast_1d(bad_chords)[w]] = 0

            # Check to see that the chord got at least one slice
            nonzero_error = tempe.max(1) > 0

            # Combine all chord filters
            chord_okay = (manual_chord_okay * nonzero_error).astype(bool)

            # 2D flags #---------------------------------------------------------------------------
            all_okay_2d = np.ones((len(self['raw'][subsys]['r']), len(self['raw'][subsys]['time'])), bool)
            # Reduced chi squared below threshold
            if self['raw'][subsys].get('redchisq', None) is not None:
                redchisq_okay = self['raw'][subsys]['redchisq'] < redchisq_limit
            else:
                redchisq_okay = all_okay_2d
            # Check for high fractional error ---
            # Check fractional temp err
            if temp is not None:
                temp_nonzero = copy.copy(temp)
                temp_nonzero[temp_nonzero == 0] = 1.0  # Avoid divide by zero error
                frac_temp_err = tempe / temp_nonzero

                frac_err_okay = (temp > hot_cold_boundary) * (frac_temp_err < frac_temp_err_hot_max) + (temp <= hot_cold_boundary) * (
                    frac_temp_err < frac_temp_err_cold_max
                )
            else:
                frac_err_okay = all_okay_2d

            # Check fractional dens err
            if density is not None:
                dens_nonzero = copy.copy(density)
                dens_nonzero[dens_nonzero == 0] = 1.0  # Avoid divide by zero error
                frac_dens_err = density_e / dens_nonzero
                frac_dens_err_okay = frac_dens_err < selected_filters['frac_dens_err_max']

                # Overall fractional error combo
                frac_err_okay &= frac_dens_err_okay

            # Check for non-zero measurement (TS can't measure 0 and 0+/-0 means missing data). We can go from just
            # temperature. If Temperature exists, so will density. They are parameters output from the same fit to raw
            # signal.
            if tempe is not None:
                measurement_exist_okay = tempe > 0
            elif density_e is not None:
                measurement_exist_okay = density_e > 0
            else:
                measurement_exist_okay = all_okay_2d

            # Combine all 2D filters
            two_d_okay = redchisq_okay * frac_err_okay * measurement_exist_okay
            # This is ONLY the two D filters. The 1D filters are things like the ELM filter that are time only or the
            # bad chord selector which is position only. THESE ARE NOT INCLUDED HERE (because we can delete any row or
            # column that's all bad).

            if two_d_okay.max() > 1:
                two_d_okay[np.where(two_d_okay > 1)[0]] = 1

            ###########################

            chord_index = np.atleast_1d(list(range(len(self['raw'][subsys]['r']))))

            wt = timeslice_okay
            wc = chord_okay

            okay = np.atleast_2d(two_d_okay[:, wt][wc, :])

            okay_complete = copy.copy(two_d_okay)
            okay_complete[:, ~wt] = 0
            okay_complete[~wc, :] = 0
            # okay_complete has the same shape as two_d_okay, but it has the 1D filters applied to it.
            # USE THIS if you aren't removing bad slices entirely

            # Set up tree for results (make sure the trees exist and make shortcuts)
            fsys = self['filtered'].setdefault(subsys, SortedDict())
            filt = fsys.setdefault('filters', SortedDict())
            fset = fsys.setdefault('settings', SortedDict())
            fraw = filt.setdefault('raw', SortedDict())

            # Save filter results
            if self.quality_filters['remove_bad_slices']:
                filt['okay'] = okay  # This is two_d_okay with the bad time slices and chords REMOVED from the array
                fsys['chord_index'] = chord_index[wc]
                filt['elm_okay'] = elm_okay[wt]
            else:
                filt['okay'] = okay_complete  # This is two_d_okay with the bad time slices and chords set to ZERO
                #                               (the array stays the same size)
                fsys['chord_index'] = chord_index
                filt['elm_okay'] = elm_okay

            fraw['raw_okay'] = okay_complete
            fraw['redchisq_okay'] = redchisq_okay
            fraw['frac_err_okay'] = frac_err_okay
            fraw['measurement_exist_okay'] = measurement_exist_okay
            fraw['ipokay'] = ipokay
            fraw['inshot_okay'] = inshot_okay
            fraw['elm_okay'] = elm_okay
            fraw['manual_bad_chords'] = copy.copy(bad_chords)

            filt['accepted_time_slices'] = wt
            filt['accepted_chords'] = wc

            filt['two_d_okay'] = two_d_okay

            # Save filtered data
            if self.quality_filters['remove_bad_slices']:
                for tag in ['temp', 'temp_e', 'density', 'density_e', 'redchisq']:
                    # These get bad slices & chords removed. Remaining bad points are set to 0 by multiplying by `okay`.
                    if self['raw'][subsys].get(tag, None) is None:
                        self.printdq('  {} was None in system {}! Copying `None` across without filtering.'.format(tag, sys), )
                        fsys[tag] = None
                    else:
                        fsys[tag] = self['raw'][subsys][tag][wc, :][:, wt]
                for tag in ['psin_TS']:
                    # This is like the above entry for temp, etc.,
                    # but separate because it's in a different place than raw data.
                    fsys[tag] = self['processed'][subsys][tag][wc, :][:, wt]
                for tag in ['time']:  # These get bad slices removed; separate b/c different indexing than the 2D data
                    fsys[tag] = self['raw'][subsys][tag][wt]
                for tag in ['r', 'z']:  # These get bad chords removed; separate b/c different indexing than the 2D data
                    fsys[tag] = self['raw'][subsys][tag][wc]
            else:
                for tag in ['temp', 'temp_e', 'density', 'density_e', 'redchisq', 'r', 'z', 'time']:
                    # Unlike the other side of this if, the 1D & 2D arrays don't need different processing this time b/c
                    # we aren't removing the bad slices
                    fsys[tag] = self['raw'][subsys][tag]
                for tag in ['psin_TS']:  # This is separate because it's in a different place than the raw data
                    fsys[tag] = self['processed'][subsys][tag]

            if self.quality_filters['set_bad_points_to_zero']:
                # We can make an extra barrier against accidentally including bad data if we multiply the values at
                # every bad point by zero. This is an option because there may be cases where one would like to examine
                # which data have been rejected, and this is hard to do if they have been zeroed out.
                for tag in ['temp', 'temp_e', 'density', 'density_e', 'psin_TS']:
                    if fsys[tag] is not None:
                        fsys[tag] = fsys[tag] * okay.astype(float)

            # Save filter settings - sys specific
            # Without copy.copy(), the "copies" of the settings would update with the main one, and we don't want that.
            fset['redchisq_limit'] = copy.copy(redchisq_limit)
            fset['bad_chords'] = copy.copy(bad_chords)
            fset['frac_temp_err_hot_max'] = copy.copy(frac_temp_err_hot_max)
            fset['frac_temp_err_cold_max'] = copy.copy(frac_temp_err_cold_max)
            fset['frac_dens_err_max'] = copy.copy(selected_filters['frac_dens_err_max'])
            fset['hot_cold_boundary'] = copy.copy(hot_cold_boundary)
            fset['remove_bad_slices'] = copy.copy(self.quality_filters['remove_bad_slices'])
            fset['set_bad_points_to_zero'] = copy.copy(self.quality_filters['set_bad_points_to_zero'])

        # Save ELM detection & filter settings - all systems
        fsetg['elm_phase_range'] = copy.copy(elm_phase_range)
        fsetg['elm_since_reject_below'] = copy.copy(elm_since_reject_below)
        fsetg['elm_since_accept_above'] = copy.copy(elm_since_accept_above)

        if apply_elm_filter:
            elm_det_set = self.elm_filter['settings']['detection']
            fsetg['elm_detection_smooth_funct'] = copy.copy(elm_det_set['smoother'])
            fsetg['elm_detection_filterscopes'] = copy.copy(elm_det_set['default_filterscope_for_elms'])
            fsetg['elm_detection_auto_fscopes'] = 'filterscope_chosen_automatically_for_shot' in elm_det_set
            fsetg['elm_detection_tuning'] = copy.deepcopy(elm_det_set['{:}_tuning'.format(elm_det_set['smoother'])])

        # Save shot for records
        self['filtered']['device'] = copy.copy(self.device)
        self['filtered']['shot'] = copy.copy(self.shot)

        self.status['filtered'] = True
        print('Done filtering TS data.')

        # Add shortcuts to plot methods for convenience
        try:
            self.setdefault('plots', SortedDict())['profile_plot'] = function_to_tree(self.profile_plot, self)
            self['plots']['contour_plot'] = function_to_tree(self.contour_plot, self)
        except ImportError:
            type_, val_, traceback_ = sys.exc_info()
            self.printdq('  Failed to load plot script to tree with function_to_tree.', topic='omfit_elm')
            if self.debug:
                self.printdq(
                    '    Exception type = {type:}\n'
                    '    Exception value = {value:}\n'
                    '    Exception traceback = \n{trace:}'.format(type=type_, value=val_, trace=traceback_),
                    topic='omfit_elm',
                )
            # This won't work outside of OMFIT and we don't want it to

    def select_time_window(
        self,
        t0,
        dt=25.0,
        systems='all',
        parameters=['temp', 'density'],
        psi_n_range=[0, 1.5],
        strict=None,
        use_shifted_psi=True,
        alt_x_path=None,
        comment=None,
        perturbation=None,
        realtime=False,
    ):
        """
        Grabs Thomson data for the time window [t0-dt, d0+dt] for the sub-systems and parameters specified.

        :param t0: Center of the time window in ms

        :param dt: Half-width of the time window in ms

        :param systems: Thomson sub-systems to gather (like ['core', 'divertor', 'tangential']). If None: detect which
            systems are available.

        :param parameters: Parameters to gather (like ['temp', 'density', 'press'])

        :param psi_n_range: Range of psi_N values to accept

        :param strict: Ignored (function accepts this keyword so it can be called generically with same keywords as its
            counterpart in the quickCER module)

        :param use_shifted_psi: T/F attempt to look up corrected psi_N (for profile alignment) in alt_x_path.

        :param alt_x_path: An alternative path for gathering psi_N. This can be an OMFIT tree or a string which will
            give an OMFITtree when operated on with eval(). Use this to provide corrected psi_N values after doing
            profile alignment. Input should be an OMFIT tree containing trees for all the sub systems being considered
            in this call to select_time_window ('core', 'tangential', etc.). Each subsystem tree should contain an array
            of corrected psi_N values named 'psin_corrected'.

        :param comment: Optional: you can provide a string and your comment will be announced at the start of execution.

        :param perturbation: None or False for no perturbation or a dictionary with instructions for perturbing data for
            doing uncertainty quantification studies such as Monte Carlo trials. The dictionary can have these keys:

            - random: T/F (default T): to scale perturbations by normally distributed random numbers
            - sigma: float (default 1): specifies scale of noise in standard deviations. Technically, I think you
              could get away with passing in an array of the correct length instead of a scalar.
            - step_size: float: specifies absolute value of perturbation in data units (overrides sigma if present)
            - channel_mask: specifies which channels get noise (dictionary with a key for each parameter to mask
              containing a list of channels or list of T/F matching len of channels_used for that parameter)
            - time_mask: specifies which time slices get noise (dictionary with a key for each parameter to mask
              containing a list of times or list of T/F matching len of time_slices_used for that parameter)
            - data_mask: specifies which points get noise (overrides channel_mask and time_mask if present) (dictionary
              with a key for each parameter to mask containing a list of T/F matching len of data for that parameter.
              Note: this is harder to define than the channel and time lists.)

            Shortcut: supply True instead of a dictionary to add 1 sigma random noise to all data.

        :param realtime: T/F: Gather realtime data instead of post-shot analysis results.

        :return: A dictionary containing all the parameters requested. Each parameter is given in a
            dictionary containing x, y, e, and other information. x, y, and e are sorted by psi_N.
        """
        from operator import itemgetter

        if systems == 'all':
            systems = self.subsystems

        self.printdq('OMFITthomson: select_time_window...', )
        if comment is not None:
            self.printdq('OMFITthomson: {}'.format(comment), )

        if realtime:
            ts_src = 'filtered_RTTS'
        else:
            ts_src = 'filtered'

        # Minor notifications (tell user not to try to put real values in the unused keywords (uk)
        for ukn, uk in list({'strict': strict}.items()):
            if uk is not None:
                self.printdq(
                    '   {} keyword is ignored by fastTS version of select_time_window(), but its value was not None!'.format(ukn),

                )

        results = self

        if ts_src not in results:
            if ts_src == 'filtered_RTTS':
                self.printdq("fastTS: filtered realtime Thomson data missing in INPUTS! Executing RT gather+filter...", )
                raise NotImplementedError("Realtime data handling not ready yet")
            else:
                self.printdq("fastTS: filtered Thomson data missing in INPUTS! Executing gather+filter...", )
                self.__call__()

        if systems is None:
            systems = [k for k in list(results[ts_src].keys()) if isinstance(results[ts_src][k], dict) and k != 'settings']
            self.printdq('Auto-assigned systems to based on filtered data availability: {:}'.format(systems), )

        # Sanitize inputs
        parameters = tolist(parameters)
        systems = tolist(systems)
        psi_n_range = np.atleast_1d(psi_n_range)
        t0 = np.atleast_1d(t0)[0]

        result = {}
        for par in parameters:
            self.printdq('Loop through parameters: {:}'.format(par), )
            time_slices_used = np.array([])
            systems_used = []
            system_okay = np.zeros(len(systems), bool)
            x1 = np.array([])
            y1 = np.array([])
            e1 = np.array([])
            t1 = np.array([])
            c1 = np.array([])
            sys1 = np.array([])
            chords_used = []

            for i_sys, sys in enumerate(systems):
                self.printdq('Loop through systems: {:}'.format(sys), )
                # Make sure this system & parameter were gathered
                if sys not in results[ts_src]:
                    self.printdq(' No data for subsystem {:}'.format(sys), )
                    continue

                if par not in results[ts_src][sys] or results[ts_src][sys][par] is None:
                    printw(' fastTS select_time_window(): No data for this parameter: {:}'.format(par))
                    continue

                if use_shifted_psi:
                    try:
                        if isinstance(alt_x_path, str):
                            alt_x_path = eval(alt_x_path)
                        else:
                            alt_x_path = alt_x_path
                        x = alt_x_path[sys]['psin_corrected']
                    except (KeyError, TypeError):
                        x = results[ts_src][sys]['psin_TS']
                        self.printdq(' Got psi_N values from filtered_TS (not using shifted profiles)', )
                    else:
                        self.printdq(
                            ' Got psi_N values from alt_x_path (probably using shifted profiles) (path = {})'.format(
                                treeLocation(alt_x_path)[-1]
                            ),

                        )
                        self.printdq('   psi_N values: min = {}, max = {}, average = {}'.format(x.min(), x.max(), x.mean()), )
                else:
                    x = results[ts_src][sys]['psin_TS']
                    self.printdq(' Got psi_N values from filtered_TS (not using shifted profiles)', )

                y = results[ts_src][sys][par]

                try:
                    e = results[ts_src][sys]['{:}_e'.format(par)]
                except KeyError:
                    self.printdq(' Could not find uncertainties for this parameter: {:}'.format(par), )
                    # User is allowed to request r and z as parameters, but these do not have uncertainties.
                    e = np.zeros(len(np.atleast_1d(x)), type(np.atleast_1d(x)[0]))
                okay = results[ts_src][sys]['filters']['okay']
                t = results[ts_src][sys]['time']
                ch = results[ts_src][sys]['chord_index']
                ch2 = ch[:, np.newaxis] + np.zeros(np.shape(x))  # 2D version of chord index for tracking chords used
                sys_num = {'core': 0, 'divertor': 1000, 'tangential': 2000}[sys]
                ch2 += sys_num

                # Time filter
                t2 = t[np.newaxis, :] + np.zeros(np.shape(x))  # 2D version of time for making the filter we'll use on data
                wt = (t2 >= (t0 - dt)) & (t2 <= (t0 + dt))

                # Position filter
                wx = (x >= min(psi_n_range)) & (x <= max(psi_n_range))

                # Overall filter
                w = wt * wx * okay

                # Make sure the filter doesn't delete everything
                if w.max() < 1:
                    self.printdq(' No data within this time window for this subsystem: {:}+/-{:}, {:}'.format(t0, dt, sys), )
                    continue

                x1 = np.append(x1, x[w])
                y1 = np.append(y1, y[w])
                e1 = np.append(e1, e[w])
                t1 = np.append(t1, t2[w])
                c1 = np.append(c1, ch2[w])

                # Keep track of slices and chords used
                time_slices_used0 = np.sort(tolist(set(t2[w].flatten())))  # tolist() removes the set type
                time_slices_used = np.append(time_slices_used, time_slices_used0)
                chords_used0 = np.sort(tolist(set(ch2[w].flatten())))
                # chords_used0 = ['{}{:02d}'.format(sys[0], int(ch_)) for ch_ in chords_used0]
                chords_used = np.append(chords_used, chords_used0)

                sys1 = np.append(sys1, [sys] * len(x[w]))
                systems_used += [sys]

                system_okay[i_sys] = True  # Any error will abort the loop, so we won't get to here unless things are okay.
                self.printdq('  {:} {:} looks okay'.format(par, sys), )
                # Done with system loop

            # Finish working on this parameter
            if system_okay.max() < 1:
                self.printdq(' Failed to gather parameter {:} from any subsystem'.format(par), )
                continue

            # Sort by x
            seq = list(zip(x1, y1, e1, t1, c1, sys1))
            seq2 = sorted(seq, key=itemgetter(0))
            x2, y2, e2, t22, c22, sys2 = list(zip(*seq2))

            x2 = np.array(x2)
            y2 = np.array(y2)
            e2 = np.array(e2)
            t22 = np.array(t22)
            c22 = np.array(c22)
            sys2 = np.array(sys2)

            result[par] = {
                'x': x2,
                'y': y2,
                'e': e2,
                't': t22,
                'ch': c22,
                'channel_type': sys2,
                'shot': copy.copy(results[ts_src]['shot']),
                'filter_settings': copy.deepcopy(results[ts_src]['settings']),
                'time_slices_used': time_slices_used,
                'channels_used': chords_used,
                'systems_used': systems_used,
                'mapping_equilibrium': copy.copy(results['efit_data']['efitID']),
            }

            things = ['typical_scale', 'typical_pedestal_scale', 'typical_sol_scale']
            for thing in things:
                if '{}_{}'.format(par, thing) in results[ts_src]:
                    result[par][thing] = results[ts_src]['{}_{}'.format(par, thing)]

        def perturb_data(data, pert=None):
            """
            Applies a perturbation to data.

            :param data: result dictionary containing data to be perturbed.

            :param pert: Instructions for applying perturbations.

            :return: result dictionary with perturbations added.
            """
            self.printdq('Adding perturbations to Thomson data returned by select_time_window()...', )
            try:
                self.printdq('  pert.keys() = {}'.format(list(pert.keys())), )
            except AttributeError:
                pass
            else:
                if 'data_mask' in list(pert.keys()):
                    try:
                        self.printdq("    pert['data_mask'].keys() = {}".format(list(pert['data_mask'].keys())), )
                    except AttributeError:
                        self.printdq("    pert['data_mask'] = {}".format(pert['data_mask']), )

            # Figure out perturbation type
            if isinstance(pert, dict):
                # Normally, the user should pass in a dictionary for pert with pert['type'] = the type they want.
                randomize = pert.get('random', True)
                sigma = pert.get('sigma', 1)
                step_size = pert.get('step_size', None)
                channel_mask = pert.get('channel_mask', None)
                time_mask = pert.get('time_mask', None)
                data_mask = pert.get('data_mask', None)

            elif type(pert) in [bool, bool_]:
                # If pert is True instead of a dictionary, do random noise for all channels
                if pert:
                    randomize = True
                    sigma = 1
                    step_size = None
                    channel_mask = None
                    time_mask = None
                    data_mask = None
                else:
                    # Perturbations turned off
                    return data
            elif pert is None:
                self.printdq('pert is None: perturbations disabled', )
                return data
            else:
                # Could not figure it out
                printe('Could not figure out perturbation type. Aborting perturb_data() and returning unperturbed data.')
                print('  pert = {}'.format(pert))
                return data

            if data_mask:
                self.printdq('  Data mask detected; disabling channel_mask and time_mask.', )
                time_mask = None
                channel_mask = None

            for par_ in list(data.keys()):
                self.printdq(' Perturbing {}...'.format(par_), )
                p = data[par_]

                def setup_mask(mask_, xx, is_data=False, label=''):
                    self.printdq('   Mask setup... ({})'.format(label), )
                    n = len(xx)
                    if not (len(np.atleast_1d(mask_)) > 5 or isinstance(mask_, dict)):
                        self.printdq('     Input mask = {}'.format(mask_), )
                    elif isinstance(mask_, dict):
                        self.printdq('     Input mask is a dictionary with mask_.keys() = {}'.format(list(mask_.keys())), )
                        for key in list(mask_.keys()):
                            self.printdq("         len(mask_['{}']) = {}".format(key, len(mask_[key])))
                    elif len(np.atleast_1d(mask_)) > 5:
                        self.printdq('     Input mask is type {} with length {}'.format(type(mask_), len(np.atleast_1d(mask_))), )
                    else:
                        self.printdq('     Input mask is type {}'.format(type(mask_)), )
                    mask_g = copy.deepcopy(mask_)
                    if mask_g is not None:
                        # Try to get out the mask
                        mask = mask_g.get(par_, None)
                    else:
                        mask = None
                    if mask is None:
                        # Make up the default mask, which passes everything
                        self.printdq('        Input mask was replaced with all True because it was None.', )
                        mask = np.ones(n, bool)
                    # Try to detect a mask which has been input as a list of channels or slices to pass.
                    mask_okay = (type(tolist(mask)[0]) in [bool, bool_]) and (len(mask) == n)

                    if not mask_okay:
                        if is_data:
                            # The normal mask transformations for channel & time don't work for data, so fail everything
                            printw(
                                '        Improperly formed data mask detected for {}; len(mask) = {} vs. len(xx) = {}. '
                                'Cancelling perturbations...'.format(par_, len(mask), len(xx))
                            )
                            mask = (xx * 0).astype(bool)
                        else:
                            # The mask is a list of bools of the proper length, but maybe it can be transformed int one.
                            if type(tolist(mask)[0]) in [bool, bool_]:
                                # The mask looks like a list/array of bools, but the length doesn't match.
                                printw(
                                    '        Improperly formed {} MASK detected for {}; len(mask) = {} vs. '
                                    'len(xx) = {}. Cancelling perturbations...'.format(label, par_, len(mask), len(xx))
                                )
                                mask = (xx * 0).astype(bool)
                            else:
                                # Assume that mask is a list of time slices or channels to use. Loop through each
                                # channel or time in the list and flag every datum which matches.
                                self.printdq('     mask needs additional processing...', )
                                if not (
                                    (isinstance(mask[0], type(xx[0])))
                                    or (isinstance(mask[0], str) and isinstance(xx[0]), str)
                                    or (is_numeric(mask[0]) and is_numeric(xx[0]))
                                ):
                                    raise ValueError(
                                        'Incompatible types between mask and data or coordinate to be masked '
                                        '({}). Mask type: {}, data type: {}. Types may only disagree if mask '
                                        'is boolean.'.format(par_, type(mask[0]), type(xx[0]))
                                    )
                                mask0 = copy.copy(mask)
                                mask = np.zeros(n, bool)
                                for m in mask0:
                                    if len(np.atleast_1d(xx == m)) != len(mask):
                                        raise ValueError(
                                            'An error occurred while masking data for perturbations: '
                                            'length of mask did not match length of match adjustment.'
                                        )
                                    mask[xx == m] = True
                    else:
                        self.printdq(
                            '    Mask is a list of bools of the correct length ({}); No more processing!'.format(len(mask)),

                        )
                        self.printdq(
                            '   Done processing mask. len(mask) = {}, len(xx) = {}, label = {}, is_data = {}.'.format(
                                len(mask), len(xx), label, is_data
                            ),

                        )

                    return mask

                # Resolve masks into lists of T/F flags matching the lengths of time_slices_used, channels_used, and x
                tm_ = setup_mask(time_mask, p['time_slices_used'], label='time')
                cm_ = setup_mask(channel_mask, p['channels_used'], label='channel')
                dm_ = setup_mask(data_mask, p['x'], is_data=True, label='data')

                # Resolve masks into list of T/F matching length of x
                valid_ch = p['channels_used'][cm_]
                valid_t = p['time_slices_used'][tm_]
                cm_ = [ch_ in valid_ch for ch_ in p['ch']]
                tm_ = [t_ in valid_t for t_ in p['t']]

                # Combine masks into base perturbation
                final_mask = dm_ & cm_ & tm_
                perturbation_ = copy.copy(final_mask).astype(float)

                # Scale the perturbation by sigma*e or by step_size
                if step_size:
                    perturbation_ *= step_size
                    self.printdq('  Scaled perturbations by absolute step_size {}'.format(step_size), )
                else:
                    perturbation_ *= sigma * p['e']
                    self.printdq('  Scaled perturbations by some number of standard deviations ({})'.format(sigma), )

                if randomize:
                    # Scale the perturbation by normally distributed random numbers
                    perturbation_ *= np.random.normal(0, 1, len(perturbation_))
                    self.printdq('  Randomized perturbations', )

                p['perturbation'] = perturbation_
                p['perturbation_added'] = np.any(perturbation_)
                p['y'] += perturbation_
                p['final_perturbation_mask'] = final_mask
                p['perturbation_masks'] = {'time': tm_, 'channel': cm_, 'data': dm_, 'valid_lists': {'t': valid_t, 'ch': valid_ch}}
            return data

        # Handle perturbations
        if perturbation:
            result = perturb_data(result, perturbation)
            result['_perturbation_added'] = False
            for par in parameters:
                if par in result:
                    if result[par].setdefault('perturbation_added', False):
                        result['_perturbation_added'] = True
        else:
            self.printdq('No perturbations added to Thomson data', )
            for par in parameters:
                if par in result:
                    result[par]['perturbation'] = None
                    result[par]['perturbation_added'] = False
            result['_perturbation_added'] = False

        # Record instructions for perturbations
        result['_perturbation'] = perturbation

        # Note data source
        result['_realtime'] = realtime
        result['__ts_src__'] = ts_src

        return result

    # Calculate derived quantities
    def calculate_derived(self, zeff=2.0, ti_over_te=1.0, zi=1.0, zb=6.0, mi=2.0, mb=12.0, use_uncert=False):
        """
        Calculate simple derived quantities.

        This is limited to quantities which are insensitive to ion measurements and can be reasonably estimated
        from electron data only with limited assumptions about ions.

        Assumptions:

        :param zeff: float
            Assumed effective charge state of ions in the plasma:
            Z_eff=(n_i * Z_i^2 + n_b * Z_b^2) / (n_i * Z_i + n_b * Z_b)

        :param ti_over_te: float or numeric array matching shape of te
            Assumed ratio of ion to electron temperature

        :param zi: float or numeric array matching shape of ne
            Charge state of main ions. Hydrogen/deuterium ions = 1.0

        :param mi: float or numeric array matching shape of te
            Mass of main ions in amu. Deuterium = 2.0

        :param zb: float or numeric array matching shape of ne
            Charge state of dominant impurity. Fully stripped carbon = 6.0

        :param mb: float or numeric array matching shape of ne
            Mass of dominat impurity ions in amu. Carbon = 12.0

        :param use_uncert: bool
            Propagate uncertainties (takes longer)
        """
        # Set up assumptions
        assume = self['assumptions'] = SortedDict()
        assume['note'] = (
            'Assumptions used as needed for derived quantities. Calculations should not be very '
            'sensitive to these assumptions such that high accuracy is not required.'
        )
        assume['Z_eff'] = zeff
        assume['Ti_over_Te'] = ti_over_te
        assume['Z_i'] = zi
        assume['Z_b'] = zb
        assume['m_i'] = mi
        assume['m_b'] = mb

        # Start calculating derived quantities
        out = self['analysis'] = SortedDict()

        for sub in self.subsystems:
            out[sub] = SortedDict()
            assume[sub] = SortedDict()
            okay = self['filtered'][sub]['filters']['okay']
            te = ne = None
            if self['filtered'][sub]['temp'] is not None:
                te = uarray(self['filtered'][sub]['temp'], self['filtered'][sub]['temp_e'])
            if self['filtered'][sub]['density'] is not None:
                ne = uarray(self['filtered'][sub]['density'], self['filtered'][sub]['density_e'])
            if (te is not None) and (ne is not None):
                pe = te * ne * 1.6021766e-19  # Convert eV * m^-3 to Pa
                self['filtered'][sub]['press'] = nominal_values(pe)
                self['filtered'][sub]['press_e'] = std_devs(pe)
            else:
                self['filtered'][sub]['press'] = self['filtered'][sub]['press_e'] = None

            if not use_uncert:
                te, ne = nominal_values(te), nominal_values(ne)
            te_, ne_, bad = self.data_filter(te, ne, okay=okay)
            nb = (ne / zb) * (zeff - zi) / (zb - zi)  # Get impurity density from Zeff
            ni = (ne - nb * zb) / zi  # Get main ion density from electron and impurity densities
            ti = te * ti_over_te  # Get ion temperature from assumed relationship to electron temperature

            assume[sub]['n_b'] = nb
            assume[sub]['n_i'] = ni
            assume[sub]['T_i'] = ti

            out[sub]['debye'] = lambda_debye(te=te_, ne=ne_)  # m
            debye_, _ = self.data_filter(out[sub]['debye'])
            out[sub]['lnLambda'], out[sub]['lnLambda_e'] = self.lnlambda(te_, ne_, debye_)
            out[sub]['resistivity'] = self.resistivity(te_, zeff, out[sub]['lnLambda'])  # Ohm*m
            out[sub]['slowing_down_time'] = self.taue(te_, ne_, out[sub]['lnLambda_e'], mb, zb)
            for item in ['debye', 'lnLambda', 'lnLambda_e', 'resistivity', 'slowing_down_time']:
                out[sub][item][bad] = np.NaN

        self.status['calcs'] = True

    @staticmethod
    def lnlambda(te, ne, debye):
        """
        Calculate the Coulomb logarithm for electrons ln(Lambda)

        :param te: array
            Electron temperature in eV

        :param ne: array matching dimensions of te
            Electron density in m^-3

        :param debye: array
            Debye length in m

        :return: lnLambda, lnLambda_e
        """

        # General? lnLambda; Source: Callen 2006 book: Fundamentals of plasma physics chapter 2
        ee = 4.8032e-10  # Elementary charge in statcoulomb
        te_erg = te * constants.eV * 1e7
        r_c = ee ** 2 / te_erg  # cm
        r_c /= 100.0  # (m) Classical distance of closest approach
        r_qm = 1.1e-10 / te ** 0.5  # m Quantum Mechanical distance of closest approach
        r_min = np.maximum(r_c, r_qm)
        ln_lambda = np.log(nominal_values(debye / r_min))

        # lnLambda for electron-electron collisions; Source: NRL Plasma Formulary 2009
        ln_lambda_e = (
            23.5
            - np.log((nominal_values(ne) / 1e6) ** 0.5 * nominal_values(te) ** (-5.0 / 4.0))
            - (1e-5 + (np.log(nominal_values(te)) - 2) ** 2 / 16.0) ** 0.5
        )

        return ln_lambda, ln_lambda_e

    @staticmethod
    def resistivity(te, zeff, ln_lambda):
        """
        Calculate Spitzer transverse resistivity using NRL Plasma Formulary 2009 Page 29

        :param te: float or array
            Electron temperature in eV

        :param zeff: float or array matching dimensions of te
            Effective ion charge state for collisions with electrons

        :param ln_lambda: float or array matching dimensions of te
            Coulomb logarithm

        :return: array matching dimensions of te
            Resistivity in Ohm*m
        """
        return 1.03e-4 * zeff * ln_lambda * te ** (-1.5)

    @staticmethod
    def taue(te, ne, ln_lambda_e, m_b=2.0, z_b=1.0):
        """
        Calculates the spitzer slowing down time using equation 5 of W. Heidbrink's 1991 DIII-D physics memo

        :param te: An array of T_e values in eV

        :param ne: Array of n_e values in m^-3

        :param ln_lambda_e: Coulomb logarithm for electron-electron collisions

        :param m_b: Atomic mass of beam species (normally deuterium) in atomic mass units

        :param z_b: Atomic number of beam species (normally deuterium) in elementary charges

        :return: Fast ion slowing down time in ms.
        """

        self.printdq('fastTS: OMFITlib_slowdown_time...', )

        c = 6.3e8 * m_b / z_b ** 2  # Collect constants

        ne2 = ne * 1e-6  # Convert from m^-3 to cm^-3

        bottom = ne2 * ln_lambda_e
        recip = bottom * 0
        recip[bottom > 0] = 1.0 / bottom[bottom > 0]  # Avoid divide by zero

        tau_se = c * te ** 1.5 * recip  # Seconds

        return tau_se * 1000  # ms

    @staticmethod
    def data_filter(*args, **kwargs):
        """
        Removes bad values from arrays to avoid math errors, for use when calculating Thomson derived quantities

        :param args: list of items to sanitize

        :param kwargs: Keywords
            - okay: array matching dimensions of items in args: Flag indicating whether each element in args is okay
            - bad_fill_value: float: Value to use to replace bad elements

        :return: list of sanitized items from args, followed by bad
        """
        bad = np.zeros(np.shape(args[0]), bool)
        okay = kwargs.pop('okay', None)
        bad_fill_value = kwargs.pop('bad_fill_value', 1.0)
        if okay is not None:
            bad = bad | ~okay
        for arg in args:
            sd = std_devs(arg)
            if (np.atleast_1d(sd) == 0).all():
                sd += 1.0
            bad = bad | (nominal_values(arg) <= 0) | (sd <= 0)
        new_args = copy.deepcopy(args)
        for i in range(len(new_args)):
            if (new_args[i] is not None) and (np.shape(new_args[i]) == np.shape(bad)):
                new_args[i][bad] = bad_fill_value
        return tolist(new_args) + [bad]

    # Plot methods
    def plot(self, fig=None, axs=None):
        """
        Launches default plot, which is normally self.elm_detection_plot(); can be changed by setting self.default_plot.

        :return: (Figure instance, array of Axes instances)
            Tuple containing references to figure and axes used by the plot
        """
        if fig is None:
            fig = pyplot.gcf()
        return getattr(self, self.default_plot, self.contour_plot)(fig=fig, axs=axs)

    @staticmethod
    def setup_axes(fig, nrow=1, ncol=1, squeeze=True, sharex='none', sharey='none'):
        """
        Utility: add grid of axes to existing figure

        :param fig: Figure instance

        :param nrow: int
            Number of rows

        :param ncol: int
            Number of columns

        :param squeeze: bool
            Squeeze output to reduce dimensions. Otherwise, output will be a 2D array

        :param sharex: string
            Describe how X axis ranges should be shared/linked. Pick from: 'row', 'col', 'all', or 'none'

        :param sharey: string
            Describe how Y axis ranges should be shared/linked. Pick from: 'row', 'col', 'all', or 'none'

        :return: Axes instance or array of axes instances
        """

        import matplotlib.axes

        axs = np.empty((nrow, ncol), matplotlib.axes.Axes)
        axs[0, 0] = fig.add_subplot(nrow, ncol, 1)
        sharex = 'all' if sharex is True else sharex
        sharey = 'all' if sharey is True else sharey
        for ix in range(nrow):
            for iy in range(ncol):
                i = iy + ncol * ix

                if (ix > 0) and sharex in ['col', 'column']:
                    sx = axs[0, iy]
                elif (iy > 0) and sharex == 'row':
                    sx = axs[ix, 0]
                elif (i > 0) and sharex == 'all':
                    sx = axs[0, 0]
                else:
                    sx = None

                if (ix > 0) and sharey in ['col', 'column']:
                    sy = axs[0, iy]
                elif (iy > 0) and sharey == 'row':
                    sy = axs[ix, 0]
                elif (i > 0) and sharey == 'all':
                    sy = axs[0, 0]
                else:
                    sy = None

                if i > 0:
                    axs[ix, iy] = fig.add_subplot(nrow, ncol, i + 1, sharex=sx, sharey=sy)
        if squeeze:
            axs = np.squeeze(axs)
        return axs

    def profile_plot(
        self, t=None, dt=25.0, position_type='psi', params=['temp', 'density'], systems='all', unit_convert=True, fig=None, axs=None
    ):
        """
        Plots profiles of physics quantities vs. spatial position for a selected time window

        :param t: float
            Center of time window in ms

        :param dt: float
            Half-width of time window in ms. All data between t-dt and t+dt will be plotted.

        :param position_type: string
            Name of X coordinate. Valid options: 'R', 'Z', 'PSI'

        :param params: list of strings
            List physics quantities to plot. Valid options are temp, density, and press

        :param systems: list of strings or 'all'
            List subsystems to include in the plot. Choose all to use self.subsystems.

        :param unit_convert: bool
            Convert units from eV to keV, etc. so most quantities will be closer to order 1 in the core.

        :param fig: Figure instance
            Plot will be drawn using existing figure instance if one is provided. Otherwise, a new figure will be made.

        :param axs: 1D array of Axes instances matching length of params.
            Plots will be drawn using existing Axes instances if they are provided. Otherwise, new axes will be added to
            fig.

        :return: Figure instance, 1D array of Axes instances
        """
        from matplotlib import pyplot

        if systems == 'all':
            systems = self.subsystems

        names = {
            'press': '$p_e$ (kPa)' if unit_convert else '$p_e$ (Pa)',
            'density': '$n_e$ (10$^{19}$/m$^{3}$)' if unit_convert else '$n_e$ (m$^{-3}$)',
            'temp': '$T_e$ (keV)' if unit_convert else '$T_e$ (eV)',
        }
        multipliers = {'press': 1e-3 if unit_convert else 1, 'density': 1e-19 if unit_convert else 1, 'temp': 1e-3 if unit_convert else 1}

        if fig is None:
            fig = pyplot.figure()
        if axs is None:
            axs = self.setup_axes(fig, len(tolist(params)), sharex='all')
        axs = np.atleast_1d(axs)
        axs[0].set_title('Thomson scattering')
        for ax in axs[:-1]:
            ax.tick_params(labelbottom=False)

        if t is None:
            self.printdq('No profile time provided to OMFITthomson profile_plot. Picking one arbitrarily...', topic='OMFITthomson')
            # Pick a time automatically based on where data are available
            okay1 = self['filtered'][systems[0]]['filters']['okay']
            # Sum okay flag along channels
            okay2 = np.sum(okay1, axis=0)
            # Find times when most channels are available (avail. ch. count >= 90th percentile)
            okay3 = okay2 >= np.percentile(okay2, 90)
            # Take the mean of times when most channels are available and use that to plot
            t = np.mean(self['filtered'][systems[0]]['time'][okay3])
            # Is this a good idea? Well, if you don't like it, try passing in a time!
            printw(
                'No time provided to OMFITthomson.profile_plot. t = {} was chosen; it is the average of times with '
                'high channel availability on the first listed subsystem ({}).'.format(t, systems[0])
            )

        for sub in systems:
            wt = (self['filtered'][sub]['time'] >= (t - dt)) & (self['filtered'][sub]['time'] <= (t + dt))
            okay = self['filtered'][sub]['filters']['okay'][:, wt]
            if position_type in ['z', 'Z']:
                x = self['filtered'][sub]['z'][:, np.newaxis] + 0 * wt
                axs[-1].set_xlabel('$Z$ (m)')
            elif position_type in ['r', 'R']:
                x = self['filtered'][sub]['r'][:, np.newaxis] + 0 * wt
                axs[-1].set_xlabel('$R$ (m)')
            else:
                x = self['filtered'][sub]['psin_TS'][:, wt]
                axs[-1].set_xlabel(r'$\psi_N$')

            for i, param in enumerate(tolist(params)):
                axs[i].set_ylabel(names[param])
                y = self['filtered'][sub][param][:, wt] * multipliers[param]
                try:
                    ye = self['filtered'][sub][param + '_e'][:, wt] * multipliers[param]
                except KeyError:
                    ye = y * 0
                axs[i].errorbar(x[okay], y[okay], ye[okay], label=sub, linestyle='', marker='_')

        for ax in axs:
            ax.legend(loc=0)

        try:
            # Getting at OMFIT plot utilities when doing stand-alone command-line stuff can be a burden
            cornernote(shot=self.shot, device=self.device, time=r'{}$\pm${}'.format(t, dt))
        except NameError:
            fig.text(
                0.99,
                0.01,
                r'{}#{} {}$\pm${} ms'.format(self.device, self.shot, t, dt),
                fontsize=10,
                ha='right',
                transform=pyplot.gcf().transFigure,
            )

        return fig, axs

    def contour_plot(
        self,
        position_type='psi',
        params=['temp', 'density'],
        unit_convert=True,
        combine_data_before_contouring=False,
        num_color_levels=41,
        fig=None,
        axs=None,
    ):
        """
        Plots contours of a physics quantity vs. time and space

        :param position_type: string
            Select position from 'R', 'Z', or 'PSI'

        :param params: list of strings
            Select parameters from 'temp', 'density', 'press', or 'redchisq'

        :param unit_convert: bool
            Convert units from e.g. eV to keV to try to make most quantities closer to order 1

        :param combine_data_before_contouring: bool
            Combine data into a single array before calling tricontourf. This may look smoother, but it can hide the way
            arrays from different subsystems are stitched together

        :param num_color_levels: int
            Number of contour levels

        :param fig: Figure instance
            Provide a Matplotlib Figure instance and an appropriately dimensioned array of Axes instances to overlay

        :param axs: array of Axes instances
            Provide a Matplotlib Figure instance and an appropriately dimensioned array of Axes instances to overlay

        :return: Figure instance, array of Axes instances
            Returns references to figure and axes used in plot
        """
        from matplotlib import pyplot

        if fig is None:
            fig = pyplot.figure()
        if axs is None:
            axs = self.setup_axes(fig, len(tolist(params)), sharex='all')
        axs = np.atleast_1d(axs)
        axs[-1].set_xlabel('Time (ms)')
        axs[0].set_title('Thomson scattering')
        for ax in axs[:-1]:
            ax.tick_params(labelbottom=False)

        tt = np.array([])
        xx = np.array([])
        yy = np.array([])

        names = {
            'press': '$p_e$ (kPa)' if unit_convert else '$p_e$ (Pa)',
            'density': '$n_e$ (10$^{19}$/m$^{3}$)' if unit_convert else '$n_e$ (m$^{-3}$)',
            'temp': '$T_e$ (keV)' if unit_convert else '$T_e$ (eV)',
        }
        multipliers = {'press': 1e-3 if unit_convert else 1, 'density': 1e-19 if unit_convert else 1, 'temp': 1e-3 if unit_convert else 1}

        for ax, param in zip(axs, params):
            for sub in self.subsystems:
                okay = self['filtered'][sub]['filters']['okay']
                t = self['filtered'][sub]['time'][np.newaxis, :] + 0 * okay

                if position_type in ['z', 'Z']:
                    x = self['filtered'][sub]['z'][:, np.newaxis] + 0 * okay
                    ax.set_ylabel('$Z$ (m)')
                elif position_type in ['r', 'R']:
                    x = self['filtered'][sub]['r'][:, np.newaxis] + 0 * okay
                    ax.set_ylabel('$R$ (m)')
                else:
                    x = self['filtered'][sub]['psin_TS']
                    ax.set_ylabel(r'$\psi_N$')

                y = nominal_values(self['filtered'][sub][param]) * multipliers.get(param, 1)

                xf = x.flatten()
                tf = t.flatten()
                yf = y.flatten()
                w = okay.flatten().astype(bool)
                tf = tf[w]
                xf = xf[w]
                yf = yf[w]

                tt = np.append(tt, tf)
                xx = np.append(xx, xf)
                yy = np.append(yy, yf)

                if not combine_data_before_contouring:
                    im = ax.tricontourf(tf, xf, yf, num_color_levels)

            if combine_data_before_contouring:
                im = ax.tricontourf(tt, xx, yy, num_color_levels)

            cb = pyplot.colorbar(im, ax=ax)
            cb.set_label(names.get(param, param))
            ax.axhline(1.0, color='k', linestyle='--')

        try:
            # Getting at OMFIT plot utilities when doing stand-alone command-line stuff can be a burden
            cornernote(shot=self.shot, device=self.device, time='')
        except NameError:
            fig.text(0.99, 0.01, '{}#{}'.format(self.device, self.shot), fontsize=10, ha='right', transform=pyplot.gcf().transFigure)

        return fig, axs


class TestOMFITthomson(unittest.TestCase):

    """
    Tests for OMFITthomson class and supporting functions. Does not require OMFIT framework/GUI to be running.
    """

    from matplotlib import pyplot

    # Set up test case
    device = 'DIII-D'
    shot = 154749
    efitid = 'EFIT03'
    time0 = 2000.0  # Default time to use when needed

    # Choose test options
    show_debug_plots = False

    # Status flags
    plots_open = pyplot.get_fignums()

    # Test helpers
    def setUp(self):
        # Announce start of test with debug print (occasionally helps to sort out weird problems)
        test_id = self.id()
        test_name = '.'.join(test_id.split('.')[-2:])
        printd('\n{}...'.format(test_name))
        self.t0 = time.time()

        self.plots_open = self.pyplot.get_fignums()

    def tearDown(self):
        # Announce end of test with debug print
        self.t1 = time.time()
        dt = self.t1 - self.t0
        test_name = '.'.join(self.id().split('.')[-2:])
        printd('    {} done.'.format(test_name))
        printd('    {} took {:0.6f} s\n'.format(test_name, dt))

        # Automatically set window titles for new plots
        new_plots = [plot for plot in self.pyplot.get_fignums() if plot not in self.plots_open]
        for i, plot in enumerate(new_plots):
            self.pyplot.figure(plot).canvas.set_window_title('{} {}'.format('.'.join(self.id().split('.')[1:]), i))

    @classmethod
    def setUpClass(cls):
        # Set up reusable class instances
        cls.basic_tf = OMFITthomson(device=cls.device, shot=cls.shot, efitid=cls.efitid)
        cls.basic_tf()

    @classmethod
    def tearDownClass(cls):
        if cls.show_debug_plots:
            cls.pyplot.show()

    # Tests for OMFITthomson class methods
    def test_tf_init(self):
        tf = OMFITthomson(device=self.device, shot=self.shot, efitid=self.efitid)
        assert tf.shot == self.shot
        self.assertIsInstance(getattr(tf, 'device', None), str)
        self.assertIsInstance(getattr(tf, 'shot', None), int)

    def test_tf_shot_lookup(self):
        tf = OMFITthomson(device=self.device, shot=0, efitid=self.efitid)
        self.assertGreater(getattr(tf, 'shot', None), 0)

    def test_tf_main(self):
        tf = OMFITthomson(device=self.device, shot=self.shot, efitid=self.efitid)  # Needs to work on a fresh instance
        tf()
        self.assertIn('raw', tf)
        assert self.shot == tf['filtered']['shot']
        self.assertIn('temp', tf['filtered'][tf.subsystems[0]])

    @unittest.skipIf(not os.environ.get('DISPLAY', ''), "Can't test plots without a display")
    def test_tf_plots(self):
        import matplotlib
        import matplotlib.figure
        import matplotlib.axes

        fig, axs = self.basic_tf.profile_plot(2000)
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(axs[0], matplotlib.axes.Axes)
        figc, ax = self.basic_tf.contour_plot()
        assert isinstance(figc, matplotlib.figure.Figure)

    def test_to_dataset(self):
        from xarray import DataArray, Dataset

        data = self.basic_tf.to_dataset()
        d0 = data[list(data.keys())[0]]
        assert isinstance(d0, Dataset)

    def test_save_load(self):
        tf = copy.deepcopy(self.basic_tf)
        # This class doesn't have dedicated save and load methods, so we just have to make sure it can be pickled.
        pickle.dumps(tf)

    def test_select_time_window(self):
        params = ['temp', 'density']
        tw = self.basic_tf.select_time_window(self.time0, parameters=params)
        for param in params:
            assert param in list(tw.keys())
            for x in 'txye':
                assert x in list(tw[param].keys())


############################################
if __name__ == '__main__':
    test_classes_main_header()

    if len(sys.argv) > 1:
        try:
            test_flag = int(sys.argv[1])
        except ValueError:
            test_flag = int(sys.argv[1] == 'test')
    else:
        test_flag = 0

    if test_flag > 0:
        sys.argv.pop(1)
        unittest.main(failfast=False)
    else:
        OMFITthomson(shot=154754)  # Test init, but don't try to use shot 0 as it will try to connect to d3drdb
