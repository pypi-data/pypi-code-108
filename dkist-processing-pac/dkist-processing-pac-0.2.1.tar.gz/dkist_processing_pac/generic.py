import os
import pkg_resources
import yaml
import asdf
from configparser import ConfigParser
import numpy as np
try:
    from sunpy.coordinates import sun
except ImportError:
    raise ImportError('PAC Modules require sunpy>=1.0')
from dkist_processing_pac.data.required_params import elliptical
from dkist_processing_pac.tag import tag

#TODO: Rewrite based on Dave's new compute_telescope_geom to remove sunpy dependency
def compute_parallactic_angle(time):
    """ Calculate the parallactic angle of the Solar disk center at a specific time.

    All angles are in radians.

    Parameters
    ----------
    time : astropy.time.Time
        The absolute date/time at which to compute the parallactic angle

    Returns
    -------
    float
        The parallactic angle of disk center at the time specified [radians]

    """
    dkist_lat = 20.7047 * np.pi / 180
    dkist_long = -156.25 * np.pi / 180
    dec = sun.true_declination(time).value * np.pi / 180.
    ra = sun.true_rightascension(time).value * 15. * np.pi / 180.
    ha = time.sidereal_time('apparent', longitude=dkist_long * 180 / np.pi).value * 15 * np.pi / 180. - ra

    p = np.arctan2(np.sin(ha), np.tan(dkist_lat) * np.cos(dec) - np.sin(dec) * np.cos(ha))

    return p


#TODO: Update these defaults!
def gen_default_config(filename):
    """Generate an example fit configuration file with default options

    Parameters
    ----------
    filename : str
       Location to save example config file
    """
    config = ConfigParser(allow_no_value=True)

    config['Main'] = {'telescope_db': 'telescope_db.txt',
                      'method': 'differential_evolution'}

    with open(filename, 'w') as f:
        config.write(f)

    return

def init_fit_mode(fit_mode: str, wavelength: float, fit_TM: bool, init_set: str = 'default') -> dict:
    """Load a PA&C fit recipe from the database

    The recipe is returned as a ConfigParser object, which is basically a fancy dictionary

    Parameters
    ----------
    fit_mode : str
        Name of PA&C fit recipe

    Returns
    -------
    configparser.ConfigParser
        Object containing parameters, their ranges, and whether or not to vary them during a fit
    """
    mode_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/fit_modes/{}.yml'.format(fit_mode))
    if not os.path.exists(mode_file):
        raise FileNotFoundError("Could not find file for recipe '{}'".format(fit_mode))

    with open(mode_file, 'rb') as f:
        recipe = yaml.load(f, Loader=yaml.SafeLoader)
        print('{}: using PA&C fitting mode "{}"'.format(tag(), fit_mode))

    switches = recipe['switches']
    if not switches['fit_bounds']:
        print('{}: Boundless fit detected'.format(tag()))

    polcal_init_file = pkg_resources.resource_filename('dkist_processing_pac',
                                                       'data/init_values/polcal_{}.asdf'.format(init_set))
    if not os.path.exists(polcal_init_file):
        raise FileNotFoundError("Could not find the polcal init value file {}".format(polcal_init_file))
    with asdf.open(polcal_init_file, 'rb', lazy_load=False, copy_arrays=True) as f:
        polcal_init = f.tree
        print('{}: using initial values from set "{}"'.format(tag(), init_set))

    wave_idx = np.argmin(np.abs(polcal_init['wave'] - wavelength))

    mode_opts = {}
    for p in polcal_init['params'].keys():
        minv, val, maxv = polcal_init['params'][p][wave_idx, :]
        if 'dret' in p:
            vary = True
            if not switches['delta_d']:
                val = 0
                vary = False
        else:
            vary = recipe['vary'][p]

        if not switches['fit_bounds']:
            minv = -np.inf
            maxv = np.inf

        mode_opts[p] = {'min': minv,
                        'value': val,
                        'max': maxv,
                        'vary': vary}

    groupcal_init_file = pkg_resources.resource_filename('dkist_processing_pac',
                                                         'data/init_values/groupcal_{}.asdf'.format(init_set))
    if not os.path.exists(polcal_init_file):
        raise FileNotFoundError("Could not find the polcal init value file {}".format(polcal_init_file))
    with asdf.open(groupcal_init_file, 'rb', lazy_load=False, copy_arrays=True) as f:
        groupcal_init = f.tree

    wave_idx = np.argmin(np.abs(polcal_init['wave'] - wavelength))

    for p in groupcal_init['params'].keys():
        minv, val, maxv = groupcal_init['params'][p][wave_idx, :]
        if not switches['fit_bounds']:
            minv = -np.inf
            maxv = np.inf

        mode_opts[p] = {'min': minv,
                        'value': val,
                        'max': maxv,
                        'vary': fit_TM}

    mode_opts['switches'] = switches

    return mode_opts


def verify_fit_mode(mode_opts, fit_TM):
    """Make sure the loaded fit mode parameters are sufficient to actually run the fits

    All required model parameters need to exist and have an initial value.

    Parameters
    ----------
    mode_opts : configparser.ConfigParser
        Object containing fit parameter definitions. Each parameter in the model is a separate section with keywords
        'value', 'min', 'max', 'vary'.
    """

    missing_pars = []
    missing_vals = []
    bad_ranges = []
    for rp in elliptical['params']:
        if rp not in mode_opts.keys():
            missing_pars.append(rp)
        else:
            if rp != 'I_sys' and 'value' not in mode_opts[rp].keys():
                missing_vals.append(rp)
            if not mode_opts['switches']['fit_bounds'] \
                and (mode_opts[rp]['min'] != -np.inf or mode_opts[rp]['max'] != np.inf):
                bad_ranges.append(rp)

    if fit_TM:
        for p in ['x34', 't34', 'x56', 't56']:
            if p not in mode_opts.keys():
                missing_pars.append(p)
            else:
                if p != 'I_sys' and 'value' not in mode_opts[p].keys():
                    missing_vals.append(p)
                if not mode_opts['switches']['fit_bounds'] \
                    and (mode_opts[p]['min'] != -np.inf or mode_opts[p]['max'] != np.inf):
                    bad_ranges.append(p)

    if len(missing_pars) > 0:
        print('{}: ERROR: missing required fit parameters {}'.format(tag(), missing_pars))

    if len(missing_vals) > 0:
        print('{}: ERROR: missing initial values for parameters {}'.format(tag(), missing_vals))

    if len(bad_ranges) > 0:
        print('{}: ERROR: boundless fit requested, but the following parameters are bounded: {}'.format(tag(), bad_ranges))

    if len(missing_vals) > 0 or len(missing_pars) > 0 or len(bad_ranges) > 0:
        raise ValueError('Loaded fit parameters are not complete. See last status message(s) for info.')

def get_default_telescope_db():

    return pkg_resources.resource_filename('dkist_processing_pac', 'data/telescope_db.txt')